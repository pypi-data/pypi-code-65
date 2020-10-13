import os
import pickle
import random

import numpy as np
import pandas as pd
from notedata.manage import DatasetManage
from notetool.tool import exists_file, log

logger = log(__name__)


class DataSet:
    """
    """

    def __init__(self, dataset: DatasetManage = None, data_path='./download/'):
        """
        """
        # 源文件保存目录
        self.dataset = dataset or DatasetManage()
        self.path_root = data_path

    def download(self,):
        """
        """
        pass

    def preprocess(self, step=0):
        """
        """
        pass


class ElectronicsData(DataSet):
    def __init__(self, *args, **kwargs):
        super(ElectronicsData, self).__init__(*args, **kwargs)

        # 源文件
        self.json_meta = self.path_root + '/electronics/meta_Electronics.json'
        self.json_reviews = self.path_root + '/electronics/reviews_Electronics_5.json'

        # 格式化文件
        self.pkl_meta = self.path_root + '/electronics/raw_data/meta.pkl'
        self.pkl_reviews = self.path_root + '/electronics/raw_data/reviews.pkl'

        # 结果文件
        self.pkl_remap = self.path_root + '/electronics/raw_data/remap.pkl'
        self.pkl_dataset = self.path_root + '/electronics/raw_data/dataset.pkl'

    def download_raw_0(self, overwrite=False):
        self.dataset.download('electronics-reviews',
                              overwrite=overwrite, path_root=self.path_root)
        self.dataset.download('electronics-meta',
                              overwrite=overwrite, path_root=self.path_root)

        logger.info("download done")
        logger.info("begin unzip file")

        os.system('cd ' + self.path_root +
                  '/electronics && gzip -d reviews_Electronics_5.json.gz')
        os.system('cd ' + self.path_root +
                  '/electronics && gzip -d meta_Electronics.json.gz')
        logger.info("unzip done")

    def convert_pd_1(self, overwrite=False):
        if exists_file(self.pkl_reviews, mkdir=True) and exists_file(self.pkl_meta, mkdir=True):
            return

        def to_df(file_path):
            with open(file_path, 'r') as fin:
                df = {}
                i = 0
                for line in fin:
                    df[i] = eval(line)
                    i += 1
                df = pd.DataFrame.from_dict(df, orient='index')
                return df

        reviews_df = to_df(self.json_reviews)
        with open(self.pkl_reviews, 'wb') as f:
            pickle.dump(reviews_df, f, pickle.HIGHEST_PROTOCOL)

        meta_df = to_df(self.json_meta)
        meta_df = meta_df[meta_df['asin'].isin(reviews_df['asin'].unique())]
        meta_df = meta_df.reset_index(drop=True)
        with open(self.pkl_meta, 'wb') as f:
            pickle.dump(meta_df, f, pickle.HIGHEST_PROTOCOL)

    def remap_id_2(self, overwrite=False):
        random.seed(1234)
        if exists_file(self.pkl_remap, mkdir=True):
            return

        # reviews
        reviews_df = pd.read_pickle(self.pkl_reviews)
        reviews_df = reviews_df[['reviewerID', 'asin', 'unixReviewTime']]
        # meta
        meta_df = pd.read_pickle(self.pkl_meta)
        meta_df = meta_df[['asin', 'categories']]
        # 类别只保留最后一个
        meta_df['categories'] = meta_df['categories'].map(lambda x: x[-1][-1])

        # with open(self.pkl_reviews, 'rb') as f:
        #     reviews_df = pickle.load(f)
        #     reviews_df = reviews_df[['reviewerID', 'asin', 'unixReviewTime']]

        # with open(self.pkl_meta, 'rb') as f:
        #     meta_df = pickle.load(f)
        #     meta_df = meta_df[['asin', 'categories']]
        #     meta_df['categories'] = meta_df['categories'].map(
        #         lambda x: x[-1][-1])

        def build_map(df, col_name):
            """
            制作一个映射，键为列名，值为序列数字
            :param df: reviews_df / meta_df
            :param col_name: 列名
            :return: 字典，键
            """
            key = sorted(df[col_name].unique().tolist())
            m = dict(zip(key, range(len(key))))
            df[col_name] = df[col_name].map(lambda x: m[x])
            return m, key

        # meta_df文件的物品ID映射
        asin_map, asin_key = build_map(meta_df, 'asin')
        # meta_df文件物品种类映射
        cate_map, cate_key = build_map(meta_df, 'categories')
        # reviews_df文件的用户ID映射
        view_map, view_key = build_map(reviews_df, 'reviewerID')

        # user_count: 192403	item_count: 63001	cate_count: 801	example_count: 1689188
        user_count, item_count, cate_count, example_count = \
            len(view_map), len(asin_map), len(cate_map), reviews_df.shape[0]
        logger.info('user_count: %d\t item_count: %d\t cate_count: %d\t example_count: %d' %
                    (user_count, item_count, cate_count, example_count))

        # 按物品id排序，并重置索引
        meta_df = meta_df.sort_values('asin')
        meta_df = meta_df.reset_index(drop=True)

        # reviews_df文件物品id进行映射，并按照用户id、浏览时间进行排序，重置索引
        reviews_df['asin'] = reviews_df['asin'].map(lambda x: asin_map[x])
        reviews_df = reviews_df.sort_values(['reviewerID', 'unixReviewTime'])
        reviews_df = reviews_df.reset_index(drop=True)
        reviews_df = reviews_df[['reviewerID', 'asin', 'unixReviewTime']]

        # 各个物品对应的类别
        cate_list = np.array(meta_df['categories'], dtype='int32')
        # cate_list = [meta_df['categories'][i] for i in range(len(asin_map))]
        # cate_list = np.array(cate_list, dtype=np.int32)

        # 保存所需数据为pkl文件
        with open(self.pkl_remap, 'wb') as f:
            pickle.dump(reviews_df, f, pickle.HIGHEST_PROTOCOL)  # uid, iid
            pickle.dump(cate_list, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump((user_count, item_count, cate_count, example_count),
                        f, pickle.HIGHEST_PROTOCOL)
            pickle.dump((asin_key, cate_key, view_key),
                        f, pickle.HIGHEST_PROTOCOL)

    def build_dataset_3(self, overwrite=False):
        random.seed(1234)
        if exists_file(self.pkl_dataset, mkdir=True):
            return

        with open(self.pkl_remap, 'rb') as f:
            reviews_df = pickle.load(f)
            cate_list = pickle.load(f)
            user_count, item_count, cate_count, example_count = pickle.load(f)

        train_set, test_set = [], []
        # 最大的序列长度
        max_sl = 0

        """
        生成训练集、测试集，每个用户所有浏览的物品（共n个）前n-1个为训练集（正样本），并生成相应的负样本，每个用户
        共有n-2个训练集（第1个无浏览历史），第n个作为测试集。
        故测试集共有192403个，即用户的数量。训练集共2608764个
        """
        for reviewerID, hist in reviews_df.groupby('reviewerID'):
            # 每个用户浏览过的物品，即为正样本
            pos_list = hist['asin'].tolist()
            max_sl = max(max_sl, len(pos_list))

            def gen_neg():
                neg = pos_list[0]
                while neg in pos_list:
                    neg = random.randint(0, item_count - 1)
                return neg

            # 正负样本比例1：1
            neg_list = [gen_neg() for i in range(len(pos_list))]

            for i in range(1, len(pos_list)):
                # 生成每一次的历史记录，即之前的浏览历史
                hist = pos_list[:i]
                sl = len(hist)
                if i != len(pos_list) - 1:
                    # 保存正负样本，格式：用户ID，正/负物品id，浏览历史，浏览历史长度，标签（1/0）
                    train_set.append((reviewerID, pos_list[i], hist, sl, 1))
                    train_set.append((reviewerID, neg_list[i], hist, sl, 0))
                else:
                    # 最后一次保存为测试集
                    label = (pos_list[i], neg_list[i])
                    test_set.append((reviewerID, hist, sl, label))

        # 打乱顺序
        random.shuffle(train_set)
        random.shuffle(test_set)

        assert len(test_set) == user_count

        # 写入dataset.pkl文件
        with open(self.pkl_dataset, 'wb') as f:
            pickle.dump(train_set, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(test_set, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump(cate_list, f, pickle.HIGHEST_PROTOCOL)
            pickle.dump((user_count, item_count, cate_count,
                         max_sl), f, pickle.HIGHEST_PROTOCOL)

    def init_data(self, overwrite=False):
        self.download_raw_0(overwrite=overwrite)

        self.convert_pd_1(overwrite=overwrite)

        self.remap_id_2(overwrite=overwrite)

        self.build_dataset_3(overwrite=overwrite)

    def download(self):
        self.download_raw_0(overwrite=False)

    def preprocess(self, step=0):
        if step == 0:
            self.convert_pd_1()
            self.remap_id_2()
            self.build_dataset_3()
        elif step == 1 or step=='convert pd':
            self.convert_pd_1()
        elif step == 2 or step=='remap id':
            self.remap_id_2()
        elif step == 3 or step=='build dataset':
            self.build_dataset_3()


class CriteoData(DataSet):
    def __init__(self,*args, **kwargs):
        super(CriteoData,self).__init__(*args, **kwargs)
    
    def download(self):
        pass

    def preprocess(self,step=0):
        pass
