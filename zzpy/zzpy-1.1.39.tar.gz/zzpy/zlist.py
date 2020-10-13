def groupby_items(items, field):
    groupby_result = {}
    for it in items:
        k = it.get(field)
        groupby_result[k] = groupby_result.get(k, []) + [it]
    return groupby_result
