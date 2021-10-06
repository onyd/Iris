import tensorflow.keras.backend as K
import numpy as np
from tensorflow import keras
import tensorflow as tf


def exponent_neg_manhattan_distance(left, right):
    return K.exp(-K.sum(K.abs(left - right), axis=1, keepdims=True))


def cosine_distance(left, right):
    x_l = K.l2_normalize(left, axis=1)
    x_r = K.l2_normalize(right, axis=1)
    return K.sum(x_l * x_r, axis=1, keepdims=True)


class Siamese(keras.Model):
    def __init__(self, shared, distance_func=cosine_distance, **kwargs):
        super().__init__(**kwargs)

        self.shared = shared
        self.distance_layer = keras.layers.Lambda(
            function=lambda x: distance_func(x[0], x[1]),
            output_shape=lambda x: (x[0][0], 1))

    def call(self, input, *args, **kwargs):
        l, r = input[0], input[1]

        # Shared layers
        x_l = self.shared(l)
        x_r = self.shared(r)

        # Compute distance between two outputs
        return self.distance_layer([x_l, x_r])
