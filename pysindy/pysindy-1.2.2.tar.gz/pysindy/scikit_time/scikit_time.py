"""
`Scikit-time <https://scikit-time.github.io/>`_ wrapper interface for PySINDy.
"""
from sklearn.pipeline import Pipeline
from sklearn.utils.validation import check_is_fitted

from ..pysindy import SINDy


class SINDyEstimator(SINDy):
    """
    Implementation of SINDy conforming to the API of a Scikit-time
    `Estimator \
    <https://scikit-time.github.io/api/generated/sktime.base.Estimator.html>`_.

    Parameters
    ----------
    optimizer : optimizer object, optional
        Optimization method used to fit the SINDy model. This must be an object
        extending the ``sindy.optimizers.BaseOptimizer`` class. Default is
        sequentially thresholded least squares with a threshold of 0.1.

    feature_library : feature library object, optional
        Feature library object used to specify candidate right-hand side features.
        This must be an object extending the
        ``sindy.feature_library.BaseFeatureLibrary`` class.
        Default is polynomial features of degree 2.

    differentiation_method : differentiation object, optional
        Method for differentiating the data. This must be an object extending
        the ``sindy.differentiation_methods.BaseDifferentiation`` class.
        Default is centered difference.

    feature_names : list of string, length n_input_features, optional
        Names for the input features (e.g. ``['x', 'y', 'z']``). If None, will use
        ``['x0', 'x1', ...]``.

    t_default : float, optional (default 1)
        Default value for the time step.

    discrete_time : boolean, optional (default False)
        If True, dynamical system is treated as a map. Rather than predicting
        derivatives, the right hand side functions step the system forward by
        one time step. If False, dynamical system is assumed to be a flow
        (right-hand side functions predict continuous time derivatives).

    Attributes
    ----------
    model : sklearn.multioutput.MultiOutputRegressor object
        The fitted SINDy model.

    n_input_features_ : int
        The total number of input features.

    n_output_features_ : int
        The total number of output features. This number is a function of
        ``self.n_input_features`` and the feature library being used.

    """

    def __init__(
        self,
        optimizer=None,
        feature_library=None,
        differentiation_method=None,
        feature_names=None,
        t_default=1,
        discrete_time=False,
    ):
        super(SINDyEstimator, self).__init__(
            optimizer=optimizer,
            feature_library=feature_library,
            differentiation_method=differentiation_method,
            feature_names=feature_names,
            t_default=t_default,
            discrete_time=discrete_time,
        )
        self._model = None

    def fit(self, x, **kwargs):
        """
        Fit the SINDyEstimator to data, learning a dynamical systems model
        for the data.

        Parameters
        ----------
        x: array-like or list of array-like, shape (n_samples, n_input_features)
            Training data. If training data contains multiple trajectories,
            x should be a list containing data for each trajectory. Individual
            trajectories may contain different numbers of samples.

        **kwargs: dict, optional
            Optional keyword arguments to pass to the ``SINDy.fit`` method.

        Returns
        -------
        self: fitted ``SINDyEstimator`` instance
        """
        super(SINDyEstimator, self).fit(x, **kwargs)
        self._model = SINDyModel(
            feature_library=self.model.steps[0][1],
            optimizer=self.model.steps[1][1],
            feature_names=self.feature_names,
            t_default=self.t_default,
            discrete_time=self.discrete_time,
            n_control_features_=self.n_control_features_,
        )
        return self

    def fetch_model(self):
        """
        Yields the estimated model. Can be none if ``fit`` was not called.

        Returns
        -------
        model: ``SINDyModel`` or None
            The estimated SINDy model or none
        """
        return self._model

    @property
    def has_model(self):
        """Property reporting whether this estimator contains an estimated
        model. This assumes that the model is initialized with ``None`` otherwise.

        :type: bool
        """
        return self._model is not None


class SINDyModel(SINDy):
    """
    Implementation of SINDy conforming to the API of a Scikit-time
    `Model <https://scikit-time.github.io/api/generated/sktime.base.Model.html>`_.

    The model is represented as a Scikit-learn pipeline object with two steps:
    1. Map the raw input data to nonlinear features according to the selected
    ``feature_library``
    2. Multiply the nonlinear features with a coefficient matrix encapuslated
    in ``optimizer``.

    This class expects the feature library and optimizer to already be fit
    with a ``SINDyEstimator``. It is best to instantiate a ``SINDyModel``
    object via the ``SINDyEstimator.fetch_model()`` rather than calling
    the ``SINDyModel`` constructor directly.

    Parameters
    ----------
    optimizer : optimizer object
        Optimization method used to fit the SINDy model. This must be an
        (already fit) object extending the ``pysindy.optimizers.BaseOptimizer``
        class.

    feature_library : feature library object
        Feature library object used to specify candidate right-hand side features.
        This must be an (already fit) object extending the
        ``pysindy.feature_library.BaseFeatureLibrary`` class.

    differentiation_method : differentiation object
        Method for differentiating the data. This must be an object extending
        the ``pysindy.differentiation_methods.BaseDifferentiation`` class.
        Default is centered difference.

    feature_names : list of string, length n_input_features, optional
        Names for the input features (e.g. ``['x', 'y', 'z']``). If None, will use
        ``['x0', 'x1', ...]``.

    t_default : float, optional (default 1)
        Default value for the time step.

    discrete_time : boolean, optional (default False)
        If True, dynamical system is treated as a map. Rather than predicting
        derivatives, the right hand side functions step the system forward by
        one time step. If False, dynamical system is assumed to be a flow
        (right-hand side functions predict continuous time derivatives).

    Attributes
    ----------
    model : sklearn.multioutput.MultiOutputRegressor object
        The fitted SINDy model.

    n_input_features_ : int
        The total number of input features.

    n_output_features_ : int
        The total number of output features. This number is a function of
        ``self.n_input_features`` and the feature library being used.
    """

    def __init__(
        self,
        feature_library,
        optimizer,
        feature_names=None,
        t_default=1,
        discrete_time=False,
        n_control_features_=0,
    ):
        super(SINDyModel, self).__init__(
            feature_library=feature_library,
            optimizer=optimizer,
            feature_names=feature_names,
            t_default=t_default,
            discrete_time=discrete_time,
        )
        self.n_control_features_ = n_control_features_

        check_is_fitted(feature_library)
        check_is_fitted(optimizer)

        steps = [("features", feature_library), ("model", optimizer)]
        self.model = Pipeline(steps)

        self.n_input_features_ = self.model.steps[0][1].n_input_features_
        self.n_output_features_ = self.model.steps[0][1].n_output_features_

    def copy(self):
        """Makes a deep copy of this model.

        Returns
        -------
        copy: SINDyModel
            A new copy of this model.
        """
        import copy

        return copy.deepcopy(self)
