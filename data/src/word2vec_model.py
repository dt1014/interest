import os
import pickle
import pandas as pd
import tqdm
import warnings
warnings.filterwarnings("ignore")
from gensim.models import Word2Vec

my_path = os.path.dirname(os.path.abspath(__file__))
model_dir = my_path + "/../../word2vec"
model = None

with open(os.path.join(my_path, "target_list.txt"), "r") as f:
    lines = f.readlines()
learning_list = []
for line in lines:
    learning_list.append(line.strip())

corpus_dir = my_path + "/../result"
    
def loadModel(name="entity_vector.model.bin"):
    global model
    model = Word2Vec.load_word2vec_format(os.path.join(model_dir, name), binary=True)
    
def saveModel(name="my.model.bin"):
    model.save_word2vec_format(os.path.join(model_dir, name), binary=True)

def getCorpus(target):
    path = os.path.join(corpus_dir, target, "common_procesed.pkl")
    df = pd.read_pickle(path)
    print("", end="")
    for content in tqdm.tqdm(df["content"].__iter__()):
        yield tkn.tokenize(content)

def buildNewModel(name):
    global model
    loadModel()
    for target in learning_list:
        print("=== learning... corpus: %s ==="%target)
        model.train(getCorpus(target))
    saveModel(name)
    
    
    
