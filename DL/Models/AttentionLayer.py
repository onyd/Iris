import tensorflow as tf
import tensorflow.keras.backend as K
from tensorflow.keras.layers import Conv2D, Conv2DTranspose, LayerNormalization
from tensorflow.python.keras.layers.core import Lambda, Dense


class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(name='att_weight',
                                 shape=(input_shape[-1], 1),
                                 initializer='normal')
        self.b = self.add_weight(name='att_bias',
                                 shape=(input_shape[1], 1),
                                 initializer='zeros')
        super().build(input_shape)

    def call(self, x, **kwargs):

        et = K.squeeze(K.tanh(K.dot(x, self.W) + self.b), axis=-1)
        at = K.softmax(et)
        at = K.expand_dims(at, axis=-1)
        output = x * at
        return K.sum(output, axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])


class MultiHeadAttention(tf.keras.layers.Layer):
    def __init__(self, d, n_heads):
        super().__init__()
        self.n_heads = n_heads
        self.d = d

        if d % n_heads != 0:
            raise ValueError("n_heads has to divide d !")

        self.Wq = tf.keras.layers.Dense(d, activation='relu')
        self.Wk = tf.keras.layers.Dense(d, activation='relu')
        self.Wv = tf.keras.layers.Dense(d, activation='relu')

        self.projection = tf.keras.layers.Dense(d, activation='relu')

    def split_over_heads(self, x, batch_size):
        """Split the last dimension into (num_heads, depth).
            Transpose the result such that the shape is (batch_size, num_heads, seq_len, depth)
        """

        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def scale_dot_product_attention(self, Q, K, V, mask):
        depth = tf.cast(tf.shape(K)[-1], tf.float32)
        QK_T = tf.matmul(Q, K, transpose_b=True)
        scaled = QK_T / tf.sqrt(depth)

        if mask is not None:
            scaled += mask * (-1e9)  # after softmax, masked coefs will be zero

        weights = tf.nn.softmax(scaled, axis=-1)
        attention = tf.matmul(weights, V)

        return attention

    def call(self, Q, K, V, mask):
        batch_size = tf.shape(Q)[0]

        Q = self.Wq(Q)
        K = self.Wk(K)
        V = self.Wv(V)

        Q = self.split_over_heads(Q, batch_size)
        K = self.split_over_heads(K, batch_size)
        V = self.split_over_heads(V, batch_size)

        scaled = self.scale_dot_product_attention(Q, K, V, mask)

        scaled = tf.transpose(scaled, perm=[0, 2, 1, 3])
        concat = tf.reshape(scaled, (batch_size, -1, self.d_model))

        attention = self.projection(concat)

        return attention


class AttentionCondenser(tf.keras.layers.Layer):
    def __init__(self, d_dim, filters, S):
        """
        Input: 4D tensor: (batch_size, w, h, c)
        params:
            S: int scale the dominance of Attention
        """
        super().__init__(self)
        self.S = S
        self.filters = filters
        self.d_dim = d_dim

    def build(self, input_shape):
        self.condensation = Lambda(
            lambda x: tf.reduce_max(x, axis=[3], keepdims=True))
        self.embeding1 = Dense(self.d_dim, activation='relu')
        self.embeding2 = Conv2D(self.filters, (1, 1),
                                strides=(1, 1),
                                activation='relu')

        self.expanding = Conv2DTranspose(input_shape[-1], (1, 1),
                                         strides=(1, 1),
                                         activation='relu')

    def call(self, x, **kwargs):
        """
        Condenser steps:
            condensation: that reduce inputs' dimension to (batch_size, w', h')
            embedding: a layer that reduce dimension size to produce an elbedding
            expension: a layer that return a tensor: (batch_size, w, h, filters)"""
        # Condensation mechanism
        condensated = self.condensation(x)  # (batch_size, w, h, 1)
        embedded = self.embeding1(condensated)  # (batch_size, w', h', filters)
        embedded = self.embeding2(embedded)  # (batch_size, w'', h'', filters)

        A = self.expanding(embedded)  # (batch_size, w, h, c)
        return self.S * x + A
