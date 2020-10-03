import pandas as pd


def str_to_timedelta(t):
    """Convert a Slurm elapsed time string to a pandas Timedelta

    Slurm formats time as days-HH:MM:SS OR HH:MM:SS
    """
    if '-' in t:
        dd, hhmmss = t.split('-')
        hh, mm, ss = (int(i) for i in hhmmss.split(':'))
        return pd.Timedelta(days=int(dd), hours=hh, minutes=mm, seconds=ss)
    else:
        hh, mm, ss = (int(i) for i in t.split(':'))
        return pd.Timedelta(hours=hh, minutes=mm, seconds=ss)
