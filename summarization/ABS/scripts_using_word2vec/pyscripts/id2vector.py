# -*- coding:utf-8 -*-

import os
import sys
import argparse
import pickle
import time
from multiprocessing import Pool

from gensim.models import Word2Vec
import numpy as np
import pandas as pd

import dataset

import config

def make_id_vector_dic(w2v_model, id2token, vocab_size):
    id_corpus = list(range(vocab_size))
    dictionary = {}
    for word_id in id_corpus:
        if id2token[word_id] == '<S>':
            dictionary[word_id] = w2v_model['＾']
        elif id2token[word_id] == '<EOS>':
            dictionary[word_id] = w2v_model['##']
        else:
            try:
                dictionary[word_id] = w2v_model[id2token[word_id]]
            except KeyError:
                dictionary[word_id] =  w2v_model['[]']
    return dictionary

def convert_batch(batch, id_vec_dic):
    def func(arr):
        return np.array([[id_vec_dic[a] for a in b] for b in arr])
    x = np.array(list(batch['x_labels'].values)).astype(np.int32)
    y_c = np.array(list(batch['yc_labels'].values)).astype(np.int32)
    vector_x = func(x)
    vector_y_c = func(y_c)
    t = np.array(list(batch['t_label'].values)).astype(np.int32)
    t_onehot = np.zeros((config.params.batch_size, config.params.vocab_size))
    t_onehot[np.arange(config.params.batch_size), t] = 1
    return {'x': vector_x, 'y_c': vector_y_c, 't_onehot': t_onehot}

def mp_func(list_batch):
    list_batch_vector = []
    for k, batch in enumerate(list_batch):
        list_batch_vector.append(convert_batch(batch), id_vec_dic)
    return list_batch_vector


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--batch_path', type=str)
    parser.add_argument('--dictionary_path', type=str)
    parser.add_argument('--w2v_path', type=str)
    parser.add_argument('--save_path', type=str)
    args = parser.parse_args()


    ### dictionaryのload ###
    token2id = dataset.load_dictionary(args.dictionary_path)
    vocab_size = len(list(token2id.keys()))
    id2token = {i:t for t, i in token2id.items()}
    config.params.vocab_size = vocab_size
    print('vocab size: ', vocab_size)
    
    ### word2vec ####
    print('making id-vector dictionary')
    w2v_model = Word2Vec.load_word2vec_format(args.w2v_path, binary=True)
    id_vec_dic = make_id_vector_dic(w2v_model, id2token, vocab_size)
    
    ### dataのload  ###
    print('loading batch')
    with open(args.batch_path, 'rb') as f_batch:
        list_batch = pickle.load(f_batch)
        
    list_batch = list_batch[:1000]
    
    ### batchごとにvectorize###
    print('id2vector')
    
    pool = Pool()
    num_process = pool._processes
    split_for_mp = []
    split_size = len(list_batch) // num_process
    for i in range(num_process):
        if i+1 < num_process:
            split_for_mp.append(list_batch[i*split_size: (i+1)*split_size])
        else:
            split_for_mp.append(list_batch[i*split_size: ])        
    del list_batch
    
    mp_results = pool.map(mp_func, split_for_mp)
    pool.close()
    
    list_vector_batch = []
    for result in mp_results:
        list_vector_batch.extend(result)
        
    print(len(list_batch))
    print(len(list_vector_batch))
        
    dataset.save_batch(args.save_path, list_vector_batch)
