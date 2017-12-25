import os
import re
import pickle
import argparse
import numpy as np
import pandas as pd

import word2vec_model as w2v
import tokenizer as tkn
import utils

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

# heuristic way (getting similarity comaring word vectors from trained word2vec model)
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
    # percentage_whole_match = sum([ws == 1.0 for ws in w_scores])/len(w_scores)
    # percentage_threshold_match = sum([ws > threshold for ws in w_scores])/len(w_scores)
    average_w_score = np.average(np.array(w_scores))
    
    # return (percentage_unq_cntry_match, 
    #         percentage_whole_match, 
    #         percentage_threshold_match, 
    #         average_w_score)
    return (percentage_unq_cntry_match, average_w_score)

def pickupSentences(title, content, number_sentences, thresholds):
    
    ###########################あとでけす###########################
    title = re.sub("(<S>|<EOS>)", "", title)
    ################################################################

    match_list = []
    highest_scores = (0, 0)
    highest_target = None
    for target in tkn.splitContent(content, number_sentences):

        # length of target must lager than that of title
        if len(target) < len(title):
            continue
        
        scores = calculateSimilarityScores(title, target)

        # pick up by threshold
        use = True
        for s, t in zip(scores, thresholds):
            if s is None:
                continue
            use = use and (s > t)
        if use:
            match_list.append((target, scores))

        # choose highest averageword score  # for no match
        if highest_scores[1] < scores[1]:
            highest_scores = scores
            highest_target = target

    # pick up from match list comparing just unq_score if unq_score is not None
    # otherwise, compare average word score
    if len(match_list) > 0:
        use_target = None
        use_scores = (0, 0)
        for target, scores in match_list:
            if scores[0] is None:
                if use_scores[1] < scores[1]:
                    use_target = target
                    use_scores = scores
            else:
                if use_scores[0] < scores[0]:
                    use_target = target
                    use_scores = scores
        return use_target, use_scores, True

    # if no match
    else:
        return highest_target, highest_scores, False
    
    #return use_target, scores
        
def assignTarget(df, number_sentences=1, thresholds=(0.9, 0.65, 0.65, 0.65)):
    ###########################あとでけす###########################
    import importlib
    importlib.reload(tkn)
    ################################################################
    global w2v
    if not w2v.model:
        w2v.loadModel()

    target_list = []
    use_list = []
    for _, value in df.iterrows():
        ###########################あとでけす###########################
        # import time
        # time.sleep(2)
        ################################################################
        title = value[0]
        content = value[1]
        target, scores, use = pickupSentences(title, content, number_sentences, thresholds)
        target_list.append(target)
        use_list.append(use)
            
        ###########################あとでけす###########################
        # if not target[-1] == "。":
        # if target is None:
        #     print("-"*100)
        #     print(title)
        #     print(target)
        #     print(content)
        #     print(scores)
        #     print(use)
        ################################################################
        
    df["target"] = target_list
    df["use"] = use_list
    return df
    
def parseMedia(flag_small):
    target_list = []
    for line in lines:
        target_list.append(line.strip())

    list_df = []
    for target in target_list:
        print("loading  ", target)
        df = pd.read_pickle(os.path.join(my_path, "../result", target, "common_procesed.pkl"))

        print("   searching target")

        if flag_small:
            print("   small data")
            df = df.ix[np.random.choice(np.arange(len(df)), 1000, replace=False), :].reset_index(drop=True)  
        
        df_ = assignTarget(df[["title__", "content__"]])
        df__ = df_.ix[np.where(df_["use"])[0], ["title__", "target"]].reset_index(drop=True)
        list_df.append(df__)

    result = pd.concat(list_df, axis=0).reset_index(drop=True)
    result.columns = ["title", "target"]
    return result

def save(outpath, result):
    utils.savePickle(outpath, result)
                
def main(args):

    result = parseMedia(args.small)
    save(args.outpath, result)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--outpath", type=str, help="")
    parser.add_argument("--small", action="store_true", default=False, help="")
    args = parser.parse_args()

    main(args)
    
