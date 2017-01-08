# -*- coding:utf-8 -*-

import os
import sys
import argparse

import numpy as np
import pandas as pd
import tensorflow as tf

from models import BOWmodel, ABSmodel
import reuters_dataset

import config

pd.set_option('display.width', 1000)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--dataset_path', type=str, default=None)
args = parser.parse_args()


###################### vocabsizeは別のを書かなくちゃ ######################

dataset, dictionary = reuters_dataset.load_dataset(args.dataset_path)
list_batch = reuters_dataset.make_batch(dataset, dictionary, config.params)[: -1] ### とりあえず

#model = BOWmodel(config.params)
model = ABSmodel(config.params)
model.build_train_graph()
a
sess = tf.Session()
sess.run(tf.initialize_all_variables())

for i in range(config.params.epoch):
    print('epoch: %d'%i)
    
    for j, batch in enumerate(list_batch):
        print('  batch: %5d (/%5d)'%(j, len(list_batch)))
        x = np.array(list(batch['x_labels'].values)).astype(np.int32)
        y_c = np.array(list(batch['yc_labels'].values)).astype(np.int32)
        t = np.array(list(batch['t_label'].values)).astype(np.int32)
        t_onehot = np.zeros((config.params.batch_size, config.params.vocab_size))
        t_onehot[np.arange(config.params.batch_size), t] = 1
        p = np.array(list(batch['p'].values)).astype(np.float32)
        accuracy = model.train(sess, x, p, y_c, t_onehot)
        print('  accuracy: %f'%accuracy)
        
    print()
