#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from itertools import combinations


# In[2]:


days_to_string = {
    1: "Mon",
    2: "Tue",
    4: "Wed",
    8: "Thu",
    16: "Fri",
    32: "Sat",
    64: "Sun"
}


# In[8]:


# TODO: transfrom to list comprehension
# comb for comb in combinations(lis, n) for n in range(1, len(lis)+1) if sum(comb) == dow
def find_dow(dow):
    lis = [1, 2, 4, 8, 16, 32, 64]
    for n in range(1, len(lis)+1):
        for comb in combinations(lis, n):
            try:
                if sum(comb) == int(dow):
                    return comb
            except:
                return None


# In[9]:


def get_dow(column):
    all_days = []
    d_list = [find_dow(val) for val in column]
    for item in d_list:
        d = ''            
        try:
            for i in item:
                if i == item[-1]:
                    d += (days_to_string[i])
                else:
                    d += (days_to_string[i] + ', ')

            all_days.append(d)

        except:
            d += 'NaN'
            all_days.append(d)

    return all_days

