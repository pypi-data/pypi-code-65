#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-Python.
# @File         : Features
# @Time         : 2019-07-26 10:04
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : featuretools

import featuretools
import featuretools as ft
import featuretools.variable_types as vt
from featuretools.selection import remove_low_information_features, remove_single_value_features

from tqdm.auto import tqdm
from tql.pipe import reduce_mem_usage, cprint
from tql.ml.automl.primitives import *


# todo： 增加时间特征
class AutoFeat(object):
    vt = vt

    def __init__(self, df, base_entity_id, target_entity_id, type2features, index=None, time_index=None,
                 secondary_time_index=None):
        self.entity_id = base_entity_id  # 表名
        self.type2features = self._convert_type(type2features)
        self.index = '__id' if index is None else index
        self.target_entity_id = target_entity_id  # self.index != '__id' => self.target_entity_id = self.entity_id

        self.es = ft.EntitySet(id='MAIN')
        self.es.entity_from_dataframe(
            entity_id=self.entity_id,
            dataframe=df.copy(),
            index=self.index,
            variable_types=self.variable_types,
            time_index=time_index,
            secondary_time_index=secondary_time_index
        )

        self._create_es()

    def _create_es(self):
        """overwrite"""
        for col in tqdm(self.normalize_entity_cols, desc='Normalize Entity'):
            self.es.normalize_entity(self.entity_id, col, col)

    def run_dfs(self, max_depth=1, features_only=True, chunk_size=None, n_jobs=1, ignore_variables=None,
                reduce_mem=False, trans_primitives=None, agg_primitives=None, **kwargs):
        """Deep Feature Synthesisf
        agg_primitives (list[str or AggregationPrimitive], optional): List of Aggregation
            Feature types to apply.

                Default: ["sum", "std", "max", "skew", "min", "mean", "count", "percent_true", "num_unique", "mode"]
                DateTime: ['time_since_last', 'time_since_first', 'trend']

        trans_primitives (list[str or TransformPrimitive], optional):
            List of Transform Feature functions to apply.

                Default: ["day", "year", "month", "weekday", "haversine", "num_words", "num_characters"]

        groupby_trans_primitives (list[str or :class:`.primitives.TransformPrimitive`], optional):
            list of Transform primitives to make GroupByTransformFeatures with

        """
        if ignore_variables is None:
            ignore_variables = [self.target_entity_id, self.index]

        if trans_primitives is None:
            trans_primitives = [
                "year", "month", "day", "hour", "minute", "week", "weekday", "is_weekend",
                'time_since_previous',  # diff
                Quarter(),
            ]

        _ = ft.dfs(
            entityset=self.es,
            target_entity=self.target_entity_id,  # 具有唯一ID: 不重复id的base_es或者normalize_entity生成的唯一id es
            features_only=features_only,
            max_depth=max_depth,
            ignore_variables={self.entity_id: ignore_variables},
            chunk_size=chunk_size,
            n_jobs=n_jobs,
            verbose=1,
            agg_primitives=agg_primitives,
            trans_primitives=trans_primitives,
            **kwargs
        )

        if features_only:
            return _
        else:
            df_ = _[0].add_prefix(f'{self.entity_id}_').reset_index()
            df_ = remove_low_information_features(df_)
            df_ = remove_single_value_features(df_, count_nan_as_value=True)

            if reduce_mem:
                df_ = reduce_mem_usage(df_)

            return df_

    @property
    def normalize_entity_cols(self):
        types = [vt.Id, vt.Categorical, vt.Boolean]
        cols = sum([self.type2features.get(type_, []) for type_ in types], [])
        return [i for i in cols if i != self.index]

    @property
    def variable_types(self):
        dic = {}
        for type_, features in self.type2features.items():
            dic.update(zip(features, len(features) * [type_]))
        return dic

    def _convert_type(self, type2features):
        type2features_ = {}
        for type_, features in type2features.items():
            if isinstance(type_, str):
                type2features_[vt.__getattribute__(type_)] = features
            else:
                type2features_[type_] = features

        return type2features_


if __name__ == '__main__':
    import pandas as pd

    df = pd.DataFrame([[1, 2, 3], [2, 2, 3], [3, 2, 3]], columns=['uid', 'a', 'b'])

    type2features = {
        vt.Id: ['uid'],
        vt.Categorical: ['a', 'b']
    }

    af = AutoFeat(df, 'test', 'test', type2features, index='uid')  # base_entity 就是 base_entity_id

    print(af.run_dfs(max_depth=2))  # print(af.run_dfs(max_depth=2, ignore_variables=['uid']))
