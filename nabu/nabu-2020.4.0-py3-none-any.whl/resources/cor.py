import numpy as np
from silx.io import get_data
from ..preproc.ccd import FlatField
from ..preproc.alignment import CenterOfRotation, CenterOfRotationAdaptiveSearch

class CORFinder:
    """
    An application-type class for finding the Center Of Rotation (COR).
    """
    def __init__(self, dataset_info, angles=None, halftomo=False, do_flatfield=True):
        """
        Initialize a CORFinder object.

        Parameters
        ----------
        dataset_info: `nabu.resources.dataset_analyzer.DatasetAnalyzer`
            Dataset information structure
        angles: array, optional
            Information on rotation angles. If provided, it overwrites
            the rotation angles available in `dataset_info`, if any.
        halftomo: bool, optional
            Whether the scan was performed in "half tomography" acquisition.
        """
        self.halftomo = halftomo
        self.dataset_info = dataset_info
        self.do_flatfield = do_flatfield
        self.shape = dataset_info._radio_dims_notbinned[::-1]
        self._get_angles(angles)
        self._init_radios()
        self._init_flatfield()
        self._apply_flatfield()
        self.cor = CenterOfRotation()
        self._default_search_method = "centered"
        if self.halftomo:
            self._default_search_method = "global"
            self.cor = CenterOfRotationAdaptiveSearch()

    def _get_angles(self, angles):
        dataset_angles = self.dataset_info.rotation_angles
        if dataset_angles is None:
            if angles is None: # should not happen with hdf5
                theta_min = 0
                theta_max = np.pi
                msg = "Warning: no information on angles was found for this dataset. Using default range "
                endpoint = False
                if self.halftomo:
                    theta_max *= 2
                    endpoint = True
                    msg += "[0, 360]"
                else:
                    msg += "[0, 180["
                print(msg)
                angles = np.linspace(
                    theta_min, theta_max, len(self.dataset_info.projections),
                    endpoint=endpoint
                )
            dataset_angles = angles
        self.angles = dataset_angles


    def _init_radios(self):
        # We take 2 radios. It could be tuned for a 360 degrees scan.
        self._n_radios = 2
        self._radios_indices = []
        radios_indices = sorted(self.dataset_info.projections.keys())

        # Take angles 0 and 180 degrees. It might not work of there is an offset
        i_0 = np.argmin(np.abs(self.angles))
        i_180 = np.argmin(np.abs(self.angles - np.pi))
        _min_indices = [i_0, i_180]
        self._radios_indices = [
            radios_indices[i_0],
            radios_indices[i_180]
        ]
        self.radios = np.zeros((self._n_radios, ) + self.shape, "f")
        for i in range(self._n_radios):
            radio_idx = self._radios_indices[i]
            self.radios[i] = get_data(self.dataset_info.projections[radio_idx]).astype("f")


    def _init_flatfield(self):
        if not(self.do_flatfield):
            return
        self.flatfield = FlatField(
            self.radios.shape,
            flats=self.dataset_info.flats,
            darks=self.dataset_info.darks,
            radios_indices=self._radios_indices,
            interpolation="linear",
            convert_float=True
        )


    def _apply_flatfield(self):
        if not(self.do_flatfield):
            return
        self.flatfield.normalize_radios(self.radios)


    def find_cor(self, search_method=None, **cor_kwargs):
        """
        Find the center of rotation.

        Parameters
        ----------
        search_method: str, optional
            Which CoR search method to use. Default is "auto" (equivalent to "centered").

        Returns
        -------
        cor: float
            The estimated center of rotation for the current dataset.

        Notes
        ------
        This function passes the named parameters to nabu.preproc.alignment.CenterOfRotation.find_shift.
        """
        search_method = search_method or self._default_search_method
        if search_method == "global":
            shift = self.cor.find_shift(
                self.radios[0],
                np.fliplr(self.radios[1]),
                low_pass=1, high_pass=20
            )
        else:
            shift = self.cor.find_shift(
                self.radios[0],
                np.fliplr(self.radios[1]),
                **cor_kwargs
            )
        # find_shift returned a single scalar in 2020.1
        # This should be the default after 2020.2 release
        if hasattr(shift, "__iter__"):
            shift = shift[0]
        #
        return self.shape[1]/2 + shift

