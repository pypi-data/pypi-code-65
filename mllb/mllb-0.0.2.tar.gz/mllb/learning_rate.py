"""
Learning rate class.
Used within the Neural Netork class
"""


class learning_rate_class:

    # Args:
    #     lr_value: (float) learning rate exp_value

    #     lr_increase: (float) value by which lr_value will be multiplied
    #                  with after every epoch of traning

    def __init__(self):
        self.lr_value = 1
        self.lr_increase = 1

    def initial(self, initial_learning_rate):

        """
        Set intial learning learning rate.
        If this functions isn't called, the default learning rate is 1.

        Args:
            initial_learning_rate: (float) set learning rate

        Return:
            --

        """

        self.lr_value = initial_learning_rate

    def multiply_after_epoch(self, product_value):

        """
        Set a value for which the learning rate will be multiplied after every
        epoch.

        Args:
            product_value: (float) value

        Return:
            --

        """

        self.lr_increase = product_value

    def exp_increase(self, exp_value):

        """
        Set an exp value for which the learning rate will be multiplied after every
        epoch.

        Args:
            product_value: (float) value

        Return:
            --

        """

        e = 2.7182818284590452353602874713527
        self.lr_increase = e**exp_value