import matplotlib.pyplot as plt # plotting
import os # for file/folder creations
import keras
from keras.models import Model, Sequential
from keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Activation, Flatten, BatchNormalization, Input, Dense
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator

# =======================================================================================
# BEG: build custom model based on args
# =======================================================================================
class TestModel:
    """ Tensorflow model created using args

    Attributes
    __________
    - args: all configs

    Methods
    _______
    - build_model(args)
    - compile(args)
    - fit(train_data, val_data, v, savename, args)
       - train_data: tuple of X and y
       - val_data: tuple of X and y
    - evaluate(x_test, y_test)
       + evaluates on completely unseen data
    - save_to(save_path)
    - summary
    - plot
    """
    def __init__(self, args):
        # build model
        self.args = args
        self.model = self.build_model(args)    
    
    def build_model(self, args):
        # define input dims
        input_dims = Input(shape=args.input_shape)#(32,32,3)) # flexible batch size
        
        x = self.convs_from_seq(args.conv_seq, input_dims)
        x = Flatten()(x)
        x = self.fcs_from_seq(args.fcs_seq, x)
        
        return Model(inputs=input_dims, outputs=x)
    
    def compile(self, args):

        # todo: add other optimizers
        if   'RMSprop' in args.__dict__ : opt = keras.optimizers.RMSprop(**args.RMSprop)
        elif 'SGD'     in args.__dict__ : opt = keras.optimizers.SGD(**args.SGD)
        elif 'Adam'    in args.__dict__ : opt = keras.optimizers.Adam(**args.Adam)
        else: 
            raise Exception('Define optimizers name exactly as in keras.optimizers')

        self.model.compile(
            loss       = args.loss,
            optimizer  = opt,
            metrics    = args.metrics,
        )
    
    # ----------------------------------------------------------
    # Training and evaluation
    # ----------------------------------------------------------
    def fit(self, train_data, val_data, v, savename, args):
        """train_data, val_data are tuples of X and y"""
        if v==0:
            print("Wait for the big picture ☕️\n\nTrainng started ...")
        num_samples = train_data[0].shape[0] #X
        num_batches = num_samples / args.batch_size

        callbacks_list = []
        # custom callbacks (single only)
        if 'CustomCallback' in args.__dict__:
            callbacks_list.append(args.CustomCallback(num_batches))
        
        # checkpointer callback
        os.makedirs(f'BestSavedModels', exist_ok=True)
        check = ModelCheckpoint(
            filepath=f"./BestSavedModels/{savename}.h5",
            verbose=v, save_best_only=True
        )
        callbacks_list.append(check)
        
        # instantiate and fit data generator
        traingen = ImageDataGenerator(**args.train_data_gen)
        valgen = ImageDataGenerator(**args.val_data_gen)
        traingen.fit(train_data[0])

        self.history = self.model.fit(
            traingen.flow(train_data[0], train_data[1], args.batch_size),
            validation_data = valgen.flow(val_data[0], val_data[1], batch_size=args.batch_size),
            steps_per_epoch = len(train_data[0]) / args.batch_size, 
            epochs          = args.epochs,
            shuffle         = args.shuffle,
            verbose         = v,
            callbacks       = callbacks_list
        )

        return self.history
    
    # evaluation
    def evaluate(self, x_test, y_test):
        print("Evaluating on test data...\n")
        testgen  = ImageDataGenerator(**self.args.test_data_gen)

        test_loss, test_acc = \
            self.model.evaluate(
                testgen.flow(x_test, y_test, batch_size=self.args.batch_size)
            )
        print(f"+ Test Loss\t:{test_loss}\n+ Test Acc\t:{test_acc}")
    
    # save
    def save_to(self, save_path):
        self.model.save(save_path)
    
    # -----------------------------------------------------------
    # plot
    # -----------------------------------------------------------
    def plot(self):
        history_dict = self.history.history
        
        # Plot loss chart
        loss_values     = history_dict['loss']
        val_loss_values = history_dict['val_loss']
        epochs          = range(1, len(loss_values) + 1)
        
        line1 = plt.plot(epochs, val_loss_values, label='Validation/Test Loss')
        line2 = plt.plot(epochs, loss_values, label='Training Loss')
        
        plt.setp(line1, linewidth=2.0, marker = '+', markersize=10.0)
        plt.setp(line2, linewidth=2.0, marker = '4', markersize=10.0)
        plt.xlabel('Epochs') 
        plt.ylabel('Loss')
        plt.grid(True)
        plt.legend()
        
        # Plot acc chart
        acc_values      = history_dict['accuracy']
        val_acc_values  = history_dict['val_accuracy']
        epochs          = range(1, len(loss_values) + 1)

        line1 = plt.plot(epochs, val_acc_values, label='Validation/Test Accuracy')
        line2 = plt.plot(epochs, acc_values, label='Training Accuracy')
        
        plt.setp(line1, linewidth=2.0, marker = '+', markersize=10.0)
        plt.setp(line2, linewidth=2.0, marker = '4', markersize=10.0)
        plt.xlabel('Epochs') 
        plt.ylabel('Accuracy')
        plt.grid(True)
        plt.legend()        
        
        # display
        plt.show()
    
    def summary(self):
        keras.utils.plot_model(
            self.model,
            to_file="model.png",
            show_shapes=False,
            #show_dtype=False,
            show_layer_names=True,
            rankdir="TB",
            expand_nested=False,
            dpi=96,
        )
        return self.model.summary()    
    # ===========================================================
    # BEG: build_model helpers
    # ===========================================================
    def convs_from_seq(self, seq, x):
        """
        + x is input which will be forwarded in series 
        + seq is of format
            [
                {"out_ch": int, "z": int, 'act': 'relu', 'bn': True, 'p': 0.5, 'L1': 1e-4},
                {"out_ch": int, "z": int, 'act': 'relu', "maxpool_z": 2},
                # -------------------------------------------------------
                {"out_ch": int, "z": int, 'act': 'relu'},
                ....
            ]
        + regularize all if `args.regularize_all = L1 / L2 / L1L2` 
        """
        # bulid series
        series = []
        for config in seq:
            
            # append convs and nonlin one-by-one                
            # regularize all
            kernel_regularizer = None
            if ('L1' in self.args.__dict__):
                kernel_regularizer =  keras.regularizers.l1(l1=self.args.__dict__['L1'])
            elif ('L2' in self.args.__dict__):
                kernel_regularizer =  keras.regularizers.l2(l2=self.args.__dict__['L2'])
            elif ('L1L2' in self.args.__dict__):
                kernel_regularizer =  keras.regularizers.l1_l2(
                    l1=self.args.__dict__['L1L2'][0], 
                    l2=self.args.__dict__['L1L2'][1]
                )
            # regularize >>>individually<<<
            # (OVERWRITE `kernel_regularizer` created by regularize all)
            if 'L1' in config:
                kernel_regularizer =  keras.regularizers.l1(l1=config['L1'])
            elif 'L2' in config:
                kernel_regularizer =  keras.regularizers.l2(l2=config['L2'])
            elif 'L1L2' in config:
                kernel_regularizer =  keras.regularizers.l1_l2(
                    l1=config['L1L2'][0],
                    l2=config['L1L2'][1],
                )
            
            series.append(
                self.__get_conv(
                    out_ch              = config['out_ch'],
                    z                   = config['z'],
                    padding             = 'same',
                    kernel_regularizer  = kernel_regularizer
                )
            )
            
            # activation function
            series.append(self.__get_act(config['act']))
            
            # pool if specified
            if 'maxpool_z' in config.keys():
                # append pool one-by-one
                series.append(self.__get_pool(config['maxpool_z']))
            
            # (before bn)
            if 'p' in config.keys():
                series.append(self.__get_dropout(config["p"]))
                
            # batchnorm (after dropout)
            if 'bn' in config.keys():
                if config['bn'] is True:
                    # append bn one-by-one
                    series.append(self.__get_bn())

        # forward through series
        """ #OVERKILL
        return Sequential(series)
        """
        for layer in series:
            x = layer(x)
        return x

    def fcs_from_seq(self, seq, x):
        """
        + x is input
        + seq is of format
            [
                {"out_nodes": int, "act": 'relu', 'bn': True},
                {"out_nodes": int, "act": 'relu', 'bn': Fale, 'p': 0.5 },
                ....
            ]
        """
        # build series
        series = []
        for config in seq:
            
            # regularize all
            kernel_regularizer = None
            if ('L1' in self.args.__dict__):
                kernel_regularizer =  keras.regularizers.l1(l1=self.args.__dict__['L1'])
            elif ('L2' in self.args.__dict__):
                kernel_regularizer =  keras.regularizers.l2(l2=self.args.__dict__['L2'])
            elif ('L1L2' in self.args.__dict__):
                kernel_regularizer =  keras.regularizers.l1_l2(
                    l1=self.args.__dict__['L1L2'][0], 
                    l2=self.args.__dict__['L1L2'][1]
                )
            # regularize >>>individually<<<
            # (OVERWRITE `kernel_regularizer` created by regularize all)
            if 'L1' in config:
                kernel_regularizer =  keras.regularizers.l1(l1=config['L1'])
            elif 'L2' in config:
                kernel_regularizer =  keras.regularizers.l2(l2=config['L2'])
            elif 'L1L2' in config:
                kernel_regularizer =  keras.regularizers.l1_l2(
                    l1=config['L1L2'][0],
                    l2=config['L1L2'][1],
                )
                
            series.append(
                self.__get_dense(
                    out_nodes           = config["out_nodes"], 
                    act                 = config["act"],
                    kernel_regularizer  = kernel_regularizer
                )
            )
            
            # batchnorm (before dropout)
            if 'bn' in config:
                if config['bn'] is True:
                    # append bn one-by-one
                    series.append(self.__get_bn())
                    
            # dropout (after batchnorm)
            if 'p' in config:
                series.append(self.__get_dropout(config["p"]))
        
        # forward through series
        """ # OVERKILL
        return Sequential(series)
        """
        for layer in series:
            x = layer(x)
        return x

        
    # helpers start ---------------------------------
    # general
    def __get_bn(self):
        return BatchNormalization()
        
    def __get_act(self, name):
        """`name` is a string. eg. 'relu'"""
        return Activation(name)
    
    # for convs_seq
    def __get_conv(self, out_ch, z, padding, kernel_regularizer):
        """
        For "SAME" padding, if you use a stride of 1, 
        the layer's outputs will have the same spatial 
        dimensions as its inputs.
        """
        return Conv2D(out_ch, (z, z), padding=padding, 
                      strides=(1, 1), kernel_regularizer=kernel_regularizer)
    
    def __get_pool(self, z):
        return MaxPooling2D(pool_size=(z, z))
    
    # for fcs_Seq
    def __get_dense(self, out_nodes, act, kernel_regularizer):
        """out_nodes is int and act is string """
        return Dense(out_nodes, activation=act, kernel_regularizer=kernel_regularizer)
    
    def __get_dropout(self, p):
        """ p if float [0, 1]"""
        return Dropout(p)
    # helpers end ------------------------------------
    # ===========================================================
    # END: build_model helpers 
    # ===========================================================
# =======================================================================================
# END: build custom model based on args
# =======================================================================================
