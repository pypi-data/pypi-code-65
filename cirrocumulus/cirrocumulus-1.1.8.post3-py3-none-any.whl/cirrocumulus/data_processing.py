import pandas as pd
import scipy.sparse

from cirrocumulus.dotplot_aggregator import DotPlotAggregator
from cirrocumulus.embedding_aggregator import EmbeddingAggregator, get_basis
from cirrocumulus.feature_aggregator import FeatureAggregator
from cirrocumulus.ids_aggregator import IdsAggregator
from cirrocumulus.unique_aggregator import UniqueAggregator


def apply_filter(df, data_filter):
    keep_expr = get_filter_expr(df, data_filter)
    return df[keep_expr] if keep_expr is not None else df


def get_filter_expr(df, data_filter):
    if df is None:
        raise ValueError('df is None')

    keep_expr = None
    if data_filter is not None:
        user_filters = data_filter.get('filters', [])
        combine_filters = data_filter.get('combine', 'and')
        for filter_obj in user_filters:
            field = filter_obj[0]
            op = filter_obj[1]
            value = filter_obj[2]
            if isinstance(field, dict):  # selection box

                selected_points_basis = get_basis(field['basis'], field.get('nbins'),
                    field.get('agg'), field.get('ndim', '2'), field.get('precomputed', False))

                if 'points' in value:
                    p = value['points']
                    field = selected_points_basis['full_name'] if selected_points_basis[
                                                                      'nbins'] is not None else 'index'
                    if field == 'index':
                        keep = df.index.isin(p)
                    else:
                        keep = df[field].isin(p)
                else:
                    keep = None
                    for p in value['path']:
                        if 'z' in p:  # 3d
                            selection_keep = \
                                (df[selected_points_basis['coordinate_columns'][0]] >= p['x']) & \
                                (df[selected_points_basis['coordinate_columns'][0]] <= p['x'] + p['width']) & \
                                (df[selected_points_basis['coordinate_columns'][1]] >= p['y']) & \
                                (df[selected_points_basis['coordinate_columns'][1]] <= p['y'] + p[
                                    'height']) & \
                                (df[selected_points_basis['coordinate_columns'][2]] >= p['z']) & \
                                (df[selected_points_basis['coordinate_columns'][2]] <= p['z'] + p['depth'])
                        else:
                            selection_keep = \
                                (df[selected_points_basis['coordinate_columns'][0]] >= p['x']) & \
                                (df[selected_points_basis['coordinate_columns'][0]] <= p['x'] + p['width']) & \
                                (df[selected_points_basis['coordinate_columns'][1]] >= p['y']) & \
                                (df[selected_points_basis['coordinate_columns'][1]] <= p['y'] + p['height'])

                    keep = selection_keep | keep if keep is not None else selection_keep

            else:
                series = df[field]
                if op == 'in':
                    keep = (series.isin(value)).values
                elif op == '>':
                    keep = (series > value)
                elif op == '=':
                    keep = (series == value)
                elif op == '<':
                    keep = (series < value)
                elif op == '!=':
                    keep = (series != value)
                elif op == '>=':
                    keep = (series >= value)
                elif op == '<=':
                    keep = (series <= value)
                else:
                    raise ValueError('Unknown filter')

            if scipy.sparse.issparse(keep):
                keep = keep.toarray().flatten()
            if hasattr(keep, 'sparse'):
                keep = keep.sparse.to_dense()
            if isinstance(keep, pd.Series):
                keep = keep.values
            if keep_expr is not None:
                if combine_filters == 'and':
                    keep_expr = keep_expr & keep
                else:
                    keep_expr = keep_expr | keep
            else:
                keep_expr = keep

    return keep_expr


def precomputed_summary(dataset_api, dataset, obs_measures, var_measures, dimensions):
    if '__count' in var_measures:
        var_measures.remove('__count')
    return dataset_api.read_precomputed_stats(dataset, obs_keys=dimensions + obs_measures, var_keys=var_measures)


def precomputed_grouped_stats(dataset_api, dataset, var_measures, dimensions):
    if (len(var_measures)) > 0 and len(dimensions) > 0:
        return dataset_api.read_precomputed_grouped_stats(dataset,
            var_keys=var_measures, obs_keys=dimensions)
    return []


def precomputed_embedding(dataset_api, dataset, basis, obs_measures, var_measures,
                          dimensions):
    if (len(obs_measures) + len(var_measures) + len(dimensions)) == 0:
        obs_measures = ['__count']
    return dataset_api.read_precomputed_basis(dataset, obs_keys=obs_measures + dimensions, var_keys=var_measures,
        basis=basis)


def get_var_name_type(key):
    index = key.find('/')
    if index == -1:
        return key, 'X'
    else:
        key_type = key[0:index]
        name = key[index + 1:]
        return name, key_type


def split_measures(measures):
    obs_measures = []
    var_measures = []
    for measure in measures:
        name, key_type = get_var_name_type(measure)
        if key_type == 'X':
            var_measures.append(name)
        elif key_type == 'obs':
            obs_measures.append(name)
        else:
            raise ValueError('Unknown key type: ' + key_type)
    return obs_measures, var_measures


