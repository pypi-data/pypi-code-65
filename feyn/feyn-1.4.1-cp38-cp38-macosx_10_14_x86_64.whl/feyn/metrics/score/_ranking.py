from numpy import array
from ._mutual import calculate_mi

def feature_importance(target_df, out_name, **kwargs):
    """
    out_name is the name of the output column.

    All columns except the output are assumed to be
    input featuers.
    """
    ret = []
    y = target_df[out_name]

    for c in target_df.drop(out_name, axis=1).columns:
        x = target_df[c]

        mi_score = calculate_mi([x], y, **kwargs)
        ret.append(mi_score)

    return array(ret)
