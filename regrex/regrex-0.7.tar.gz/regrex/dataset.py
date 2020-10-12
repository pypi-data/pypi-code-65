import sklearn.model_selection as model_selection
import pickle as pk

def TestTrainSplit(x, y, testsize, randomstate):
    return model_selection.train_test_split(x, y, test_size=testsize, random_state=randomstate)

def SaveData(x, y, output_file):
    data = {"x": x, "y": y}
    with open(output_file, 'wb') as outfile:
        pk.dump(data, outfile)

def LoadData(input_file):
    with open(input_file, 'rb') as infile:
        data = pk.load(infile)
    return data    