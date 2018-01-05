import os
import pickle
import numpy as np
import pandas as pd
import tqdm
import warnings
warnings.filterwarnings("ignore")

from gensim.models import Word2Vec, KeyedVectors

my_path = os.path.dirname(os.path.abspath(__file__))
model_dir = my_path + "/../../word2vec"
model = None

with open(os.path.join(my_path, "target_list.txt"), "r") as f:
    lines = f.readlines()
learning_list = []
for line in lines:
    learning_list.append(line.strip())

corpus_path = my_path + "/../result/all/getTarget/title_target.pkl"
    
def loadModel(name="entity_vector.model.bin", binary=True):
    global model
    try:
        model = Word2Vec.load_word2vec_format(os.path.join(model_dir, name), binary=binary)
    except DeprecationWarning:
        model = KeyedVectors.load_word2vec_format(os.path.join(model_dir, name), binary=binary)
    
def saveModel(name="my.model.bin", binary=True):
    model.save_word2vec_format(os.path.join(model_dir, name), binary=binary)

def trainModel(size, window=5, min_count=5, corpus=None, name=None):
    if corpus is None:
        corpus = getCorpus()

    global model
    model = Word2Vec(corpus, size=size, window=window, min_count=min_count, workers=4)
    
    if name is None:
        saveModel(name="my.model%d"%size, binary=False)
    else:
        saveModel(name=name, binary=False)
    
def getCorpus():
    rng = np.random.RandomState(0)
    df = pickle.load(open(corpus_path, "rb"))
    corpus = df.values.flatten()
    rng.shuffle(corpus)

    import tokenizer as tkn
    corpus = [tkn.tokenize(sentence, O="wakati", neologd=True).split() for sentence in corpus]
    
    return corpus

def buildNewModel(name):
    global model
    loadModel()
    for target in learning_list:
        print("=== learning... corpus: %s ==="%target)
        model.train(getCorpus(target))
    saveModel(name)
    
    
    
