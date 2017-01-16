# -*- coding: utf-8 -*-

import os
import sys
import argparse
import math
import time

import numpy as np
import pandas as pd
import tensorflow as tf

from models import ABSmodel
import dataset
import config

parser = argparse.ArgumentParser(description='')
parser.add_argument('--gpu', type=int, default=None)
parser.add_argument('--dataset_path', type=str)
parser.add_argument('--model_path', type=str)
args = parser.parse_args()

model_path = '../result/models/reuters/epoch10/model.ckpt'
dataset_path = '../data/dataset/reuters/train.csv'

dictionary_path = '../data/dataset/reuters/dictionary.pkl'
dictionary = reuters_dataset.load_dictionary(dictionary_path)
start_symbol_id = dictionary.token2id['<S>']
end_symbol_id = dictionary.token2id['EOS']
symbol_ids = {'<S>': start_symbol_id, 'EOS': end_symbol_id}
vocab_size = len(list(dictionary.iterkeys()))
config.params.vocab_size = vocab_size

dataset = reuters_dataset.str2list(reuters_dataset.load_dataset(dataset_path, 1, 100))

sess = tf.Session()
if args.gpu:
    with tf.device('/gpu:%d'%args.gpu):
        model = ABSmodel(config.params)
        model.rebuild_forward_graph(sess, model_path)
else:
    model = ABSmodel(config.params)
    model.rebuild_forward_graph(sess, model_path)

print(dataset)

for d in dataset:
    output = []
    x = np.array(list(d['x_labels'].values)).astype(np.int32)
    y_c = np.array([dictionary.token2id['<S>']] * config.params.window_size).astype(np.int32)
    for x in d['x_labels']:
        model.
