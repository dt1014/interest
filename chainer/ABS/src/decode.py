# -*- coding: utf-8 -*-
import os
import sys
import json
import pickle
import argparse
import functools
import itertools

import chainer
import chainer.functions as F

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../../../data/src/")
from makeDictionary import START_SYMBOL, END_SYMBOL, UNK_SYMBOL, DIGIT_SYMBOL

import nnModel
from utils import *
from search import beamsearch

BEAM_WIDTH = 3
MAX_LENGTH = 20

def predict(x, yc, nn):

    x_yc = [(x_, yc_) for x_, yc_ in zip(x, yc)]
    
    with chainer.using_config("train", False):
        y = nn(x_yc)
    
    prob = F.softmax(nn(x_yc), axis=1).data
    
    return prob
        
def decode(data, nn, dictionary, start_yc):
    predictFunc = functools.partial(predict,
                                    nn=nn)
    BSfunc = functools.partial(beamsearch,
                               start=start_yc,
                               predFunc=predictFunc,
                               beam_width=BEAM_WIDTH,                         
                               stop_id=dictionary[END_SYMBOL],
                               max_length=MAX_LENGTH)
    
    result = list(map(BSfunc, data))
    
    return result
    
def main(args):

    global nnModel
    
    train = pickle.load(open(args.trainpath, "rb"))
    val = pickle.load(open(args.valpath, "rb"))
    test = pickle.load(open(args.testpath, "rb"))
    dictionary = pickle.load(open(args.dicpath, "rb"))

    configSetup(args, dictionary)
    nn, _, _ = setup.modelSetup(nnModel, args.nn_config, args.opt_config, args.modelpath)

    start_yc = [dictionary[START_SYMBOL]] * args.dataset_config["previous_window_size"]

    for data in [train, val, test]:
        data = train["target"] #########################################################################################################
        decoded = decode(data, nn, dictionary, start_yc)
        

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trainpath", type=str, help="")
    parser.add_argument("--valpath", type=str, help="")
    parser.add_argument("--testpath", type=str, help="")
    parser.add_argument("--dicpath", type=str, help="")
    parser.add_argument("--modelpath", type=str, help="")
    parser.add_argument("--outpath", type=str, help="")
    parser.add_argument("--dataset_config", type=json.loads, help="")
    parser.add_argument("--nn_config", type=json.loads, help="")
    parser.add_argument("--opt_config", type=json.loads, help="")
    args = parser.parse_args()

    main(args)
