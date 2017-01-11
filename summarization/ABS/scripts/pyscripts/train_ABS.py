# -*- coding:utf-8 -*-

import os
import sys
import argparse
import time

import numpy as np
import pandas as pd
import tensorflow as tf

from models import BOWmodel, ABSmodel
import reuters_dataset

import config

def make_smoothed_x(x, vocab_size):
    start = time.time()
    smoothed_x = np.zeros((config.params.batch_size, x.shape[1], vocab_size))
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            for k in range(-config.params.smoothing_window_size, config.params.smoothing_window_size+1):
                smoothed_x[i][j][x[i][min(x.shape[1]-1, max(0, j+k))]] += 1        
    return smoothed_x

pd.set_option('display.width', 1000)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--dataset_path', type=str)
parser.add_argument('--dictionary_path', type=str)
parser.add_argument('--save_dir', type=str)
args = parser.parse_args()

# dataset = reuters_dataset.load_dataset(args.dataset_path)
# list_batch = reuters_dataset.make_batch(dataset, dictionary, config.params)[: -1]#[: 10] ### とりあえず

dictionary = reuters_dataset.load_dictionary(args.dictionary_path)
start_symbol_id = dictionary.token2id['<S>']
end_symbol_id = dictionary.token2id['EOS']
symbol_ids = {'<S>': start_symbol_id, 'EOS': end_symbol_id}
vocab_size = len(list(dictionary.iterkeys()))
config.params.vocab_size = vocab_size
del dictionary

seed = 0
num_lines = sum(1 for line in open(args.dataset_path))
read_rows = 1000
n_loop_for_row = int((num_lines-1)/read_rows+1)
print(num_lines)
print(n_loop_for_row)

with tf.device('/gpu:2'):
    model = ABSmodel(config.params)
    model.build_train_graph()

sess = tf.Session()
sess.run(tf.initialize_all_variables())
saver = tf.train.Saver()

# for i in range(config.params.epoch):
#     print('epoch: %d'%(i+1))
#     accuracy = 0
#     for j, batch in enumerate(list_batch):
#         sys.stdout.write('\r  batch: %5d (/%5d)'%(j+1, len(list_batch)))
#         x = np.array(list(batch['x_labels'].values)).astype(np.int32)
#         y_c = np.array(list(batch['yc_labels'].values)).astype(np.int32)
#         t = np.array(list(batch['t_label'].values)).astype(np.int32)
#         t_onehot = np.zeros((config.params.batch_size, config.params.vocab_size))
#         t_onehot[np.arange(config.params.batch_size), t] = 1
#         smoothed_x = make_smoothed_x(x, config.params.vocab_size)
        
#         accuracy += model.train(sess, x, smoothed_x, y_c, t_onehot)
#     print()
#     print('accuracy: %f'%(accuracy/(j+1)))      

#     #if (i+1) % 5 == 0:
#     save_path = saver.save(sess, args.save_dir+'/model_epoch%d.ckpt'%(i+1))
#     print('Model saved in file: %s' % save_path)

for i in range(config.params.epoch):
    print('epoch: %d'%(i+1))
    accuracy = 0
    for k in range(n_loop_for_row):
        l = 0
        dataset = reuters_dataset.load_dataset(args.dataset_path, k*read_rows+1, read_rows)
        for j, n_slice_data, batch in reuters_dataset.make_batch(dataset, symbol_ids, config.params, seed):
            sys.stdout.write('\r  j_sentence: %5d (/%5d)'%(j+1, n_slice_data))
            x = np.array(list(batch['x_labels'].values)).astype(np.int32)
            y_c = np.array(list(batch['yc_labels'].values)).astype(np.int32)
            t = np.array(list(batch['t_label'].values)).astype(np.int32)
            t_onehot = np.zeros((config.params.batch_size, config.params.vocab_size))
            t_onehot[np.arange(config.params.batch_size), t] = 1
            smoothed_x = make_smoothed_x(x, config.params.vocab_size)
            accuracy += model.train(sess, x, smoothed_x, y_c, t_onehot)
            l += 1
        print()
    print('accuracy: %f'%(accuracy/l))      

    seed += 1
    
    if (i+1) % 5 == 0:
        save_path = saver.save(sess, args.save_dir+'/model_epoch%d.ckpt'%(i+1))
        print('Model saved in file: %s' % save_path)

