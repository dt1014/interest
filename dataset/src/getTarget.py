import os
import re
import pickle
import argparse
import numpy as np
import pandas as pd

import word2vec_model as w2v
import tokenizer as tkn

my_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(my_path, "target_list.txt"), "r") as f:
    lines = f.readlines()
learning_list = []
for line in lines:
    learning_list.append(line.strip())

pos_filter = ["^名詞", "^接頭詞", "^接続詞", "^連体詞", "^動詞", "^形容詞", "^副詞"]
pos_uniques = ["^名詞-固有名詞-人名",
               "^名詞-固有名詞-組織",
               "^名詞-固有名詞-地域-一般"]
country_expression = {"アメリカ": "米",
                      "アメリカ": "米国",
                      "アメリカ合衆国": "米",
                      "アメリカ合衆国": "米国",
                      "ロシア": "露",
                      "ソ連": "ソ",
                      "イギリス": "英",
                      "イギリス": "英国",
                      "フランス": "仏",
                      "ドイツ": "独",
                      "イタリア": "伊",
                      "スペイン": "西",
                      "カナダ": "加",
                      "ブラジル": "伯",
                      "インド": "印"}
country_expression_ = {v: k for k, v in country_expression.items()}

def loadData(path):
    with open(path, "rb") as f:
        df = pickle.load(f)
    return df

def w2vSetup():
    global w2v
    w2v.loadModel()
        
def wordSimilarity(word1, word2):
    if word1 == word2:
        return 1.0
    try:
        return w2v.model.similarity(word1, word2)
    except (KeyError, ValueError):
        return 0.0

def countrySimilarity(word1, word2):
    if word1 == word2:
        return 1.0
    if word1 in list(country_expression.keys()):
        return max(wordSimilarity(word1, word2),
                   wordSimilarity(country_expression[word1], word2))
    elif word1 in list(country_expression_.keys()):
        return max(wordSimilarity(word1, word2),
                   wordSimilarity(country_expression_[word1], word2))
    else:
        return wordSimilarity(word1, word2)    

def filterPOS(token):
    for pos in pos_filter:
        if re.search(pos, token[1]):
            return token
    return None

def isUnique(token):
    if not re.search("^名詞", token[1]):
        return False
    for unq in pos_uniques:
        if re.search(unq, token[1]):
            return True
    return False

def isCountry(token):
    return True if re.search("^名詞-固有名詞-地域-国", token[1]) else False

# heuristic
def calculateSimilarityScores(title, target, threshold=0.5):
    title_tokens = tkn.tokenize(title)
    target_tokens = tkn.tokenize(target)

    w_scores = []
    unq_cntry_scores = []
    for token1 in map(filterPOS, title_tokens):
        if not token1:
            continue
        w_score = 0.0
        flag_unique = isUnique(token1)
        flag_country = isCountry(token1)
        for token2 in map(filterPOS, target_tokens):
            if not token2:
                continue
            if flag_country:
                temp = countrySimilarity(token1, token2)
            else:
                temp = wordSimilarity(token1, token2)
            if temp > w_score:
                w_score = temp
            if temp >= 1.0:
                w_score = 1.0
                break
        if flag_country or flag_country:
            unq_cntry_scores.append(True if w_score==1.0 else False)
            
        w_scores.append(w_score)

    percentage_unq_cntry_match = sum(unq_cntry_scores)/len(unq_cntry_scores) if len(unq_cntry_scores)>0 else None
    percentage_whole_match = sum([ws == 1.0 for ws in w_scores])/len(w_scores)
    percentage_threshold_match = sum([ws > threshold for ws in w_scores])/len(w_scores)
    average_w_score = np.average(np.array(w_scores))
    
    return (percentage_unq_cntry_match, 
            percentage_whole_match, 
            percentage_threshold_match, 
            average_w_score)

# def pickupSentences(title, content, number_sentences=1):
    
#     ###########################あとでけす###########################
#     title = re.sub("(<S>|<EOS>)", "", title)
#     ################################################################
#     print()
#     print("="*200)
#     print(title)
#     print(content)
#     for target in tkn.splitContent(content, number_sentences):
#         scores = calculateSimilarityScores(title, target)
#         print("-"*100)
#         print("   " + target)
#         print("   " + str(scores))
            
def filter(df, number_sentences=1, thresholds=(0.9, 0.65, 0.65, 0.65)):
    global w2v
    if not w2v.model:
        w2v.loadModel()

    result_true = []
    result_false = []
    for _, value in df.iterrows():
        import time
        time.sleep(2)
        title = value[0]
        content = value[1]
        ###########################あとでけす###########################
        title = re.sub("(<S>|<EOS>)", "", title)
        ################################################################
        
        target = tkn.splitContent(content, number_sentences)[0]
        scores = calculateSimilarityScores(title, target)
        use = True
        for s, t in zip(scores, thresholds):
            if s is None:
                continue
            use = use and (s > t)

        print("-"*100)
        print(title)
        print(target)
        print(scores)
        print(use)
