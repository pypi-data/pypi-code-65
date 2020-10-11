import keras #for one-hot-encoding
import math 

class InMemoryImgHandler:
    """ Handles image data available in RAM

    + Splits and stores data in-memory
    + Creates one-hot-encoded targets if specified

    Attributes
    ___________
    - x_train  : np.ndarray
    - x_test   : np.ndarray
    - y_train  : np.ndarray
    - y_test   : np.ndarray

    Methods
    _______ 
    - train_val_test_split(X: np.ndarray, y: np.ndarray, ratio: tuple)
    - one_hot_encode(y: np.ndarray, num_classes: int)
    """

    
    def __init__(self, X, y, y_info, ratio=(60,20,20)):
        """
        - X: np.ndarray
            + np.nd array (n_samples, w, h, c)
        - y: np.ndarray
            + Either one-hot-encoded (n_smaple, n_classes) bin matrix
            + or numeric (n_smaple, 1) vec
        - y_info: tuple
            - y_info[0]: int 
                + num_classes
            - y_info[1]: bool 
                + True if one-hot-encoded already
        - ratio: tuple = (60,20,20)
            + (train_ratio, val_ratio, test_ratio) between 0-100 and sum to 100
        """

        if y_info[1] is False:
            y = self.one_hot_encode(y, y_info[0])
        
        # split and store                
        (self.x_train, self.y_train), (self.x_val, self.y_val), (self.x_test, self.y_test) = \
            InMemoryImgHandler.train_val_test_split(X, y, ratio)

    # ============================================================================================
    # BEG: static methods 
    # ============================================================================================
    @staticmethod
    def train_val_test_split(X, y, ratio):
        """ Splits data into train test and validation

        Parameters
        __________
        - X: np.ndarray 
            + 4-D (n_samples, w, h, c) 
        - y: np.ndarray
            + one-hot-encoded bin matrix
        - ratio: tuple 
            + (train_ratio, val_ratio, test_ratio)

        Returns 
        _______
        tuple 
            + (X_tr, y_tr), (X_val, y_val), (X_te, y_te)

        * Note: Not shufflind cz, taken care by `model.fit`
        """

        if (ratio[0] + ratio[1] + ratio[2]) != 100:
            raise Exception('Split percents\' sum must be 100!')

        n_samples = X.shape[0]
        n_train   =  math.floor( (ratio[0]/100) * n_samples )
        n_val     =  math.floor( (ratio[1]/100) * n_samples )
        n_test    =  math.floor( (ratio[2]/100) * n_samples )
        
        train_l, train_r   =             0, n_train
        val_l, val_r       =       n_train, n_train+n_val
        test_l, test_r     = n_train+n_val, n_train+n_val+n_test
        
        return (
            ( X[train_l:train_r], y[train_l:train_r] ), 
            ( X[val_l:val_r]    , y[val_l:val_r] ), 
            ( X[test_l:test_r]  , y[test_l:test_r] ), 
        )
    
    @staticmethod
    def one_hot_encode(y, num_classes):
        """ y (is n_samples, 1) 2-D vector. Not a flat array"""
        return keras.utils.to_categorical(y, num_classes)
    # ============================================================================================
    # END: static methods 
    # ============================================================================================