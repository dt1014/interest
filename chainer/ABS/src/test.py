# -*- coding: utf-8 -*-
import os
import sys
import json
import pickle
import argparse
import functools
import itertools
import copy

import pandas as pd

import chainer
from chainer.iterators import SerialIterator
import chainer.functions as F

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../../../data/src/")
from makeDictionary import START_SYMBOL, END_SYMBOL, UNK_SYMBOL, DIGIT_SYMBOL

import nnModel
from utils import *
from search import beamsearch

BEAM_WIDTH = 3
MAX_LENGTH = 20

from train import convertBatch

env_config = {"gpu": {"main": 0}}

def predict(x, yc, nn):

    x_yc = [(x_, yc_) for x_, yc_ in zip(x, yc)]
    
    with chainer.using_config("train", False):
        y = nn(x_yc)
    
    prob = F.softmax(nn(x_yc), axis=1).data
    
    return prob
        
def test(args, nnModel, dictionary, data, epoch):

    configSetup(args, dictionary)
    try:
        _, model, _ = setup.modelSetup(nnModel, args.nn_config, args.opt_config, args.modelpath, epoch)
    except FileNotFoundError:
        return None, None

    xp, gpu, model = setup.cudaSetup(model, env_config)
    iteration = SerialIterator(data, len(data), repeat=True, shuffle=False)

    with chainer.using_config("train", False):
        model(*convertBatch(iteration.next(), env_config["gpu"]["main"]))

    loss, accuracy = model.loss, model.accuracy

    return loss.data, accuracy.data


def scheduleTest(args, nnModel, dictionary, data):

    losses = []
    accuracies = []
    for epoch in range(1, args.opt_config["epoch"]+1):
        args_ = copy.deepcopy(args)
        loss, accuracy = test(args_, nnModel, dictionary, data, epoch)
        losses.append(loss)
        accuracies.append(accuracy)
        
    return losses, accuracies
        
def main(args):

    global nnModel

    if os.path.exists(os.path.join(args.tempdir, "train.pkl")) and os.path.exists(os.path.join(args.tempdir, "val.pkl")) and os.path.exists(os.path.join(args.tempdir, "test.pkl")):
        train = pickle.load(open(os.path.join(args.tempdir, "train.pkl"), "rb"))
        val = pickle.load(open(os.path.join(args.tempdir, "val.pkl"), "rb"))
        test = pickle.load(open(os.path.join(args.tempdir, "test.pkl"), "rb"))
    else:
        train = pickle.load(open(args.trainpath, "rb"))
        val = pickle.load(open(args.valpath, "rb"))
        test = pickle.load(open(args.testpath, "rb"))
        train, val, test = dataSetup(train, val, test)
        saveOBJs(args.tempdir, {"train": train, "val": val, "test": test})
    dictionary = pickle.load(open(args.dicpath, "rb"))

    results = []
    for data in [train, val, test]:
        losses, accuracies = scheduleTest(args, nnModel, dictionary, data)
        results.append([losses, accuracies])


    train_df = pd.DataFrame(np.array(results[0]).T, index=["epoch"+str(i) for i in range(1, len(results[0][0])+1)], columns=["loss", "accuracy"])
    val_df = pd.DataFrame(np.array(results[1]).T, index=["epoch"+str(i) for i in range(1, len(results[0][0])+1)], columns=["loss", "accuracy"])
    test_df = pd.DataFrame(np.array(results[2]).T, index=["epoch"+str(i) for i in range(1, len(results[0][0])+1)], columns=["loss", "accuracy"])

    train_df.to_csv(os.path.join(args.outdir, "train_score.csv"))
    val_df.to_csv(os.path.join(args.outdir, "val_score.csv"))
    test_df.to_csv(os.path.join(args.outdir, "test_score.csv"))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trainpath", type=str, help="")
    parser.add_argument("--valpath", type=str, help="")
    parser.add_argument("--testpath", type=str, help="")
    parser.add_argument("--tempdir", type=str, help="")
    parser.add_argument("--dicpath", type=str, help="")
    parser.add_argument("--modelpath", type=str, help="")
    parser.add_argument("--outdir", type=str, help="")
    parser.add_argument("--dataset_config", type=json.loads, help="")
    parser.add_argument("--nn_config", type=json.loads, help="")
    parser.add_argument("--opt_config", type=json.loads, help="")
    args = parser.parse_args()

    main(args)
