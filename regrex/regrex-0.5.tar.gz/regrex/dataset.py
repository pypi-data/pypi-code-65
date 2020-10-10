import sklearn.model_selection as model_selection

def TestTrainSplit(x, y, trainsize, testsize, randomstate):
    return model_selection.train_test_split(x, y, train_size=trainsize,test_size=testsize, random_state=randomstate)

