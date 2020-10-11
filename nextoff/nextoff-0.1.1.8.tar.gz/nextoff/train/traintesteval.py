import os
import keras
from nextoff.models.raw import TestModel

# =======================================================================================
# BEG: abstraction for train, test and eval of model
# =======================================================================================
def train_test_model_with(data, args, savename="bestmodel"):
    """ Build temporary model and train/test/eval/plot w/ it 
    
    Parameters
    __________
    - data: data.inmemory.InMemoryImgHandler
    - args:  must follow convention
    - savename: str
        + name of the saved model inside `BestSavedModels` dir
    """
    # initialize and build
    # --------------------
    baseline_model = TestModel(args)
    baseline_model.compile(args)
    
    # Train eval, save and plot
    # -------------------------
    if 'v' in args.__dict__: v = args.v
    else: v = 0
    hist = baseline_model.fit( 
                (data.x_train, data.y_train),
                (data.x_val, data.y_val), 
                v,
                savename, 
                args
    )
    
    # Evaluate the performance (unseen data)
    baseline_model.evaluate(data.x_test, data.y_test)
    # plot
    baseline_model.plot()

    return hist
# =======================================================================================
# END: abstraction for train, test and eval of model
# =======================================================================================