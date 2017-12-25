import numpy as np 

import chainer.functions as F

def configSetup(args, dictionary):
    args.nn_config["V_vocab_size"] = len(list(dictionary.keys()))
    args.nn_config["C_window_size"] = args.dataset_config["previous_window_size"]
    args.nn_config["activate"] = F.__dict__[args.nn_config["activate"]]

def trainSetup(train_raw, val_raw):
    train = [((v[0], v[1]), np.int32(v[2])) for _, v in train_raw.iterrows()]
    val = [((v[0], v[1]), np.int32(v[2])) for _, v in val_raw.iterrows()]
    return train, val
