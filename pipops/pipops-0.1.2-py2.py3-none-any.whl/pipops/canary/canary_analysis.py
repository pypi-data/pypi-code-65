from scipy.stats import kruskal, chi2
import numpy as np


class CanaryAnalysis():
    def analyze_canary(tollerance, *args, **kwargs):
        args = list(map(np.asarray, args))
        num_groups = len(args)
        if num_groups < 2:
            raise ValueError('Need at least two groups in pipops.canary()')
        if tollerance == 0:
            raise ValueError(
                "Tollerance value can't be zero, it must be in the range of 1 to 100")
        for arg in args:
            if arg.size == 0:
                return (
                    np.nan, np.nan)
        records_len = np.asarray(list(map(len, args)))
        stat, p = kruskal(*args)
        alpha = ((tollerance) / 100)
        degree_of_freedom = num_groups - 1
        chi_critical_value = chi2.isf(q=alpha, df=degree_of_freedom)

        if stat == 0:
            result = True
        elif stat >= chi_critical_value:
            result = True
        else:
            result = False
        return result
