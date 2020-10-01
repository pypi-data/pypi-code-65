# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2020 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

import tensorflow as tf

from ._base import (
    build_base_callback,
    build_empty_keras_callback,
    build_keras_callback,
    build_predictive_early_stopping_keras_callback,
)

BaseCallback = build_base_callback(tf.keras.callbacks.Callback)

PredictiveEarlyStoppingKerasCallback = build_predictive_early_stopping_keras_callback(
    BaseCallback
)

EmptyKerasCallback = build_empty_keras_callback(BaseCallback)

KerasCallback = build_keras_callback(BaseCallback)
