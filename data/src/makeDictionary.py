import os
import re
import pickle
import argparse
import functools
import gensim

import pandas as pd

import tokenizer as tkn
import utils

MIN_FREQUENCY = 5
START_SYMBOL = "<S>"
END_SYMBOL = "<EOS>"
UNK_SYMBOL = "<UNK>"
DIGIT_SYMBOL = "<D>"

def tokenizeFunc(sentence):
    func = functools.partial(tkn.tokenize, O="wakati", neologd=True)
    result = re.sub("\n", "", func(sentence))
    result = re.sub(r"[0-9]+([^年月日時0-9])", r"%s\1"%DIGIT_SYMBOL, result)
    result = re.sub(r"([1-9]{,2}月)", r"\1 ", result)
    result = re.sub(r"((午前)|(午後))", r"\1 ", result)
    return result.split()
    
def tokenizeTitleTarget(df):
    df_ = df.applymap(tokenizeFunc)
    return df_
    
def getDict(df):

    dictionary = gensim.corpora.Dictionary(df.values.flatten())

    bow = dict(dictionary.doc2bow([elem for list_elem in df.values.flatten() for elem in list_elem]))

    seed_dict = {START_SYMBOL: 0,
                 END_SYMBOL: 1,
                 UNK_SYMBOL: 2,
                 DIGIT_SYMBOL: 3}
    filtered_dict =  seed_dict.copy()

    val = len(filtered_dict)
    for k in dictionary.token2id.keys():
        if bow[dictionary.token2id[k]] >= MIN_FREQUENCY and not k in list(seed_dict.keys()):
            filtered_dict[k] = val
            val += 1
    
    vocab_sizes = {"before filter": len(list(dictionary.iterkeys())),
                   "after filter": len(list(filtered_dict.items()))}

    return filtered_dict, vocab_sizes, bow

def token2idFunc(tokens, dictionary):
    result = []
    for t in tokens:
        try:
            result.append(dictionary[t])
        except KeyError:
            result.append(dictionary[UNK_SYMBOL])
    return result

def token2id(df, dictionary):
    func = functools.partial(token2idFunc, dictionary=dictionary)
    df_ = df.applymap(func)
    return df_

def id2tokenFunc(ids, dictionary_r):
    return [dictionary_r[i] for i in ids]
    
def id2token(df, dictionary):
    dictionary_r = {v: k for k, v in dictionary.items()}
    func = functools.partial(id2tokenFunc, dictionary_r=dictionary_r)
    df_ = df.applymap(func)
    return df_
    
def save(df, df_id, dictionary, vocab_sizes, bow, outdir):

    save_dict = locals()
    save_dict.pop("outdir")
    
    for key, val in save_dict.items():
        outpath = os.path.join(outdir, key+".pkl")
        utils.savePickle(outpath, val)
                    
                 
def main(args):
    
    df_raw = pickle.load(open(args.inpath, "rb"))
    print("tokenize")
    df_token = tokenizeTitleTarget(df_raw)
    print("getDict")
    dictionary, vocab_sizes, bow = getDict(df_token)
    print("token2id")
    df_id = token2id(df_token, dictionary)
    df_token_unk = id2token(df_id, dictionary)

    df_token.columns = [x+"_token" for x in df_token.columns]
    df_token_unk.columns = [x+"_token_unk" for x in df_token_unk.columns]

    df = pd.concat((df_raw, df_token, df_token_unk), axis=1)
    
    save(df, df_id, dictionary, vocab_sizes, bow, args.outdir)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inpath", type=str, help="")
    parser.add_argument("--outdir", type=str, help="")
    args = parser.parse_args()

    main(args)
    
