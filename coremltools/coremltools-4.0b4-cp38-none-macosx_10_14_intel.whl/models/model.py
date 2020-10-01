# Copyright (c) 2017, Apple Inc. All rights reserved.
#
# Use of this source code is governed by a BSD-3-clause license that can be
# found in the LICENSE.txt file or at https://opensource.org/licenses/BSD-3-Clause
import json as _json
import os as _os
import tempfile as _tempfile
import warnings as _warnings
from copy import deepcopy as _deepcopy
from six import string_types as _string_types

from .utils import _has_custom_layer as _has_custom_layer
from .utils import load_spec as _load_spec
from .utils import _macos_version as _macos_version
from .utils import save_spec as _save_spec
from ..proto import Model_pb2 as _Model_pb2

_MLMODEL_FULL_PRECISION = "float32"
_MLMODEL_HALF_PRECISION = "float16"
_MLMODEL_QUANTIZED = "quantized_model"

_VALID_MLMODEL_PRECISION_TYPES = [
    _MLMODEL_FULL_PRECISION,
    _MLMODEL_HALF_PRECISION,
    _MLMODEL_QUANTIZED,
]

# Linear quantization
_QUANTIZATION_MODE_LINEAR_QUANTIZATION = "_linear_quantization"
# Linear quantization represented as a lookup table
_QUANTIZATION_MODE_LOOKUP_TABLE_LINEAR = "_lookup_table_quantization_linear"
# Lookup table quantization generated by K-Means
_QUANTIZATION_MODE_LOOKUP_TABLE_KMEANS = "_lookup_table_quantization_kmeans"
# Custom lookup table quantization
_QUANTIZATION_MODE_CUSTOM_LOOKUP_TABLE = "_lookup_table_quantization_custom"
# Dequantization
_QUANTIZATION_MODE_DEQUANTIZE = "_dequantize_network"  # used for testing
# Symmetric linear quantization
_QUANTIZATION_MODE_LINEAR_SYMMETRIC = "_linear_quantization_symmetric"

_SUPPORTED_QUANTIZATION_MODES = [
    _QUANTIZATION_MODE_LINEAR_QUANTIZATION,
    _QUANTIZATION_MODE_LOOKUP_TABLE_LINEAR,
    _QUANTIZATION_MODE_LOOKUP_TABLE_KMEANS,
    _QUANTIZATION_MODE_CUSTOM_LOOKUP_TABLE,
    _QUANTIZATION_MODE_DEQUANTIZE,
    _QUANTIZATION_MODE_LINEAR_SYMMETRIC,
]

_LUT_BASED_QUANTIZATION = [
    _QUANTIZATION_MODE_LOOKUP_TABLE_LINEAR,
    _QUANTIZATION_MODE_LOOKUP_TABLE_KMEANS,
    _QUANTIZATION_MODE_CUSTOM_LOOKUP_TABLE,
]

_METADATA_VERSION = "com.github.apple.coremltools.version"
_METADATA_SOURCE = "com.github.apple.coremltools.source"


class _FeatureDescription(object):
    def __init__(self, fd_spec):
        self._fd_spec = fd_spec

    def __repr__(self):
        return "Features(%s)" % ",".join(map(lambda x: x.name, self._fd_spec))

    def __len__(self):
        return len(self._fd_spec)

    def __getitem__(self, key):
        for f in self._fd_spec:
            if key == f.name:
                return f.shortDescription
        raise KeyError("No feature with name %s." % key)

    def __contains__(self, key):
        for f in self._fd_spec:
            if key == f.name:
                return True
        return False

    def __setitem__(self, key, value):
        for f in self._fd_spec:
            if key == f.name:
                f.shortDescription = value
                return
        raise AttributeError("No feature with name %s." % key)

    def __iter__(self):
        for f in self._fd_spec:
            yield f.name


def _get_proxy_and_spec(filename, use_cpu_only=False):
    try:
        from ..libcoremlpython import _MLModelProxy
    except Exception:
        _MLModelProxy = None

    filename = _os.path.expanduser(filename)
    specification = _load_spec(filename)

    if _MLModelProxy:

        # check if the version is supported
        engine_version = _MLModelProxy.maximum_supported_specification_version()
        if specification.specificationVersion > engine_version:
            # in this case the specification is a newer kind of .mlmodel than this
            # version of the engine can support so we'll not try to have a proxy object
            return (None, specification, None)

        try:
            return (_MLModelProxy(filename, use_cpu_only), specification, None)
        except RuntimeError as e:
            _warnings.warn(
                "You will not be able to run predict() on this Core ML model."
                + " Underlying exception message was: "
                + str(e),
                RuntimeWarning,
            )
            return (None, specification, e)

    return (None, specification, None)


