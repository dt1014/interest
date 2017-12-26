import os
import sys
import pickle
import numpy as np 

import chainer.functions as F

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/../../Common/")
import chainerSetup as setup

def configSetup(args, dictionary):
    args.nn_config["V_vocab_size"] = len(list(dictionary.keys()))
    args.nn_config["C_window_size"] = args.dataset_config["previous_window_size"]
    args.nn_config["activate"] = F.__dict__[args.nn_config["activate"]]

def trainSetup(train_raw, val_raw):
    train = [((np.int32(v[0]), np.int32(v[1])), np.int32(v[2])) for _, v in train_raw.iterrows()]
    val = [((np.int32(v[0]), np.int32(v[1])), np.int32(v[2])) for _, v in val_raw.iterrows()]
    return train, val

def savePickle(outpath, result):
    try:
        pickle.dump(result, open(outpath, "wb"))
    except OSError:
        bytes_out = pickle.dumps(result)
        n_bytes = sys.getsizeof(bytes_out)
        max_bytes = 2**31 - 1
        with open(outpath, "wb") as f_out:
            for idx in range(0, n_bytes, max_bytes):
                f_out.write(bytes_out[idx: idx+max_bytes])

def saveOBJs(outdir, save_dict):
    for key, val in save_dict.items():
        outpath = os.path.join(outdir, key+".pkl")
        savePickle(outpath, val)
