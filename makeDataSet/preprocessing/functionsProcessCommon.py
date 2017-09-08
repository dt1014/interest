# -*- coding: utf-8 -*-

import sys
import re
import mojimoji

from settings import START, EOS

def processGeneralTitle(title):
    title = mojimoji.han_to_zen(title, digit=False, ascii=False)
    title = mojimoji.zen_to_han(title, kana=False)
    title = title.strip()
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
    head_remove_list = ["〔.+〕", "訂正:", "訂正.+-", "再送:", "再送-", "コラム:", "焦点:", "視点:", "インタビュー:", "アングル:", "緊急市場調査:", \
                        "情報BOX:", "特別リポート:", "ホットストック:", "ブログ:", "オピニオン:", "BRIEF-", "UPDATE.*-", r"^【.+?】", r"コラム【.+?】"r"^\(.+?\)"]
    tail_remove_list = ["[:=]識者は?こうみる", r"\s*\|\s*ロイター"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    return START + title.strip() + EOS

def processReutersContent(content):
    head_remove_list = [r"\[.+?\]\s*-?\s*", r"^【.+?】"]
    tail_remove_list = []
    inside_remove_list = [r"\(<br>.*<br>\)", "<br>\.N225<br>"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list])
    # processing for code or abbreviation of company
    pattern = r"\(<br>([a-zA-Z]+?)\.?[a-zA-Z0-9]+<br>\)"
    while True:
        if re.search(pattern, content):
            content = re.sub(pattern, r"(\1)", content)
        else:
            break
    content = removeInside(content, inside_remove_list)
    return START + content.strip() + EOS

def processAfpTitle(title):
    head_remove_list = ["^【.+?】", "^<.*Beauty Life>", "^動画:", "^字幕:"]
    tail_remove_list = ["写真\d*枚 国際ニュース:AFPBB News", "写真\d*枚 マリ・クレール (スタイル|スタイル ムッシュ|スタイル マリアージュ) : marie claire (style|style monsieur|style mariage)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    return START + title.strip() + EOS

def processAfpContent(content):
    head_remove_list = ["^<br>", "^【.*?】", "^\(.+?\)"]
    tail_remove_list = ["\(c\).*?$", "【.*】.*$", ">>\s*記事全文.*?$", "■お問合せ先.*?", "■関連情報.*?"]
    inside_remove_list = ["【.*?】"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    content = removeInside(content, inside_remove_list)
    return START + content.strip() + EOS