def check_bin_input(nbins):
    if nbins is not None:
        nbins = int(nbins)
        nbins = min(1000, nbins)
        if nbins <= 0:
            nbins = None
    return nbins


def handle_export_dataset_filters(dataset_api, dataset, data_filters):
    import json

    reformatted_filters = []
    filter_names = []
    for data_filter_obj in data_filters:
        filter_value = json.loads(data_filter_obj['value'])
        filter_names.append(data_filter_obj['name'])
        reformatted_filters.append(filter_value)

    df_info = get_data(dataset_api, dataset, measures=['obs/index'], data_filters=reformatted_filters)
    result_df = pd.DataFrame(index=df_info['df']['index'])
    for i in range(len(reformatted_filters)):
        data_filter = reformatted_filters[i]
        filter_name = filter_names[i]
        df_filtered = apply_filter(df_info['df'], data_filter)
        df = pd.DataFrame(index=df_filtered['index'])
        df[filter_name] = True
        result_df = result_df.join(df, rsuffix='r')
    result_df.fillna(False, inplace=True)
    return result_df.to_csv()


# embedding - list of basis, measures, dimensions
def handle_data(dataset_api, dataset, embedding_list=None, grouped_stats=None, stats=None, selection=None):
    dimensions = set()
    measures = set()
    basis_list = []
    basis_keys = set()
    if embedding_list is not None:
        for embedding in embedding_list:
            dimensions.update(embedding.get('dimensions', []))
            embedding['count'] = '__count' in embedding.get('measures', [])
            measures.update(embedding.get('measures', []))
            nbins = check_bin_input(embedding.get('nbins', None))
            agg_function = embedding.get('agg', 'max')
            ndim = embedding.get('ndim', '2')
            precomputed = embedding.get('precomputed', False)
            basis = get_basis(embedding.get('basis'), nbins=nbins, agg=agg_function, dimensions=ndim,
                precomputed=precomputed)

            if basis['full_name'] not in basis_keys:
                basis_list.append(basis)
                basis_keys.add(basis['full_name'])

            embedding['basis'] = basis
    if selection is not None:
        data_filter = selection.get('filter')
        var_keys_filter, obs_keys_filter, selected_points_filter_basis_list = data_filter_keys(data_filter)
        selection['basis'] = selected_points_filter_basis_list
        measures.update(var_keys_filter)
        dimensions.update(obs_keys_filter)
        dimensions.update(selection.get('dimensions', []))
        measures.update(selection.get('measures', []))
        embeddings = selection.get('embeddings', [])
        embeddings_mapped = []
        for embedding in embeddings:
            basis = get_basis(embedding.get('basis'), nbins=embedding.get('nbins'), agg=embedding.get('agg', 'max'),
                dimensions=embedding.get('ndim', '2'),
                precomputed=embedding.get('precomputed', False))
            embeddings_mapped.append(basis)
        selection['embeddings'] = embeddings_mapped
        for basis_obj in selected_points_filter_basis_list + embeddings_mapped:
            if basis_obj['full_name'] not in basis_keys:
                basis_list.append(basis_obj)
                basis_keys.add(basis_obj['full_name'])

    if grouped_stats is not None:
        dimensions.update(grouped_stats.get('dimensions', []))
        measures.update(grouped_stats.get('measures', []))
    if stats is not None:
        dimensions.update(stats.get('dimensions', []))
        measures.update(stats.get('measures', []))

    has_count = '__count' in measures
    if has_count:
        measures.remove('__count')
    obs_measures, var_measures = split_measures(measures)
    df = dataset_api.read(dataset=dataset, obs_keys=list(dimensions) + obs_measures,
        var_keys=var_measures, basis=basis_list)
    if has_count:
        df['__count'] = 1
    results = {}
    if embedding_list is not None:
        results['embedding'] = []
        for embedding in embedding_list:
            dimensions = embedding.get('dimensions', [])
            measures = embedding.get('measures', [])
            obs_measures, var_measures = split_measures(measures)
            basis = embedding['basis']
            if basis['precomputed']:
                result = precomputed_embedding(dataset_api, dataset, basis, obs_measures, var_measures, dimensions)
            else:
                result = EmbeddingAggregator(obs_measures=obs_measures,
                    var_measures=var_measures,
                    dimensions=dimensions,
                    count=embedding['count'],
                    nbins=basis['nbins'],
                    basis=basis,
                    agg_function=basis['agg'],
                    quick=True).execute(df)
            results['embedding'].append(result)
    if grouped_stats is not None:
        if dataset_api.has_precomputed_stats(dataset):
            results['dotplot'] = precomputed_grouped_stats(dataset_api, dataset, grouped_stats.get('measures', []),
                grouped_stats.get('dimensions', []))
        else:
            results['dotplot'] = DotPlotAggregator(var_measures=grouped_stats.get('measures', []),
                dimensions=grouped_stats.get('dimensions', [])).execute(df)
    if stats is not None:
        dimensions = stats.get('dimensions', [])
        measures = stats.get('measures', [])
        obs_measures, var_measures = split_measures(measures)
        if dataset_api.has_precomputed_stats(dataset):
            result['summary'] = precomputed_summary(dataset_api, dataset, obs_measures, var_measures, dimensions)
        else:
            results['summary'] = FeatureAggregator(obs_measures, var_measures, dimensions).execute(df)
    if selection is not None:
        results['selection'] = {}
        dimensions = selection.get('dimensions', [])
        measures = selection.get('measures', [])
        obs_measures, var_measures = split_measures(measures)
        basis_list = selection.get('basis', [])
        embeddings = selection.get('embeddings', [])
        for basis_obj in basis_list + embeddings:
            if not basis_obj['precomputed'] and basis_obj['nbins'] is not None:
                EmbeddingAggregator.convert_coords_to_bin(df=df,
                    nbins=basis_obj['nbins'],
                    bin_name=basis_obj['full_name'],
                    coordinate_columns=basis_obj['coordinate_columns'])

        df = apply_filter(df, data_filter)
        if len(embeddings) > 0:
            results['selection']['coordinates'] = {}
            for embedding in embeddings:
                results['selection']['coordinates'][embedding['full_name']] = UniqueAggregator(
                    embedding['full_name'] if embedding['nbins'] is not None else 'index').execute(df)

        results['selection']['summary'] = FeatureAggregator(obs_measures, var_measures, dimensions).execute(df)
        if len(dimensions) > 0 and len(var_measures) > 0:
            results['selection']['dotplot'] = DotPlotAggregator(var_measures=var_measures,
                dimensions=dimensions).execute(df)
        results['selection']['count'] = df.shape[0]

    return results


