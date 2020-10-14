import os
import pickle

import pandas as pd

from .model.model import SbModel


def build(sb_model: SbModel):
    # Get all input files downloaded
    train_path = '/opt/ml/input/data/train'
    input_files = [os.path.join(train_path, file) for file in os.listdir(train_path)]

    if len(input_files) == 0:
        raise Exception(f'There are no files in {train_path}. This usually indicates that the '
                        f'channel ("train") was incorrectly specified, the data specification in '
                        f'S3 was incorrectly specified or the role specified does not have '
                        f'permission to access the data.')

    # Take the set of files and read them all into a single pandas dataframe
    raw_data = [pd.read_csv(path, compression='gzip', sep='|', quotechar='"') for path in
                input_files]
    train_input = pd.concat(raw_data)
    sb_model.train(train_input)

    with open('sb_model.pickle', 'wb') as handle:
        pickle.dump(sb_model, handle)

    # Copy output model to the sagemaker model path
    os.system("cp sb_model.pickle /opt/ml/model/sb_model.pickle")