class MLModel(object):
    """
    This class defines the minimal interface to a CoreML object in Python.

    At a high level, the protobuf specification consists of:

    - Model description: Encodes names and type information of the inputs and outputs to the model.
    - Model parameters: The set of parameters required to represent a specific instance of the model.
    - Metadata: Information about the origin, license, and author of the model.

    With this class, you can inspect a CoreML model, modify metadata, and make
    predictions for the purposes of testing (on select platforms).

    Examples
    --------
    .. sourcecode:: python

        # Load the model
        >>> model =  MLModel('HousePricer.mlmodel')

        # Set the model metadata
        >>> model.author = 'Author'
        >>> model.license = 'BSD'
        >>> model.short_description = 'Predicts the price of a house in the Seattle area.'

        # Get the interface to the model
        >>> model.input_description
        >>> model.output_description

        # Set feature descriptions manually
        >>> model.input_description['bedroom'] = 'Number of bedrooms'
        >>> model.input_description['bathrooms'] = 'Number of bathrooms'
        >>> model.input_description['size'] = 'Size (in square feet)'

        # Set
        >>> model.output_description['price'] = 'Price of the house'

        # Make predictions
        >>> predictions = model.predict({'bedroom': 1.0, 'bath': 1.0, 'size': 1240})

        # Get the spec of the model
        >>> model.spec

        # Save the model
        >>> model.save('HousePricer.mlmodel')

    See Also
    --------
    predict
    """

    def __init__(self, model, useCPUOnly=False):
        """
        Construct an MLModel from a .mlmodel

        Parameters
        ----------
        model: str or Model_pb2
            If a string is given it should be the location of the .mlmodel to load.

        useCPUOnly: bool
            Set to true to restrict loading of model on CPU Only. Defaults to False.

        Examples
        --------
        >>> loaded_model = MLModel('my_model_file.mlmodel')
        """

        if isinstance(model, _string_types):
            self.__proxy__, self._spec, self._framework_error = _get_proxy_and_spec(
                model, useCPUOnly
            )
        elif isinstance(model, _Model_pb2.Model):
            filename = _tempfile.mktemp(suffix=".mlmodel")
            _save_spec(model, filename)
            self.__proxy__, self._spec, self._framework_error = _get_proxy_and_spec(
                filename, useCPUOnly
            )
            try:
                _os.remove(filename)
            except OSError:
                pass
        else:
            raise TypeError(
                "Expected model to be a .mlmodel file or a Model_pb2 object"
            )

        self._input_description = _FeatureDescription(self._spec.description.input)
        self._output_description = _FeatureDescription(self._spec.description.output)

    @property
    def short_description(self):
        return self._spec.description.metadata.shortDescription

    @short_description.setter
    def short_description(self, short_description):
        self._spec.description.metadata.shortDescription = short_description

    @property
    def input_description(self):
        return self._input_description

    @property
    def output_description(self):
        return self._output_description

    @property
    def user_defined_metadata(self):
        return self._spec.description.metadata.userDefined

    @property
    def author(self):
        return self._spec.description.metadata.author

    @author.setter
    def author(self, author):
        self._spec.description.metadata.author = author

    @property
    def license(self):
        return self._spec.description.metadata.license

    @license.setter
    def license(self, license):
        self._spec.description.metadata.license = license

    @property
    def version(self):
        return self._spec.description.metadata.versionString

    @version.setter
    def version(self, version_string):
        self._spec.description.metadata.versionString = version_string

    def __repr__(self):
        return self._spec.description.__repr__()

    def __str__(self):
        return self.__repr__()

    def save(self, filename):
        """
        Save the model to a .mlmodel format.

        Parameters
        ----------
        filename: str
            Target filename for the model.

        See Also
        --------
        coremltools.utils.load_model

        Examples
        --------
        >>> model.save('my_model_file.mlmodel')
        >>> loaded_model = MLModel('my_model_file.mlmodel')
        """
        filename = _os.path.expanduser(filename)
        _save_spec(self._spec, filename)

    def get_spec(self):
        """
        Get a deep copy of the protobuf specification of the model.

        Returns
        -------
        model: Model_pb2
            Protobuf specification of the model.

        Examples
        ----------
        >>> spec = model.get_spec()
        """
        return _deepcopy(self._spec)

    def predict(self, data, useCPUOnly=False, **kwargs):
        """
        Return predictions for the model. The kwargs gets passed into the
        model as a dictionary.

        Parameters
        ----------
        data: dict[str, value]
            Dictionary of data to make predictions from where the keys are
            the names of the input features.

        useCPUOnly: bool
            Set to true to restrict computation to use only the CPU. Defaults to False.

        Returns
        -------
        out: dict[str, value]
            Predictions as a dictionary where each key is the output feature
            name.

        Examples
        --------
        >>> data = {'bedroom': 1.0, 'bath': 1.0, 'size': 1240}
        >>> predictions = model.predict(data)
        """

        if self.__proxy__:
            return self.__proxy__.predict(data, useCPUOnly)
        else:
            if _macos_version() < (10, 13):
                raise Exception(
                    "Model prediction is only supported on macOS version 10.13 or later."
                )

            try:
                from ..libcoremlpython import _MLModelProxy
            except Exception as e:
                print("exception loading model proxy: %s\n" % e)
                _MLModelProxy = None
            except:
                print("exception while loading model proxy.\n")
                _MLModelProxy = None

            if not _MLModelProxy:
                raise Exception(
                    "Unable to load CoreML.framework. Cannot make predictions."
                )
            elif (
                _MLModelProxy.maximum_supported_specification_version()
                < self._spec.specificationVersion
            ):
                engineVersion = _MLModelProxy.maximum_supported_specification_version()
                raise Exception(
                    "The specification has version "
                    + str(self._spec.specificationVersion)
                    + " but the Core ML framework version installed only supports Core ML model specification version "
                    + str(engineVersion)
                    + " or older."
                )
            elif _has_custom_layer(self._spec):
                raise Exception(
                    "This model contains a custom neural network layer, so predict is not supported."
                )
            else:
                if self._framework_error:
                    raise self._framework_error
                else:
                    raise Exception(
                        "Unable to load CoreML.framework. Cannot make predictions."
                    )
