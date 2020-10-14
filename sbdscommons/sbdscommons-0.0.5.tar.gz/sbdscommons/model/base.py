class Model:
    """
    Model interface for each used data science model.
    Each model need to implement a @method: fit and a predict method
    """

    def fit(self, *args, **kwargs):
        raise NotImplementedError('The fit method needs to be implemented by each model')

    def predict(self, *args, **kwargs):
        raise NotImplementedError('The predict method needs to be implemented by each model')


class PrepInput:
    """
    PrepInput interface for each used data science model.
    Each PrepInput needs to implement fit, transform and fit_transform methods
    """

    def fit(self, *args, **kwargs):
        raise NotImplementedError('The fit method needs to be implemented by each model')

    def transform(self, *args, **kwargs):
        raise NotImplementedError('The transform method needs to be implemented by each model')

    def fit_transform(self, *args, **kwargs):
        raise NotImplementedError('The fit_transform method needs to be implemented by each model')
