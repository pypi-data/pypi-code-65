"""Module containing models required for training
"""

from tensorflow.keras import regularizers
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model


def autoencoder(input_dim, bottleneck_dim):
    """Model for autoencoder

    Args:
        input_dim (int): Length of the input
        bottleneck_dim (int): Bottleneck layer size

    Returns:
        A dimension 3 tuple with, in order:
         - autoencoder_model (Model): Keras model for the complete autoencoder
         - encoder_model (Model): Keras model for the encoder
         - decoder_model (Model): Keras model for the decoder
    """

    x_input = Input(shape=(input_dim, ))
    l1_reg = 10e-5  # Regularisation value

    encoder_1 = Dense((input_dim + bottleneck_dim) // 2,
                      activation="relu",
                      activity_regularizer=regularizers.l1(l1_reg))(x_input)

    bottleneck = Dense(bottleneck_dim,
                       activation="relu",
                       activity_regularizer=regularizers.l1(l1_reg))(encoder_1)

    decoder_1 = Dense((input_dim + bottleneck_dim) // 2,
                      activation="relu")(bottleneck)

    fuzzy_out = Dense(input_dim, activation="sigmoid")(decoder_1)

    autoencoder_model = Model(x_input, fuzzy_out)
    encoder_model = Model(x_input, bottleneck)

    encoded_input = Input(shape=(bottleneck_dim, ))
    decoder_layer0, decoder_layer1 = autoencoder_model.layers[-2:]

    decoder_model = Model(encoded_input,
                          decoder_layer1(decoder_layer0(encoded_input)))
    return autoencoder_model, encoder_model, decoder_model


def custom_autoencoder(layer_dims, activations=None):
    """Custom model for autoencoder

    Args:
        layer_dims (list): List of dimensions of each layer, assumed
            until the central layer of an auto-encoder (symetrical
            architecture).

        activations (list): List of activation for each layer. Note that the
            number of elements should be exactly equal to
            (2 * len(layer_dims) - 2). The activation values can be valid
            strings or tf activation functions. Default activation for all
            layers is ReLU.

         layer_dims[0]
            o                            o
            o    o  layer_dims[-1]  o    o
            o    o       o          o    o
            o    o       o          o    o
            o    o                  o    o
            o activations[0]             o
                                       activations[-1]

    Raises:
        ValueError: When layer_dims is not of length greater than or equal to 2

    Returns:
        A dimension 3 tuple with, in order:
         - autoencoder_model (Model): Keras model for the complete autoencoder
         - encoder_model (Model): Keras model for the encoder
         - decoder_model (Model): Keras model for the decoder
    """

    if not isinstance(layer_dims, list):
        raise TypeError("Expected {} got {} for layer_dims".format(
            list, type(layer_dims)))

    if not len(layer_dims) >= 2:
        raise ValueError("Expected layer_dims to have 2 or more elements!")

    if not all(isinstance(x, int) for x in layer_dims):
        raise TypeError("Expected each layer_dim in layer_dims to be int")

    # Number of activations required

    n_activations = 2 * len(layer_dims) - 2

    if activations is None:
        activations = ["relu"] * n_activations

    if not isinstance(activations, list):
        raise TypeError("Expected {} got {} for activations".format(
            list, type(activations)))

    if not len(activations) == n_activations:
        raise ValueError(
            "activations not of expected size. Got {} instead of {}".format(
                len(activations), n_activations))

    x_input = Input(shape=(layer_dims[0], ))
    autoencoder_out = x_input
    l1_reg = 10e-5  # Regularisation value

    for (layer_dim, activation) in zip(layer_dims[1:],
                                       activations[:len(layer_dims) - 1]):
        # Encoding layers
        autoencoder_out = Dense(
            layer_dim,
            activation=activation,
            activity_regularizer=regularizers.l1(l1_reg))(autoencoder_out)

    bottleneck = autoencoder_out
    encoded_input = Input(shape=(layer_dims[-1], ))

    for (layer_dim, activation) in zip(reversed(layer_dims[1:-1]),
                                       activations[len(layer_dims) - 1:-1]):
        # Decoding layers
        autoencoder_out = Dense(layer_dim,
                                activation=activation)(autoencoder_out)

    fuzzy_out = Dense(layer_dims[0],
                      activation=activations[-1])(autoencoder_out)

    autoencoder_model = Model(x_input, fuzzy_out)
    encoder_model = Model(x_input, bottleneck)

    decoded_out = get_decoded_out(autoencoder_model, encoded_input,
                                  len(layer_dims) - 1)

    decoder_model = Model(encoded_input, decoded_out)

    return autoencoder_model, encoder_model, decoder_model


def get_decoded_out(autoencoder_model, encoded_input, n_layers):
    """Extract the last few layers from the autoencoder to create the decoder.
    This helps train both at the same time.

    Args:
        autoencoder_model (Model): Model of the autoencoder
        encoded_input (Input): Input layer of the decoder
        n_layers (int): Number of layers to extract from autoencoder

    Returns:
        decoder_model (Model): Model of the decoder
    """

    decoded_out = encoded_input
    for layer in autoencoder_model.layers[-n_layers:]:
        decoded_out = layer(decoded_out)

    return decoded_out
