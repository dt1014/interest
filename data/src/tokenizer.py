import re
import MeCab

# def tokenizePOSfilter(sentence, pos_filter):
#     tagger = MeCab.Tagger("-Ochasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
#     tagger.parse("")
#     node = tagger.parseToNode(sentence)
#     filtered = []
#     while node:
#         if str(node.feature.split(",")[0]) in pos_filter:
#             filtered.append(node.surface)
#         node = node.next
#     return filtered

def tokenize(sentence, O="chasen", neologd=False):
    if neologd:
        mt = MeCab.Tagger("-O"+O+" -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    else:
        mt = MeCab.Tagger("-O"+O)
    parse = mt.parse(sentence)
    if O == "wakati":
        return parse
    result = []
    for line in parse.split('\n'):
        m = re.search("^(.+?)\t.+?\t.+?\t(.+?)$", line)
        if m:
            result.append([re.sub("\t", "-", m.group(1)), re.sub("\t", "-", m.group(2))])
    return result

def replaceString(sentence, patterns):
    for s, l in patterns.items():
        sentence = re.sub(s, l, sentence)
    return sentence
        
def splitContent(content, number_sentences):
    patterns = {"\s": "",
                "\(<br>": "(",
                "<br>\)": ")",
                "<br>、": "、",
                "<br>。": "。",
                "「<br>": "「",
                "<br>」": "」"}
    content = replaceString(content, patterns)
    split_point = "(。|<br>)"
    result = []
    for splitted in re.split(split_point, content):
        ###########################あとでけす###########################
        splitted = re.sub("(<S>|<EOS>)", "", splitted)
        ################################################################
        m = re.search(split_point, splitted)
        if not m and len(splitted)>0:
            result.append(splitted + "。")

    if number_sentences > 1:
        temp_result = result[:]
        result = []
        for idx in range(1, len(temp_result)):
            result.append(temp_result[idx-1]+temp_result[idx])
            
    return result

