# ----------------------------------------------------------- class: SoxStats ------------------------------------------------------------ #

class SoxStats:

    # example properties
    # 
    #    length_seconds: float
    #    maximum_amplitude: float
    #    maximum_delta: float
    #    mean_amplitude: float
    #    mean_delta: float
    #    mean_norm: float
    #    midline_amplitude: float
    #    minimum_amplitude: float
    #    minimum_delta: float
    #    rms_amplitude: float
    #    rms_delta: float
    #    rough_frequency: int
    #    samples_read: int
    #    scaled_by: float
    #    volume_adjustment: float

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        resp_str: str
    ):
        self.length_seconds = None
        self.maximum_amplitude = None
        self.maximum_delta = None
        self.mean_amplitude = None
        self.mean_delta = None
        self.mean_norm = None
        self.midline_amplitude = None
        self.minimum_amplitude = None
        self.minimum_delta = None
        self.rms_amplitude = None
        self.rms_delta = None
        self.rough_frequency = None
        self.samples_read = None
        self.scaled_by = None
        self.volume_adjustment = None

        for line in resp_str.strip().split('\n'):
            comps = line.split(':')
            name = comps[0]
            val_str = comps[1].strip()

            while '  ' in name:
                name = name.replace('  ', ' ')

            name = '_'.join(name.strip().replace('(', '').replace(')', '').lower().split(' '))
            val = float(val_str) if '.' in val_str else int(val_str)

            setattr(self, name, val)


# ---------------------------------------------------------------------------------------------------------------------------------------- #