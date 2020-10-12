import numpy
from matchms import Spectrum
from matchms.filtering import harmonize_precursor_mz


def test_harmonize_precursor_mz():
    spectrum_in = Spectrum(mz=numpy.array([], dtype="float"),
                           intensities=numpy.array([], dtype="float"),
                           metadata={"pepmass": (445.0, 10.0)})

    spectrum = harmonize_precursor_mz(spectrum_in)

    assert spectrum.get("precursor_mz") == 445.0
