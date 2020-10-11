import os
import re
import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter

class pjftools:
    def __init__(self, data:'dataframe'=None, col_key:str=None, col_value:str=None, dict_keyword={}, colcontent='content'):
        self.df = data
        self.col_key = col_key
        self.col_value = col_value
        self.dict_keyword = dict_keyword
        self.col_content = colcontent
        
    def time_calc(func):
        ''' 装饰器，计算函数运行时间 '''
        def wrapper(*args, **kargs):
            start_time = datetime.now()
            f = func(*args, **kargs)
            exec_time = datetime.now() - start_time
            print('运行 {0} 耗时为：{1}'.format(func.__name__,exec_time))
            return f
        return wrapper
        
    def _count(self, axis:int=0) -> int:
        return self.df.shape[axis]
    
    def value_nunique(self) -> int:
        return self.df[self.col_value].nunique()
    
    def count_value(self) -> str:
        list_data = [(value, group.shape[0]) for value, group in self.df.groupby(self.col_value)]
        list_data = sorted(list_data, key=lambda x:x[1], reverse=True)
        data = '、'.join(['{0}({1})'.format(i[0], i[1]) for i in list_data])
        return data
    
    def textinfo(text:str, list_word:list=[], dictionary:dict={}, wordinfo:dict={}, info:list=['info', 'allcnt', 'diffcnt']) -> dict:
        '''  根据string统计keywordinfo   '''
        dictionary = {'word':list_word} if list_word!=[] else dictionary
        for key, values in dictionary.items():
            wordinfo[key] = {}
            wordinfo[key]['info'] = ' '.join(sorted(['{0},{1}'.format(word, text.count(word)) for word in values if word in text], key=lambda x:x.split(',')[1], reverse=True))
            if not wordinfo[key]['info']: wordinfo[key]['allcnt'], wordinfo[key]['diffcnt'] = 0,0; continue
            wordinfo[key]['allcnt'] = sum([int(i.split(',')[1]) for i in wordinfo[key]['info'].split(' ')])
            wordinfo[key]['diffcnt'] = len(wordinfo[key]['info'].split(' '))
            wordinfo[key] = {i:wordinfo[key][i] for i in info if i in wordinfo[key].keys()}
        wordcloud = ' '.join(sorted([i for i in wordcloud.split(' ') if i != ''], key=lambda x:x.split(',')[1], reverse=True))
        return wordinfo
    
    @time_calc
    def wordinfo(df:'dataframe', KeyColumns:str, colcontent:str='content', dict_keyword:dict={}, na=False) -> 'dataframe':
        ''' 基于dict，对dataframe进行关键词统计，计算不同类型关键词的总数，不同数 '''
        res,keyword_res = [],{}
        for value, group in df.groupby(KeyColumns):
            allcnt,diffcnt,types,wordcloud = 0,0,0,''
            content = ' '.join(group[colcontent].astype(str))
            for key, values in dict_keyword.items():
                keyword_res[key] = {}
                keyword_res[key]['message'] = ' '.join(sorted(['{0},{1}'.format(word, content.count(word)) for word in values if word in content], key=lambda x:x.split(',')[1], reverse=True))
                if not keyword_res[key]['message']: keyword_res[key]['allcnt'], keyword_res[key]['diffcnt'] = 0,0; continue
                keyword_res[key]['allcnt'] = sum([int(i.split(',')[1]) for i in keyword_res[key]['message'].split(' ')])
                keyword_res[key]['diffcnt'] = len(keyword_res[key]['message'].split(' '))
                wordcloud += '{0} '.format(keyword_res[key]['message'])
                allcnt += keyword_res[key]['allcnt']
                diffcnt += keyword_res[key]['diffcnt']
                types += 1 if keyword_res[key]['diffcnt']!=0 else 0
            wordcloud = ' '.join(sorted([i for i in wordcloud.split(' ') if i != ''], key=lambda x:x.split(',')[1], reverse=True))
            res += [[value, allcnt, diffcnt, types, wordcloud] + [j for i in [list(v.values()) for k,v in keyword_res.items()] for j in i]]
        df = pd.DataFrame(res, columns = [KeyColumns, 'allcnt', 'diffcnt', 'types', 'wordcloud'] + [f'{k}_{v_k}' for k,v in keyword_res.items() for v_k in list(v.keys())])
        df = df if na==True else df.query('allcnt > 0').reset_index(drop=True)
        return df
    
    @time_calc
    def value_count(self, data:'datarame', col_key:str, col_value:str, res_:list=[]) -> 'dataframe':
        ''' 统计次数 '''
        self.df,self.col_key,self.col_value = data,col_key,col_value
        for key, group in self.df.groupby(self.col_key):
            self.df,self.col_key = group,key
            res_ += [[key, self._count(), self.value_nunique(), self.count_value()]]
        resdf = pd.DataFrame(res_, columns=[col_key, 'count', 'diff_{}'.format(self.col_value), 'data_{}'.format(self.col_value)]).sort_values(by='diff_{}'.format(self.col_value), ascending=False).reset_index(drop=True)
        return resdf
    
    def mergeplus(data:list=None, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x','_y'), copy=True, indicator=False, validate=None,):
        '''   批量迭代合并dataframe   '''
        from functools import reduce
        resdf = reduce(lambda x,y:pd.merge(x, y, how=how, on=on, left_on=left_on, right_on=right_on, left_index=left_index, right_index=right_index, sort=sort, suffixes=suffixes, copy=copy, indicator=indicator, validate=validate), data)
        return resdf
    
    def add_split(df:'dataframe', column:str, sep:str=',', axis:int=0) -> 'dataframe':
        ''' 根据分隔符，切分合并数据 '''
        dict_action = {0:df.merge(df[column].str.split(sep).explode(), left_index=True, right_index=True), \
                       1:df.merge(df[column].str.split(sep, expand=True), left_index=True, right_index=True)}
        df = dict_action[axis] if axis in dict_action else print('清输入正确的 axis 参数 1 or 0')
        return df
    
    def textrank(sentence, topK=20, withWeight=False, allowPOS=('ns','n','vn','v'), withFlag=False,) -> list:
        ''' 基于 textrank 提取关键词 '''
        import jieba.analyse
        list_keyword = jieba.analyse.textrank(sentence=sentence, topK=topK, withWeight=withWeight, allowPOS=allowPOS, withFlag=withFlag)
        return list_keyword
    
    def extract_address(data:[list, 'dataframe'], column=0, index=[], cut=True, lookahead=8, pos_sensitive=False, open_warning=True,):
        '''   cpca进行地址提取  '''
        import cpca
        data = pd.DataFrame(data)
        address = pd.merge(data, cpca.transform(data.loc[:,column], index=index, cut=cut, lookahead=lookahead, pos_sensitive=pos_sensitive, open_warning=open_warning), left_index=True, right_index=True)
        return address
    
class load_data():
    def _read_dictionary(file:str, resdict:dict={}, encoding:str='utf-8', sep=',') -> dict:
        '''  加载关键词字典  '''
        with open(file=file, encoding=encoding) as f:
            for line in f.readlines():
                lines = line.split(':')
                value = re.sub('[\n\r]$', '', ''.join(lines[1:])).split(sep)
                value = list(filter(None, value))
                resdict[lines[0]] = value if len(value)>1 else value[0]  
        return resdict

    def _read_keyword(file:str, list_word:list=[], encoding:str='utf-8', sep:str='|') -> str:
        '''  加载关键词  '''
        with open(file=file, encoding=encoding) as f:
            for line in f.readlines():
                list_word += re.sub('[\n\r]$', '', line.split(':')[1]).split(',')
            keyword = sep.join(list_word)
        return keyword
        
class re_:
    '''  常用正则匹配  '''
    def __init__(self, path_dict:str=None):
        '''   目前支持类型为：'ip', 'email', 'phone', 'idcard', 'carlisence', 'url'  '''
        self.dict_re = {'ip':'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',\
                        'email':'[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}',\
                        'phone':'(?:\+?86)?1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7(?:[235-8]\d{2}|4(?:0\d|1[0-2]|9\d))|9[0-35-9]\d{2}|66\d{2})\d{6}',\
                        'idcard':'[1-9]\d{5}[12]\d{3}(?:0[1-9]|1[012])(?:0[1-9]|[12]\d|3[01])\d{3}(?:X|x|\d)',\
                        'carlisence':'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Za-z]{1}[A-Za-z0-9]{4}[A-Za-z0-9挂学警港澳]{1}',\
                        'url':'[((https?|ftp|file)://)(www)][-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'}

    def judge_pattern(self, info=None, pattern:str=None) -> tuple:
        '''  pattern参数信息增加到self.dict_re'''
        info = [info] if type(info)!=list else info
        if pattern!=None:
            self.dict_re[pattern] = pattern
            info.append(pattern)
            types = list(self.dict_re.keys())
        return info,types

    def judge_unableinfo(self, info=None, types:list=None) -> str:
        ''' 提示info中的无效信息并剔除'''
        if len(set(info).difference(set(types)))>0:
            print('暂未提供正则类型(努力更新中...)：{}'.format('、'.join(list(set(info).difference(set(types))))))
            info = list(set(types).intersection(set(info)))
        return info

    def judge_counter(self, text:str, info:list=None, counter:bool=False) -> dict:
        '''  是否统计发现次数  '''
        if counter:
            resdict = {i:dict(Counter(re.findall(self.dict_re[i], text))) for i in info}
        else:
            resdict = {i:list(set(re.findall(self.dict_re[i], text))) for i in info}
        return resdict

    def extract_info(self, text:str, info=None, pattern:str=None, counter:bool=False) -> dict:
        '''  提取信息  '''
        pattern_ = self.judge_pattern(info, pattern)
        info,types = pattern_[0],pattern_[1]
        info = self.judge_unableinfo(info, types)
        resdict = self.judge_counter(text=text, info=info, counter=counter)                
        return resdict