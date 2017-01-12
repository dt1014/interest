# -*- coding:utf-8 -*-

import os
import sys
import argparse
import time

import numpy as np
import pandas as pd
import tensorflow as tf

from models import ABSmodel
import reuters_dataset

import config

# この関数とxのパディングの関数をmake_batchにある並列の中に入れる
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
parser.add_argument('--gpu', type=int, default=None)
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

print('vocab size: ', vocab_size)

num_lines = sum(1 for line in open(args.dataset_path))
read_rows = 10000
n_loop_for_read = int((num_lines-1)/read_rows+1)
print('num_lines: ', num_lines)
print('n_loop_for_read_row:', n_loop_for_read)


if args.gpu:
    with tf.device('/gpu:%d'%args.gpu):
        model = ABSmodel(config.params)
        model.build_train_graph()
else:
    model = ABSmodel(config.params)
    model.build_train_graph()
        
sess = tf.Session()
sess.run(tf.global_variables_initializer())
save_vals = {'E': model.E,
             'U_w': model.U_w,
             'U_b': model.U_b,
             'V_w': model.V_w,
             'V_b': model.V_b,
             'W_w': model.W_w,
             'W_b': model.W_b,
             'G': model.G,
             'F': model.F,
             'P': model.P}
saver = tf.train.Saver(save_vals)

# help(saver.save)

for i in range(config.params.epoch):
    print('epoch: %d'%(i+1))
    accuracy = 0
    for k in range(n_loop_for_read):
        l = 0
        dataset = reuters_dataset.load_dataset(args.dataset_path, k*read_rows+1, read_rows)
        for j, n_batch, batch in reuters_dataset.make_batch(dataset, symbol_ids, config.params):
            sys.stdout.write('\r  batch: %5d (/%5d)'%(j+1, n_batch))
            x = np.array(list(batch['x_labels'].values)).astype(np.int32)
            y_c = np.array(list(batch['yc_labels'].values)).astype(np.int32)
            t = np.array(list(batch['t_label'].values)).astype(np.int32)
            t_onehot = np.zeros((config.params.batch_size, config.params.vocab_size))
            t_onehot[np.arange(config.params.batch_size), t] = 1
            accuracy += model.train(sess, x, y_c, t_onehot)
            l += 1
        print()
    print('  accuracy: %f'%(accuracy/l))      

    
    if (i+1) % 5 == 0:
        save_dir = args.save_dir+'/epoch%d'%(i+1)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_path = saver.save(sess, save_dir+'/model.ckpt')
        print('  Model saved in file: %s' % save_path)

