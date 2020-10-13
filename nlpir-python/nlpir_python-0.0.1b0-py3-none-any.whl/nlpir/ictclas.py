#! coding=utf-8
"""
high-level toolbox for Chinese Word Segmentation
"""
import nlpir.native.ictclas
# ICTCLAS instance
__ictclas__ = None

def __get_instance__():
    if __ictclas__ is None:
        return nlpir.native.ictclas.ICTCLAS()

