# -*- coding: utf-8 -*-
import os
import sys
import json
import pickle
import argparse
import nnModel

from chainer.iterators import SerialIterator
from chainer import training
from chainer.dataset import convert
from chainer.training import extensions

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../../Common/")

import chainerSetup as setup
from utils import *

env_config = {"gpu": 0}
    
def trainModel(args, train, val, dictionary):

    configSetup(args, dictionary)
    nn, model, optimizer = setup.modelSetup(nnModel, args.nn_config, args.opt_config)
    xp, gpu, model = setup.cudaSetup(model, env_config)
    
    train_iter = SerialIterator(train, args.opt_config["batchsize"])
    val_iter = SerialIterator(val, len(val), repeat=False, shuffle=False)

    converter = convert.concat_examples # default
        
    updater = training.StandardUpdater(train_iter,
                                       optimizer,
                                       converter=converter,
                                       device=env_config["gpu"])
    evaluator = extensions.Evaluator(val_iter,
                                     model,
                                     converter=converter,
                                     device=env_config["gpu"])
        
    trainer = training.Trainer(updater, (args.opt_config["epoch"], "epoch"), args.outdir)
    
    trainer.extend(extensions.LogReport(log_name="training.log",
                                        trigger=(1, "epoch")))
    trainer.extend(extensions.snapshot(filename="trainer{.updater.epoch}"))
    trainer.extend(extensions.snapshot_object(model,
                                              filename="model{.updater.epoch}"))
    trainer.extend(extensions.dump_graph("main/loss",
                                         out_name="cg.dot"))
    trainer.extend(evaluator, name="val")
    trainer.extend(extensions.ProgressBar())

    trainer.run()

    
    from IPython import embed; embed()
    
    
def main(args):

    global nnModel
    
    train = pickle.load(open(args.trainpath, "rb"))
    val = pickle.load(open(args.valpath, "rb"))
    dictionary = pickle.load(open(args.dicpath, "rb"))

    train, val = trainSetup(train, val)
    trainModel(args, train, val, dictionary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inpath", type=str, help="")
    parser.add_argument("--trainpath", type=str, help="")
    parser.add_argument("--valpath", type=str, help="")
    parser.add_argument("--dicpath", type=str, help="")
    parser.add_argument("--outdir", type=str, help="")
    parser.add_argument("--dataset_config", type=json.loads, help="")
    parser.add_argument("--nn_config", type=json.loads, help="")
    parser.add_argument("--opt_config", type=json.loads, help="")
    args = parser.parse_args()

    main(args)
