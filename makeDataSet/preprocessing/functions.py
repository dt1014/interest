# -*- coding: utf-8 -*-

import sys
import re
import mojimoji

from settings import START, EOS

def processGeneralTitle(title):
    title = mojimoji.han_to_zen(title, digit=False, ascii=False)
    title = mojimoji.zen_to_han(title, kana=False)
    return title

def processGeneralContent(content):
    content = mojimoji.han_to_zen(content, digit=False, ascii=False)
    content = mojimoji.zen_to_han(content, kana=False)
    
    # cutting off first paragraph from content
    # patterns = ["^(.+?。\s*)(<br>|$)"]
    # for pattern in patterns:
    #     m = re.search(pattern, content)
    #     if m:
    #         content_ = m.group(1)
    #         break

    if not "content_" in locals():
        content_= content

    content_ = content_.strip()
    content_ = re.sub("(<br>[\s\t・]*)+", "<br>", content_)

    return content_

def removeHeadTail(sentence, n_groups, remove_lists, remove_formats=["(%s)(.+)", "(.+)(%s)"]):
    for n_group, remove_list, remove_format in zip(n_groups, remove_lists, remove_formats):
        for remove in remove_list:
            m = re.search(remove_format%remove, sentence)
            if m:
                sentence = m.group(n_group)
    sentence = sentence.strip()
    return sentence
                                                                                                                                           

def removeInside(sentence, remove_list):
    for remove in remove_list:
        sentence = re.sub(remove, "", sentence)
    return sentence
                                                                                                                           
def processReutersTitle(title):
    # 一文につき複数のパターンの組み合わせがある場合がある
    # 「〜こうみる:」を除くかどうか判断に悩む
    head_remove_list = ["〔.+〕", "訂正:", "訂正.+-", "再送:", "再送-", "コラム:", "焦点:", "視点:", "インタビュー:", "アングル:", "緊急市場調査:", \
                        "情報BOX:", "特別リポート:", "ホットストック:", "ブログ:", "オピニオン:", "BRIEF-", "UPDATE.*-"]
    tail_remove_list = ["[:=]識者は?こうみる"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    return START + title + EOS

def processReutersContent(content):
    head_remove_list = ["\[.+?\]\s*-?\s*"]
    tail_remove_list = []
    #print()
    #print(content)
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list])
    #print(content)
    return START + content + EOS
