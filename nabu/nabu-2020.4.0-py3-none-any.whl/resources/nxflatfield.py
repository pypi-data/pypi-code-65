import os
from tempfile import mkdtemp
import numpy as np
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
from tomoscan.esrf.hdf5scan import ImageKey
from ..utils import check_supported
from ..io.writer import NXProcessWriter
from ..io.utils import get_first_hdf5_entry, hdf5_entry_exists
from .logger import LoggerOrPrint

val_to_nxkey = {
    "flats": ImageKey.FLAT_FIELD.value,
    "darks": ImageKey.DARK_FIELD.value,
    "projections": ImageKey.PROJECTION.value,
}


def _extract_entry(data_path):
    return data_path.lstrip("/").split("/")[0]

def replace_h5_entry(data_url, new_entry):
    split_path = data_url.data_path().lstrip("/").split("/")
    split_path[0] = new_entry
    new_data_path = "/".join(split_path)
    return DataUrl(
        file_path=data_url.file_path(),
        data_path=new_data_path,
        data_slice=data_url.data_slice(),
        scheme=data_url.scheme
    )



class NXFlatField:
    """
    A helper class to load flats and darks, or to compute the final ones.

    At ESRF, several darks/flats series are acquired during a scan.
    Each series undergoes a reduction (mean, median, ...) to get a "final" image.
    For example, there is one series of flats in the beginning, and one in the end ;
    thus there are two corresponding "final" flats.
    """

    def __init__(
        self, data_url, image_keys, lookup_files=None, results_file=None,
        dont_write_results=False, force_load_existing_results=False, logger=None,
        flats_reduction="mean", darks_reduction="mean",
    ):
        """
        Initialize a FlatFieldLoader helper.

        Parameters
        -----------
        data_url: silx.io.url.DataUrl
            A DataUrl object containing the URL to the volume data.
        image_keys: list of int
            List of keys corresponding to each image of the data volume.
            See Nexus Format specification, NXtomo, "image_key".
        lookup_files: list of DataUrl, optional
            List of paths (DataUrl) to inspect to load existing "final" flats/darks.
            If something is found one of these URL, the data will be loaded from there.
        results_file: str, optional
            File path where to write the results.
            Mind the difference with `lookup_files`: this parameter is for writing.
            If the file already exists, its data will be overwritten !
            If nothing is provided, a temporary file is created, except if the option
            'dont_write_results' is set to True.
        dont_write_results: bool, optional
            Whether to disable writing results to a file. If set to True, nothing will
            be written (neither to results_file nor temporary file).
            Default is False.
        force_load_existing_results: bool, optional
            Whether to force loading existing results, regardless of the input data
            and results file.
            If set to True, the parameter 'lookup_files' must contain exactly one
            (valid) DataUrl of the results to load.
            Default is False.
        logger: Logger object, optional
            Logging object
        flats_reduction: str, optional
            Reduction function to use for flats. Can be "mean", "median" or "sum".
            Default is "mean".
        darks_reduction: str, optional
            Reduction function to use for darks. Can be "mean", "median" or "sum".
            Default is "mean".

        Warning
        -------
        Make sure to use DataUrl objects for the 'lookup_files' and 'results_file'
        parameters.
        """
        self.data_url = data_url
        self.image_keys = image_keys
        self.lookup_files = lookup_files or []
        self.results_file = results_file
        self.dont_write_results = dont_write_results
        self.force_load_existing_results = force_load_existing_results
        self.logger = LoggerOrPrint(logger)
        self.reduction_function = {}
        self._set_reduction_method("flats", flats_reduction)
        self._set_reduction_method("darks", darks_reduction)
        self._get_data_shape()
        self._discover_existing_results()


    def _set_reduction_method(self, what, reduction_method):
        check_supported(what, val_to_nxkey.keys(), "image type")
        red_methods = {
            "mean": np.mean,
            "median": np.median,
            "sum": np.sum
        }
        check_supported(reduction_method, red_methods, "reduction method")
        self.reduction_function[what] = red_methods[reduction_method]


    def _get_data_shape(self):
        with HDF5File(self.data_url.file_path(), "r") as fid:
            shp = fid[self.data_url.data_path()].shape
        self.data_shape = shp


    def _discover_existing_results(self):
        self._existing_results = None
        if self.lookup_files == []:
            return
        for data_url in self.lookup_files:
            if self.force_load_existing_results or self.is_valid_results_file(data_url):
                self._existing_results = self._get_existing_results_url(data_url)
                self.logger.info("Loaded flats/darks from %s" % data_url.file_path())
                break
        if self._existing_results is None:
            self.logger.debug("Flats/darks could not be loaded from any file")


    def get_config(self):
        return {
            "input_file": self.data_url.path(),
            "lookup_files": [url.path() for url in self.lookup_files],
            "results_file": self.results_file or "None",
            "flats_reduction_method": self.reduction_function["flats"].__name__,
            "darks_reduction_method": self.reduction_function["darks"].__name__,
            "image_key": self.image_keys,
            "data_shape": self.data_shape,
        }


    def _is_same_configuration(self, cfg, ignore_filenames=False):
        my_config = self.get_config()
        res = True
        try:
            for key in ["flats_reduction_method", "darks_reduction_method"]:
                res &= (my_config[key] == bytes.decode(cfg[key][()]))
            res &= np.allclose(my_config["data_shape"], cfg["data_shape"][()])
            res &= np.allclose(my_config["image_key"], cfg["image_key"][()])

            du1 = DataUrl(path=my_config["input_file"])
            du2 = DataUrl(path=bytes.decode(cfg["input_file"][()]))
            if not(ignore_filenames):
                res &= (
                    os.path.basename(du1.file_path()) == os.path.basename(du2.file_path())
                )
            res &= (du1.data_path() == du2.data_path())
        except KeyError:
            res = False
        return res


    def is_valid_results_file(self, data_url):
        if not(os.path.isfile(data_url.file_path())):
            return False
        cfg_path = os.path.join(data_url.data_path(), "configuration")
        with HDF5File(data_url.file_path(), "r") as fid:
            try:
                cfg = fid[cfg_path]
            except KeyError:
                return False
            is_same_cfg = self._is_same_configuration(cfg)
            if not(is_same_cfg):
                self.logger.warning("Incompatible results file: %s" % data_url.file_path())
        return is_same_cfg


    def _get_existing_results_url(self, data_url):
        res = {"flats": {}, "darks": {}}
        # If entry is incorrect, take first entry
        # TODO find a more elegant mechanism
        fname = data_url.file_path()
        entry = _extract_entry(data_url.data_path())
        if not(hdf5_entry_exists(fname, entry)):
            new_entry = get_first_hdf5_entry(fname)
            data_url = replace_h5_entry(data_url, new_entry)
            self.logger.warning(
                "Entry %s in file %s does not exist. Using the first entry %s"
                % (entry, fname, new_entry)
            )
        #
        results_path = os.path.join(data_url.data_path(), "results") # NXProcess
        with HDF5File(data_url.file_path(), "r") as fid:
            for what in res.keys():
                for img_id in fid[results_path][what].keys():
                    res[what][int(img_id)] = DataUrl(
                        file_path=data_url.file_path(),
                        data_path=os.path.join(results_path, what, img_id)
                    )
        return res


    @staticmethod
    def load_data(ff_results):
        res_arrays = {"flats": {}, "darks": {}}
        for what in res_arrays.keys():
            for img_id, data_url in ff_results[what].items():
                with HDF5File(data_url.file_path(), "r") as fid:
                    res_arrays[what][img_id] = fid[data_url.data_path()][()]
        return res_arrays


    @staticmethod
    def get_data_slices(image_keys, key, dummy_value=-100):
        """
        Return indices in the data volume where images correspond to a certain key.

        Parameters
        ----------
        image_keys: list of int
            List of keys corresponding to each image of the data volume.
            See Nexus Format specification, NXtomo, "image_key".
        key: int
            Key to search in the `image_keys` list.

        Returns
        --------
        slices: list of slice
            A list where each item is a slice.
        """
        image_keys = np.hstack([[dummy_value], image_keys])
        jump_indices = np.where(np.diff(image_keys == key) != 0)[0]
        n_jumps = jump_indices.size
        if (n_jumps % 2):
            if image_keys[-1] == key:
                jump_indices = jump_indices.tolist() +  [None]
            else:
                raise ValueError("Something wrong with image_keys")
        slices = []
        for i in range(0, n_jumps, 2):
            slices.append(slice(jump_indices[i], jump_indices[i+1]))
        return slices


    def get_data_chunk(self, data_slice):
        """
        Get a data chunk from the data volume whose path was specified at class instantiation.
        """
        with HDF5File(self.data_url.file_path(), "r", swmr=True) as f:
            data_raw = f[self.data_url.data_path()][data_slice]
        return data_raw


    def write_results(self, flats_and_darks, entry=None, process_name="flat_field_images", tmp_fallback=True):
        """
        Write the results in a HDF5 file.

        Parameters
        -----------
        flats_and_darks: dict
            Dictionary of dictionaries, in the form

            >>> {
            ...     "darks": { 0: reduced_flat_0, 1000: reduced_flat_1000},
            ...     "flats": { 1: reduced_dark_0},
            ... }

            where each reduced_array is a numpy array.

        entry: str, optional
            HDF5 entry name. If not provided, the same entry as input dataset is taken.
        process_name: str, optional
            Process name. Default is "flat_field_images".
        tmp_fallback: bool, optional
            Whether to write to /tmp if writing fails. Default is True.
        """
        if entry is None:
            entry = [x for x in self.data_url.data_path().split("/") if len(x) > 0][0]
        results_file = self.results_file
        if results_file is None and not(tmp_fallback):
            raise ValueError("Please provide results_file and/or dont_write_results=False")
        def is_writeable(fname):
            if fname is None:
                return False
            target_dir = os.path.dirname(results_file)
            return os.access(target_dir, os.W_OK)
        if is_writeable(results_file):
            target_dir = os.path.dirname(results_file)
        else:
            tempdir = mkdtemp(prefix="nabu_flatfield_")
            if results_file is None:
                msg = "Results file not provided. "
            else:
                msg = "Cannot write to %s - " % (os.path.dirname(results_file))
            self.logger.warning(
                msg + "Using temporary directory %s instead" % tempdir
            )
            target_dir = tempdir
            results_file = "nabu_processes.h5"

        results_file = os.path.join(target_dir, os.path.basename(results_file))
        writer = NXProcessWriter(results_file, entry=entry, overwrite=True)
        h5_results_path = writer.write(
            flats_and_darks, process_name, config=self.get_config()
        )
        self.logger.debug("Wrote final flats and darks to %s" % results_file)
        links = {}
        for img_type, imgs in flats_and_darks.items():
            links[img_type] = {}
            for img_idx in imgs.keys():
                links[img_type][img_idx] = DataUrl(
                    file_path=results_file,
                    data_path=os.path.join(h5_results_path, img_type, str(img_idx))
                )
        return links


    def compute_final_images(self):
        self.logger.info(
            "Computing final flats/darks for %s" % self.data_url.file_path()
        )
        res = {"flats": {}, "darks": {}}
        for what in res.keys():
            img_slices = self.get_data_slices(self.image_keys, val_to_nxkey[what])
            if img_slices == []:
                self.logger.error("No %s found in %s" % (what, self.data_url.file_path()))
                res[what] = None
            for data_slice in img_slices:
                data_chunk = self.get_data_chunk(data_slice)
                img = self.reduction_function[what](data_chunk, axis=0)
                res[what][int(data_slice.start)] = img
        return res


    def get_final_urls(self):
        if self._existing_results is not None:
            return self._existing_results
        else:
            flats_and_darks = self.compute_final_images()
            return self.write_results(flats_and_darks)
