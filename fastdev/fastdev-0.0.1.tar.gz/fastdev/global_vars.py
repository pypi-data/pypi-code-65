import os.path

DATASET_BASE = "/Users/jasper.wang/Workspace/resources/dataset/"
CONLL = os.path.join(DATASET_BASE, 'conll2012')

MODEL_BASE = "/Users/jasper.wang//Workspace/resources/models/"
BERT = os.path.join(MODEL_BASE, 'bert_base_uncased')
BERT_CHINESE = os.path.join(MODEL_BASE, 'bert_chinese')

""" print('-'*50)
print('Datasets:')
print(f'conll2012: {CONLL}')
print('-'*50)
print('Models:')
print(f'bert: {BERT}')
print(f'bert chinese: {BERT_CHINESE}')
print('-'*50) """
