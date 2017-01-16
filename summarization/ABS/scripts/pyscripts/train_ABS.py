# -*- coding:utf-8 -*-

import os
import sys
import argparse
import pickle
import time

import numpy as np
import pandas as pd
import tensorflow as tf

from models import ABSmodel
import dataset

import config

pd.set_option('display.width', 1000)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--gpu', type=int, default=None)
parser.add_argument('--batch_path', type=str)
parser.add_argument('--dictionary_path', type=str)
parser.add_argument('--save_dir', type=str)
args = parser.parse_args()

dictionary = dataset.load_dictionary(args.dictionary_path)
vocab_size = len(list(dictionary.keys()))
config.params.vocab_size = vocab_size
del dictionary

print('vocab size: ', vocab_size)

if args.gpu:
    with tf.device('/gpu:%d'%args.gpu):
        model = ABSmodel(config.params)
        model.build_train_graph()
else:
    model = ABSmodel(config.params)
    model.build_train_graph()

tf.set_random_seed(0)
sess = tf.Session()
sess.run(tf.global_variables_initializer())
# sess.run(tf.inittialize_all_variables()) # for lower tf version
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

log_dir = args.save_dir+'/log'
log_path = log_dir+'/train_log.csv'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
with open(log_path, 'w') as f_log:
    f_log.write('epoch,accuracy\n')

### dataのload  ### 
with open(args.batch_path, 'rb') as f_batch:
    list_batch = pickle.load(f_batch)

for i in range(config.params.epoch):
    print('epoch: %d'%(i+1))
    accuracy = 0
    for j, batch in enumerate(list_batch):
        print(batch)
        sys.stdout.write('\r  batch: %5d (/%5d)'%(j+1, len(list_batch)))
        x = np.array(list(batch['x_labels'].values)).astype(np.int32)
        y_c = np.array(list(batch['yc_labels'].values)).astype(np.int32)
        t = np.array(list(batch['t_label'].values)).astype(np.int32)
        t_onehot = np.zeros((config.params.batch_size, config.params.vocab_size))
        t_onehot[np.arange(config.params.batch_size), t] = 1
        accuracy += model.train(sess, x, y_c, t_onehot)
    print()
    print('  accuracy: %f'%(accuracy/(j+1)))      
    train_log.append('%d,%f'%(i, accuracy/(j+1)))
    
    save_dir = args.save_dir+'/epoch%d'%(i+1)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = saver.save(sess, save_dir+'/model.ckpt')
    print('  Model saved in file: %s' % save_path)


