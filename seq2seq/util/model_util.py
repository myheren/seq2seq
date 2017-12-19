import numpy as np
import tensorflow as tf

__all__ = ["convert_decoding", "convert_embedding", "create_embedding", "create_rnn_cell", "create_rnn_single_cell"]

def convert_decoding(decoding_list, eos):
    eos = eos.encode("utf-8")
    if eos in decoding_list:
        decoding_list = decoding_list[:decoding_list.index(eos)]
    decoding = b" ".join(decoding_list)
    
    return decoding

def convert_embedding(embedding_lookup):
    if embedding_lookup is not None:
        embedding = [v for k,v in embedding_lookup.items()]
    else:
        embedding = None
    
    return embedding

def create_embedding(vocab_size,
                     embedding_dim,
                     pretrained=False):
    """create embedding with pre-trained embedding or initializer"""
    if pretrained is True:
        embedding = tf.get_variable("embedding", shape=[vocab_size, embedding_dim], dtype=tf.float32,
            initializer=tf.zeros_initializer, trainable=False)
        embedding_placeholder = tf.placeholder(name="embedding_placeholder",
                                               shape=[vocab_size, embedding_dim], dtype=tf.float32)
        embedding = embedding.assign(embedding_placeholder)
    else:
        embedding = tf.get_variable("embedding", shape=[vocab_size, embedding_dim], dtype=tf.float32)
        embedding_placeholder = None
    
    return embedding, embedding_placeholder

def create_rnn_single_cell(unit_dim,
                           unit_type,
                           activation,
                           forget_bias,
                           residual_connect,
                           drop_out):
    """create single rnn cell"""
    if activation == "tanh":
        activation_function = tf.nn.tanh
    elif activation == "relu":
        activation_function = tf.nn.relu
    elif activation == "leaky_relu":
        activation_function = tf.nn.leaky_relu
    elif activation == "sigmoid":
        activation_function = tf.nn.sigmoid
    else:
        activation_function = None
    
    if unit_type == "lstm":
        single_cell = tf.contrib.rnn.BasicLSTMCell(num_units=unit_dim,
            activation=activation_function, forget_bias=forget_bias)
    elif unit_type == "peephole_lstm":
        single_cell = tf.contrib.rnn.LSTMCell(num_units=unit_dim,
            use_peepholes=True, activation=activation_function, forget_bias=forget_bias)
    elif unit_type == "layer_norm_lstm":
        single_cell = tf.contrib.rnn.LayerNormBasicLSTM(num_units=unit_dim,
            layer_norm=True, activation=activation_function, forget_bias=forget_bias)
    elif unit_type == "gru":
        single_cell = tf.contrib.rnn.GRUCell(num_units=unit_dim, activation=activation_function)
    else:
        raise ValueError("unsupported unit type {0}".format(unit_type))
    
    if drop_out > 0.0:
        single_cell = tf.contrib.rnn.DropoutWrapper(cell=single_cell, input_keep_prob=1.0-drop_out)
        
    if residual_connect == True:
        single_cell = tf.contrib.rnn.ResidualWrapper(cell=single_cell)
    
    return single_cell

def create_rnn_cell(num_layer,
                    unit_dim,
                    unit_type,
                    activation,
                    forget_bias,
                    residual_connect,
                    drop_out):
    """create rnn cell"""
    if num_layer > 1:
        cell_list = []
        for i in range(num_layer):
            single_cell = create_rnn_single_cell(unit_dim=unit_dim, unit_type=unit_type, activation=activation,
                forget_bias=forget_bias, residual_connect=residual_connect, drop_out=drop_out)
            cell_list.append(single_cell)
        cell = tf.contrib.rnn.MultiRNNCell(cell_list)
    else:
        cell = create_rnn_single_cell(unit_dim=unit_dim, unit_type=unit_type, activation=activation,
            forget_bias=forget_bias, residual_connect=residual_connect, drop_out=drop_out)
    
    return cell
