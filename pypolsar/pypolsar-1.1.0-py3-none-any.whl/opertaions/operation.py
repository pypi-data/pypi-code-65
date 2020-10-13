Coherence


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
    coh = multilook(in1 * np.conj(in2), window_size=3, *args, **kwargs) 
                / np.sqrt( multilook(in1*np.conj(in1), window_size=3, *args, **kwargs) 
                * multilook( in2 * np.conj(in2, window_size=3, *args, **kwargs) ) )
"""        
coh = np.abs(smooth(array[0] * np.conj(array[1]), self.win)
                     / np.sqrt(smooth(array[0] * np.conj(array[0]), self.win)
                               * smooth(array[1] * np.conj(array[1]), self.win)))
"""
    return np.clip(np.nan_to_num(coh), 0.0, 1.0)
