from scipy.stats import mannwhitneyu
import numpy as np


class CanaryAnalysis():
    def analyze_canary(tollerance, *args, **kwargs):
        args = list(map(np.asarray, args))
        num_groups = len(args)
        if num_groups < 2:
            result = None
            delta = None
            description = "Atleast two groups needed for comparision"
            return result, delta, description
        if tollerance == 0:
            result = None
            delta = None
            description = "Tollerance value can't be zero, it must be in the range of 1 to 100"
            return result, delta, description
        if num_groups > 2:
            result = None
            delta = None
            description = "More than two groups comparition is not permitted"
            return result, delta, description
        for arg in args:
            if arg.size == 0:
                return (np.nan, np.nan)
        records_len = np.asarray(list(map(len, args)))
        _, p_value = mannwhitneyu(*args)
        alpha = (tollerance / 100)
        variance = 1 - p_value
        delta = round(variance * 100)
        if (variance <= alpha):
            result = True
            description = "Canary is allowed"
        else:
            result = False
            description = "Canary is not allowed, Rollback !"
        return result, delta, description