def handle_selection_ids(dataset_api, dataset, data_filter):
    selection_info = get_selected_data(dataset_api, dataset, measures=['obs/index'], data_filter=data_filter)
    return {'ids': IdsAggregator().execute(selection_info['df'])}


def get_data(dataset_api, dataset, embeddings=[], measures=[], dimensions=[], data_filters=[]):
    obs_measures, var_measures = split_measures(measures)
    var_keys_filter = []
    obs_keys_filter = []
    selected_points_filter_basis_list = []
    for data_filter in data_filters:
        _var_keys_filter, _obs_keys_filter, selected_points_filter_basis_list = data_filter_keys(data_filter)
        selected_points_filter_basis_list += selected_points_filter_basis_list
        var_keys_filter += _var_keys_filter
        obs_keys_filter += _obs_keys_filter
    obs_keys = list(set(obs_measures + obs_keys_filter + dimensions))
    var_keys = list(set(var_measures + var_keys_filter))
    basis_objs = []
    basis_keys = set()
    for embedding in embeddings:
        basis_obj = get_basis(embedding['basis'], embedding.get('nbins'), embedding.get('agg'),
            embedding.get('ndim', '2'), embedding.get('precomputed', False))
        if basis_obj['full_name'] not in basis_keys:
            basis_objs.append(basis_obj)
            basis_keys.add(basis_obj['full_name'])
    for basis_obj in selected_points_filter_basis_list:
        if basis_obj['full_name'] not in basis_keys:
            basis_objs.append(basis_obj)
            basis_keys.add(basis_obj['full_name'])
    df = dataset_api.read(dataset=dataset, obs_keys=obs_keys, var_keys=var_keys, basis=basis_objs)
    for basis_obj in basis_objs:
        if not basis_obj['precomputed'] and basis_obj['nbins'] is not None:
            EmbeddingAggregator.convert_coords_to_bin(df=df,
                nbins=basis_obj['nbins'],
                bin_name=basis_obj['full_name'],
                coordinate_columns=basis_obj['coordinate_columns'])
    return {'df': df, 'basis': basis_objs, 'obs_measures': obs_measures, 'var_measures': var_measures,
            'dimensions': dimensions}


def get_selected_data(dataset_api, dataset, embeddings=[], measures=[], dimensions=[], data_filter=None):
    df_info = get_data(dataset_api, dataset, embeddings, measures, dimensions,
        [data_filter] if data_filter is not None else [])
    df = apply_filter(df_info['df'], data_filter)
    df_info['df'] = df
    return df_info


def data_filter_keys(data_filter):
    var_keys = set()
    obs_keys = set()
    basis_list = []
    if data_filter is not None:
        user_filters = data_filter.get('filters', [])

        for i in range(len(user_filters)):
            user_filter = user_filters[i]
            key = user_filter[0]
            if isinstance(key, dict):
                basis = get_basis(key['basis'], key.get('nbins'), key.get('agg'),
                    key.get('ndim', '2'), key.get('precomputed', False))
                basis_list.append(basis)
            else:
                name, key_type = get_var_name_type(key)
                user_filter[0] = name
                if key_type == 'X':
                    var_keys.add(name)
                else:
                    obs_keys.add(name)
    return list(var_keys), list(obs_keys), basis_list
