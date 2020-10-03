import tensorflow as tf


@tf.function
def complex_to_channels(x):
    real = tf.math.real(x)
    imag = tf.math.imag(x)
    zed = tf.stack([real, imag], axis=-1)
    return zed


@tf.function
def channels_to_complex(x):
    real = x[..., 0]
    imag = x[..., 1]
    result = tf.complex(real, imag)
    return result
