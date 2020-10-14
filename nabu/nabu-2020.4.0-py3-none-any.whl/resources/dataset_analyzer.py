import os
import numpy as np
from silx.io.url import DataUrl
from tomoscan.esrf.edfscan import EDFTomoScan
from tomoscan.esrf.hdf5scan import HDF5TomoScan
from ..thirdparty.tomwer_load_flats_darks import get_flats_frm_process_file, get_darks_frm_process_file
from .nxflatfield import NXFlatField
from .utils import is_hdf5_extension

dataset_infos = {
    "num_radios": None,
    "num_darks": None,
    "num_flats": None,
    "radios": None,
    "darks": None,
    "flats": None,
    "frame_dims": None,
    "energy_kev": None,
    "distance_m": None,
    "pixel_size_microns": None,
}


class DatasetAnalyzer(object):
    """
    Base class for datasets analyzers.
    """
    def __init__(self, location, processes_file=None, extra_options=None):
        """
        Initialize a Dataset analyzer.

        Parameters
        ----------
        location: str
            Dataset location (directory or file name)
        processes_file: str, optional
            Processes file providing supplementary information (ex. pre-processed data)
        extra_options: dict, optional
            Extra options on how to interpret the dataset.
            Available options are the following:
              - force_flatfield
        """
        self.location = location
        self.processes_file = processes_file
        self._set_extra_options(extra_options)


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        advanced_options = {
            "force_flatfield": False,
        }
        advanced_options.update(extra_options)
        self.extra_options = advanced_options


    def _init_dataset_scan(self, filetype, **kwargs):
        scanners = {
            "edf": EDFTomoScan,
            "hdf5": HDF5TomoScan,
        }
        if filetype not in scanners.keys():
            raise ValueError("No scanner for file type: %s" % filetype)
        scanner = scanners[filetype]
        self.dataset_scanner = scanner(self.location, **kwargs)
        self.projections = self.dataset_scanner.projections
        self.flats = self.dataset_scanner.flats
        self.darks = self.dataset_scanner.darks
        self.n_angles = self.dataset_scanner.tomo_n
        self.radio_dims = (self.dataset_scanner.dim_1, self.dataset_scanner.dim_2)
        self._binning = (1, 1)
        self.translations = None
        self.axis_position = None
        self._radio_dims_notbinned = self.radio_dims

    @property
    def energy(self):
        """
        Return the energy in kev.
        """
        return self.dataset_scanner.energy

    @property
    def distance(self):
        """
        Return the sample-detector distance in meters.
        """
        return abs(self.dataset_scanner.distance)

    @property
    def pixel_size(self):
        """
        Return the pixel size in microns.
        """
        return self.dataset_scanner.pixel_size * 1e6 # TODO X and Y pixel size

    @property
    def binning(self):
        """
        Return the binning in (x, y)
        """
        return self._binning

    @property
    def rotation_angles(self):
        """
        Return the rotation angles in radians.
        """
        return self._get_rotation_angles()


    def remove_unused_radios(self):
        """
        Remove "unused" radios.
        This is used for legacy ESRF scans.
        """
        # This should only be used with EDF datasets
        if self.dataset_scanner.type != "edf":
            return
        # Extraneous projections are assumed to be on the end
        projs_indices = sorted(self.projections.keys())
        used_radios_range = range(projs_indices[0], self.n_angles)
        radios_not_used = []
        for idx in self.projections.keys():
            if idx not in used_radios_range:
                radios_not_used.append(idx)
        for idx in radios_not_used:
            self.projections.pop(idx)
        return radios_not_used


class EDFDatasetAnalyzer(DatasetAnalyzer):
    """
    EDF Dataset analyzer for legacy ESRF acquisitions
    """
    def __init__(self, location, n_frames=1, processes_file=None, extra_options=None):
        """
        EDF Dataset analyzer.

        Parameters
        -----------
        location: str
            Location of the folder containing EDF files
        """
        super().__init__(location, processes_file=processes_file, extra_options=extra_options)
        if not(os.path.isdir(location)):
            raise ValueError("%s is not a directory" % location)
        self._init_dataset_scan("edf", n_frames=n_frames)

    def _get_rotation_angles(self):
        # Not available in EDF dataset
        return None


