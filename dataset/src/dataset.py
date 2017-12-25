import os
import json
import pickle
import argparse
import numpy as np
import pandas as pd

import functools
from multiprocessing import Pool

from makeDictionary import START_SYMBOL, END_SYMBOL
import utils

rng = np.random.RandomState(0)

def split_x_yc_t(row, window_size, previous_ids):
    
    title = previous_ids + row[1][0]
    target = row[1][1]
    result = []

    for s, e in zip(np.arange(len(title)-window_size), np.arange(window_size, len(title))):
        temp = [target, title[s: e], title[e]] # x, yc, t
        result.append(temp)
    
    return result
    

def schedule_split(df, config, dictionary):
    pool = Pool(8)
    pool_result = pool.map(functools.partial(split_x_yc_t,
                                             window_size=config["previous_window_size"],
                                             previous_ids=config["previous_window_size"]*[dictionary[START_SYMBOL]]),
                           df.iterrows())
    result = []
    for pr in pool_result:
        result.extend(pr)
    
    return result

def save(train, df_id_train, df_id_val, df_id_test, outdir):

    save_dict = locals()
    save_dict.pop("outdir")

    for key, val in save_dict.items():
        outpath = os.path.join(outdir, key+".pkl")
        utils.savePickle(outpath, val)
    
    
def main(args):
    
    df_id = pickle.load(open(os.path.join(args.inpath, "df_id.pkl"), "rb"))
    dictionary = pickle.load(open(os.path.join(args.inpath, "dictionary.pkl"), "rb"))

    df_id_train, df_id_val, df_id_test = np.split(df_id.sample(frac=1, random_state=rng),
                                                  [int((1-args.config["val_test_ratio"])*len(df_id)), int((1-args.config["val_test_ratio"]/2.)*len(df_id))])
    
    train = schedule_split(df_id_train, args.config, dictionary)
    train = pd.DataFrame(train, columns=["x", "yc", "t"])

    save(train, df_id_train, df_id_val, df_id_test, args.outdir)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inpath", type=str, help="")
    parser.add_argument("--outdir", type=str, help="")
    parser.add_argument("--config", type=json.loads, help="")
    args = parser.parse_args()

    main(args)
    
