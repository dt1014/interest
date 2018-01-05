# -*- coding: utf-8 -*-
import os
import sys
import json
import pickle
import argparse

import chainer
from chainer.iterators import SerialIterator
from chainer import training
from chainer.dataset import convert
from chainer.training import extensions
import chainer.links as L

import nnModel
from utils import *

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../../../data/src/")
import word2vec_model as w2v

env_config = {"gpu": {"main": 0, "second": 1, "third": 2, "forth": 3}}

def getInitialEmbed(vocab_size, embedding_size, dictionary, name):
    if name is None:
        w2v.loadModel()
    else:
        try:
            w2v.loadModel(name, binary=False)
        except FileNotFoundError:
            w2v.trainModel(size=embedding_size, name=name)
            
    initial_W = L.EmbedID(vocab_size, embedding_size, ignore_label=-1).W.data

    replace_count = 0
    for token, ID in dictionary.items():
        try:
            initial_W[ID] = w2v.model[token]
            replace_count += 1
        except KeyError:
            pass

    initial_W = initial_W.astype(np.float32)

    return initial_W, replace_count
    
def convertBatch(batch, device=-1, online_pad=False):

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
    
    if args.opt_config["use_word2vec"]:
        sys.stdout.write("\r%-50s"%"   setting initial W ...")
        args.nn_config["initial_EG_W"], replace_count_EG = getInitialEmbed(args.nn_config["V_vocab_size"], args.nn_config["D_embedding_size"], dictionary, name=None)
        w2v.model = None
        args.nn_config["initial_F_W"], replace_count_F = getInitialEmbed(args.nn_config["V_vocab_size"], args.nn_config["H_hidden_size"], dictionary, name="my.model%d"%args.nn_config["H_hidden_size"])
        sys.stdout.flush()
        print()
        print(   "times replaing initial vector for E and G: %d / %d"%(replace_count_EG, args.nn_config["V_vocab_size"]))
        print(   "times replaing initial vector for F      : %d / %d"%(replace_count_F, args.nn_config["V_vocab_size"]))
        
    nn, model, optimizer = setup.modelSetup(nnModel, args.nn_config, args.opt_config)
    xp, gpu, model = setup.cudaSetup(model, env_config)
    
    train_iter = SerialIterator(train, args.opt_config["batchsize"])
    # val_iter = SerialIterator(val, len(val), repeat=False, shuffle=False)

    if isinstance(env_config["gpu"]["main"], int):
        updater = training.StandardUpdater(train_iter,
                                           optimizer,
                                           converter=convertBatch,
                                           device=env_config["gpu"]["main"])
    else:
        updater = training.ParallelUpdater(train_iter,
                                           optimizer,
                                           converter=convertBatch,
                                           devices=env_config["gpu"])
    # if isinstance(env_config["gpu"], int):
    #     eval_device = env_config["gpu"]
    # else:
    #     eval_device = env_config["gpu"]["main"]
        
    # evaluator = extensions.Evaluator(val_iter,
    #                                  model,
    #                                  converter=convertBatch,
    #                                  device=eval_device)
        
    trainer = training.Trainer(updater, (args.opt_config["epoch"], "epoch"), args.outdir)
    
    trainer.extend(extensions.LogReport(log_name="training.log",
                                        trigger=(1, "epoch")))
    trainer.extend(extensions.snapshot(filename="trainer{.updater.epoch}"))
    trainer.extend(extensions.snapshot_object(model,
                                              filename="model{.updater.epoch}"))
    trainer.extend(extensions.dump_graph("main/loss",
                                         out_name="cg.dot"))
    # trainer.extend(evaluator, name="val")
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
        train, val = dataSetup(train, val)
        saveOBJs(args.tempdir, {"train": train, "val": val})

    del val
    val = None
  
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