class HDF5DatasetAnalyzer(DatasetAnalyzer):
    """
    HDF5 dataset analyzer
    """
    def __init__(self, location, processes_file=None, extra_options=None):
        """
        HDF5 Dataset analyzer.

        Parameters
        -----------
        location: str
            Location of the HDF5 master file
        """
        super().__init__(location, processes_file=processes_file, extra_options=extra_options)
        if not(os.path.isfile(location)):
            raise ValueError("%s is not a file" % location)
        self._init_dataset_scan("hdf5")
        self._get_flats_darks()
        self._rot_angles = None


    def _get_flats_darks(self):
        if len(self.flats) == 0 and not(self.extra_options["force_flatfield"]):
            # No flats at all in the dataset. Do nothing.
            return
        if self.processes_file is None and self._load_flats_from_tomwer():
            # Loaded from tomwer_processes.h5
            return
        # Otherwise load or compute flats/darks with nabu
        self._compute_or_load_flats()


    def _load_flats_from_tomwer(self, tomwer_processes_fname=None):
        tomwer_processes_fname = tomwer_processes_fname or "tomwer_processes.h5"
        tomwer_processes_file = os.path.join(self.dataset_scanner.path, "tomwer_processes.h5")
        if not(os.path.isfile(tomwer_processes_file)):
            return False
        print("Loading darks and refs from %s" % tomwer_processes_file)
        new_flats = get_flats_frm_process_file(
            tomwer_processes_file, self.dataset_scanner.entry
        )
        new_darks = get_darks_frm_process_file(
            tomwer_processes_file, self.dataset_scanner.entry
        )
        self.flats = new_flats
        self.darks = new_darks
        return True


    def _compute_or_load_flats(self):
        processes_file = self.processes_file
        if processes_file is None:
            processes_file = os.path.join(self.dataset_scanner.path, "nabu_processes.h5")
        # By default, write in processes_file. Not sure it is a good idea
        results_file = processes_file
        # Don't write in processes_file if flatfield = forced
        if self.extra_options["force_flatfield"]:
            results_file = None
        lookup_files = [
            DataUrl(
                file_path=processes_file,
                data_path=os.path.join(self.dataset_scanner.entry, "flat_field_images")
            )
        ]
        self._nxflatfield = NXFlatField(
            self._get_dataset_hdf5_url(),
            self.dataset_scanner.image_key,
            lookup_files=lookup_files,
            results_file=results_file,
            force_load_existing_results=self.extra_options["force_flatfield"],
            flats_reduction="median",
            darks_reduction="mean"
        )
        res = self._nxflatfield.get_final_urls()
        self.flats = res["flats"]
        self.darks = res["darks"]


    def _get_rotation_angles(self):
        if self._rot_angles is None:
            angles = np.array(self.dataset_scanner.rotation_angle)
            projs_idx = np.array(list(self.projections.keys()))
            angles = angles[projs_idx]
            self._rot_angles = np.deg2rad(angles)
        return self._rot_angles


    def _get_dataset_hdf5_url(self):
        first_proj_idx = sorted(self.projections.keys())[0]
        first_proj_url = self.projections[first_proj_idx]
        return DataUrl(
            file_path=first_proj_url.file_path(),
            data_path=first_proj_url.data_path(),
            data_slice=None
        )


    @property
    def dataset_hdf5_url(self):
        return self._get_dataset_hdf5_url()


def analyze_dataset(dataset_path, processes_file=None, extra_options=None):
    if not(os.path.isdir(dataset_path)):
        if not(os.path.isfile(dataset_path)):
            raise ValueError("Error: %s no such file or directory" % dataset_path)
        if not(is_hdf5_extension(os.path.splitext(dataset_path)[-1].replace(".", ""))):
            raise ValueError("Error: expected a HDF5 file")
        dataset_analyzer_class = HDF5DatasetAnalyzer
    else: # directory -> assuming EDF
        dataset_analyzer_class = EDFDatasetAnalyzer
    dataset_structure = dataset_analyzer_class(
        dataset_path, processes_file=processes_file, extra_options=extra_options
    )
    return dataset_structure

