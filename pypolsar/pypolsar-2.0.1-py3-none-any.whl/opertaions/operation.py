import numpy as np

from ..filters.spatial import multilook


def coherence(in1, in2, window_size=7, *args, **kwargs):
    """[summary]

    Calc coherence between two complex arrays

    Parameters
    ----------
    in1 : [type]
        [description]
    in2 : [type]
        [description]
    window_size : int, optional
        [description], by default 7
    """
    coh = multilook(in1 * np.conj(in2), window_size, *args, **kwargs) / (
        np.sqrt(
            multilook(in1 * np.conj(in1), window_size, *args, **kwargs)
            * multilook(in2 * np.conj(in2, window_size, *args, **kwargs))
        )
    )

    return np.clip(np.nan_to_num(coh), 0.0, 1.0)
