# -*- coding: utf-8 -*-
import os
import sys
import json
import pickle
import argparse
import nnModel

import chainer
from chainer.iterators import SerialIterator
from chainer import training
from chainer.dataset import convert
from chainer.training import extensions

from utils import *

env_config = {"gpu": 0}

def convertBatch(batch, device, online_pad=False):

    xs = [x for x, _ in batch]
    ts = [t for _, t in batch]

    if device < 0:
        result_x = [chainer.cuda.to_cpu(np.array(x)) for x in xs]
        result_t = chainer.cuda.to_cpu(np.array(ts))
        return tuple([result_x, result_t])

    else:
        range_x = np.cumsum([len(x) for x in xs[: -1]], dtype=int)
        concat_x = np.concatenate(xs, axis=0)
        range_x_ = np.cumsum([len(x) for x in concat_x[: -1]], dtype=int)
        concat_x_ = np.concatenate(concat_x, axis=0)
        concat_x_ = chainer.cuda.to_gpu(concat_x_, device, chainer.cuda.Stream.null)
        result_x = chainer.cuda.cupy.split(concat_x_, range_x_)
        result_x_ = []
        for i in range(0, len(concat_x), 2):
            result_x_.append((result_x[i], result_x[i+1]))                                                                                              
        result_t = chainer.cuda.cupy.array(ts)
        return tuple([result_x_, result_t])

def trainModel(args, train, val, dictionary):

    configSetup(args, dictionary)
    nn, model, optimizer = setup.modelSetup(nnModel, args.nn_config, args.opt_config)
    xp, gpu, model = setup.cudaSetup(model, env_config)
    
    train_iter = SerialIterator(train, args.opt_config["batchsize"])
    val_iter = SerialIterator(val, len(val), repeat=False, shuffle=False)

    # updater = training.StandardUpdater(train_iter,
    #                                    optimizer,
    #                                    converter=converter,
    #                                    device=env_config["gpu"])
    
    updater = training.ParallelUpdater(train_iter,
                                       optimizer,
                                       converter=convertBatch,
                                       devices={"main": 0, "second": 1, "third": 2, "forth": 3})

    evaluator = extensions.Evaluator(val_iter,
                                     model,
                                     converter=convertBatch,
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

    sys.stdout.flush()
    print()
    print("   start training")
    print()
    
    trainer.run()

    
def main(args):

    global nnModel
    sys.stdout.write("\r%-50s"%"   setting dataset ...")

    dictionary = pickle.load(open(args.dicpath, "rb"))
    if os.path.exists(os.path.join(args.tempdir, "train.pkl")) and os.path.exists(os.path.join(args.tempdir, "val.pkl")):
        train = pickle.load(open(os.path.join(args.tempdir, "train.pkl"), "rb"))
        val = pickle.load(open(os.path.join(args.tempdir, "val.pkl"), "rb"))
        
    else:
        train = pickle.load(open(args.trainpath, "rb"))
        val = pickle.load(open(args.valpath, "rb"))
        train, val = trainSetup(train, val)
        saveOBJs(args.tempdir, {"train": train, "val": val})
        
    sys.stdout.flush()
    
    trainModel(args, train, val, dictionary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trainpath", type=str, help="")
    parser.add_argument("--valpath", type=str, help="")
    parser.add_argument("--tempdir", type=str, help="")
    parser.add_argument("--dicpath", type=str, help="")
    parser.add_argument("--outdir", type=str, help="")
    parser.add_argument("--dataset_config", type=json.loads, help="")
    parser.add_argument("--nn_config", type=json.loads, help="")
    parser.add_argument("--opt_config", type=json.loads, help="")
    args = parser.parse_args()

    main(args)
