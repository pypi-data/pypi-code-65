import pandas as pd
from typing import Iterable
import functools

pd_merge = pd.merge


@functools.wraps(pd_merge)
def captivity_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: Iterable[str],
    suffixes=None,
    *args,
    **kwargs,
):
    """

    Wraps pd.merge, preventing:
    * joins where non-join columns have duplicate names (except when suffixes are explicitly passed)

    :param left:
    :param right:
    :param on:
    :param args:
    :param kwargs:
    :return:
    """
    if suffixes is None:
        from captivity import flag_issue

        problematic_columns = (
            set(left.columns).intersection(set(right.columns)).difference(on)
        )
        if len(problematic_columns) > 0:
            flag_issue(
                f"Merging dataframes with overlapping column names that are not in the on parameter is a bad idea. Problematic columns: {problematic_columns}"
            )

        suffixes = ("_x", "_y")
    return pd_merge(left=left, right=right, on=on, suffixes=suffixes, *args, **kwargs)


pd.DataFrame.merge = captivity_merge
pd.merge = captivity_merge
