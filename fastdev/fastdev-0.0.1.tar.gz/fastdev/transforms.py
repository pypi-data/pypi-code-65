import os.path
import numpy as np
import torch
from transformers import BertTokenizer
from global_vars import BERT, BERT_CHINESE

def bert_chinese_tokenize(corpus):
    vocab_path = os.path.join(BERT_CHINESE, 'vocab.txt')
    tokenizer = BertTokenizer(vocab_file=vocab_path)
    return [tokenizer.encode(sen) for sen in corpus]

def bert_tokenize(corpus):
    vocab_path = os.path.join(BERT, 'vocab.txt')
    tokenizer = BertTokenizer(vocab_file=vocab_path)
    return [tokenizer.encode(sen) for sen in corpus]

def padding(corpus, padding_idx=0):
    max_l = max(map(len, corpus))
    ids = [sen+[padding_idx]*(max_l-len(sen)) for sen in corpus]
    
    ids = np.array(ids)
    mask = (ids != padding_idx).astype(int)

    return ids, mask

if __name__ == "__main__":
    corpus = ["测试中的依据", "呵呵apple"]

    print(padding(bert_chinese_tokenize(corpus)))