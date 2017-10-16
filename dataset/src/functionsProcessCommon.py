# -*- coding: utf-8 -*-

import sys
import re
import mojimoji

from settings import START, EOS

def processDigit(sentence):
    return re.sub("[0-9]{1,}", "<D>", sentence)

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
                        "情報BOX:", "特別リポート:", "ホットストック:", "ブログ:", "オピニオン:", "BRIEF-", "UPDATE.*-", r"^【.+?】", r"コラム【.+?】", r"^\(.+?\)", r"^.+?こうみる:"]
    tail_remove_list = ["[:=]識者は?こうみる", r"\s*\|\s*ロイター"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    return title.strip()

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
    return content.strip()

def processAfpTitle(title):
    head_remove_list = ["^【.+?】", "^<.*Beauty Life>", "^動画:", "^字幕:"]
    tail_remove_list = ["写真\d*枚 国際ニュース:AFPBB News", "写真\d*枚 マリ・クレール (スタイル|スタイル ムッシュ|スタイル マリアージュ) : marie claire (style|style monsieur|style mariage)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    return title.strip()

def processAfpContent(content):
    head_remove_list = ["^<br>", "^【.*?】", "^\(.+?\)"]
    tail_remove_list = ["\(c\).*?$", "【.*】.*$", ">>\s*記事全文.*?$", "■お問合せ先.*?", "■関連情報.*?"]
    inside_remove_list = ["【.*?】"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    content = removeInside(content, inside_remove_list)
    return content.strip()

def processSankeiTitle(title):
    head_remove_list = [r"^【.+?】", r"\(動画(あり|付き|つき|も)\)"]
    tail_remove_list = [r"\(動画(あり|付き|つき|も)\)", r"\([前後]編\)", r"\(一問一答\)"]
    inside_remove_list = [r"\(\d+完?\)", r"\([上下]\)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list]) 
    title = removeInside(title, inside_remove_list)
    return title.strip()

def processSankeiContent(content):
    symbol = ["■", "□", "◆", "◇", "▲", "△", "▼", "▽"]
    head_remove_list = [r"^<br>", r"読んで見フォト", r"^<br>", r"写真で深読み、見るニュース", r"^<br>"]
    head_remove_list += [r"^%s.+?<br>"%x for x in symbol]
    tail_remove_list = [r"<br>%s"%x for x in symbol]
    inside_remove_list = ["[%s]"%("".join(symbol))] 
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return content.strip()

def processAsahiTitle(title):
    head_remove_list = [r"^【.+?】",  r"^\(.+?\)", r"^《.+?》", r"^訂正:"]
    tail_remove_list = [r"\(.+\)$", r"=訂正(・おわび)?あり"]
    inside_remove_list = [r"\(\d+\)", r"\([上下]\)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    title = removeInside(title, inside_remove_list)
    return title.strip()

def processAsahiContent(content):
    head_remove_list = [r"^<br>"]
    tail_remove_list = []
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list])
    return content.strip()

def processYomiuriTitle(title):
    head_remove_list = [r"^<br>", r"^\(.+?\)", r"^〈[1-9上下]+〉", r"^【.+?】"]
    tail_remove_list = [r"\(.+\)$", r"=訂正(・おわび)?あり"]
    inside_remove_list = [r"\(\d+\)", r"\([上下]\)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    title = removeInside(title, inside_remove_list)
    return title.strip()

def processYomiuriContent(content):
    head_remove_list = [r"^<br>"]
    tail_remove_list = []
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list])
    return content.strip()
    
def processJijiTitle(title):
    return title.strip() # give up...

def processJijiContent(content):
    head_remove_list = [r"^<br>", r"^【.+?】", r"^\(.+?\)"]
    tail_remove_list = [r"<br>関連ニュース", r"<br>【(社会|経済|政治)記事一覧へ】", r"<br>【アクセスランキング】", r"【.+?】$"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return content.strip()
    
def processNikkeiTitle(title):
    head_remove_list = [r"^<br>", r"^\(.+?\)", r"^\)"]
    tail_remove_list = [r" :日本経済新聞$", r"\(.+?\)$"]
    inside_remove_list = [r"\([0-9上下]\)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list])
    title = removeInside(title, inside_remove_list)
    return title.strip()

def processNikkeiContent(content):
    head_remove_list = [r"^<br>", r"^\(.+?\)", r"^<br>", r"^【.+?】", r"^<br>"]
    tail_remove_list = []
    inside_remove_list = [r"画像の拡大"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    content = removeInside(content, inside_remove_list)
    return content.strip()

def processZaikeiTitle(title):
    head_remove_list = [r"^【.+?】", "^■FISCOアプリの銘柄選定:【本日の材料と銘柄】", "^《新興市場銘柄ダイジェスト》:", "^■(.+?)の銘柄選定:"]
    tail_remove_list = [r"\s*\|\s*財経新聞\s*$", "\s*\|\s*韓流STARS\s*$"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return title.strip()

def processZaikeiContent(content):
    head_remove_list = [r"^<br>"]
    tail_remove_list = []
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return content.strip() # tired...

def processItmediaTitle(title):
    head_remove_list = []
    tail_remove_list = ["\s+\-\s+.+?$", "\s*\(\d+/\d+\)\s*$"]
    inside_remove_list = [r"\([0-9上下]\)"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    title = removeInside(title, inside_remove_list)
    title = re.sub("[―—]{2}", ":", title)
    return title.strip()

def processItmediaContent(content):
    head_remove_list = []
    tail_remove_list = [r"<br>Copyright©", r"<br>.+?も併せてチェック", "。<br>過去の.+?一覧はこちら", "この記事が気に入ったら"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return content.strip() 

def processGigazineTitle(title):
    head_remove_list = []
    tail_remove_list = ["\s+\-\s+.+?$", "((先行)?試[飲食]|食べ比べ|速攻(フォト)?|フォト|実機)?レビュー$"]
    title = removeHeadTail(title, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return title.strip()

def processGigazineContent(content):
    head_remove_list = [r"^<br>"]
    tail_remove_list = [r"<br>関連コンテンツ$"]
    content = removeHeadTail(content, [2, 1], [head_remove_list, tail_remove_list], remove_formats=["(%s)(.+)", "(.+?)(%s)"])
    return content.strip() # so tired......
