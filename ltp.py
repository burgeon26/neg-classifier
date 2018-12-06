# -*- coding:utf-8 -*-
# made by freedom
# 2017.3.29

import configparser
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer

# 识别人名和公司名
def NER(text, segmentor, postagger, recognizer):
    listNh = list()
    listNi = list()
    if len(text) < 2:
        return (listNh, listNi)
    words = segmentor.segment(text)
    postags = postagger.postag(words)
    netags = recognizer.recognize(words, postags)
    str = ''
    for word, ntag in zip(words, netags):
        if (ntag.endswith('-Nh')):
            if (ntag.startswith('B-')):
                str = word
            elif (ntag.startswith('I-')):
                str += word
            elif (ntag.startswith('E-')):
                str += word
                if str not in listNh:
                    listNh.append(str)
                    str = ''
            elif (ntag.startswith('S-')):
                str = word
                if str not in listNh:
                    listNh.append(str)
                    str = ''
        elif (ntag.endswith('-Ni')or ntag.endswith('-Ns')):
            if (ntag.startswith('B-')):
                str = word
            elif (ntag.startswith('I-')):
                str += word
            elif (ntag.startswith('E-')):
                str += word
                if str not in listNi:
                    listNi.append(str)
                    str = ''
            elif (ntag.startswith('S-')):
                str = word
                if str not in listNi:
                    listNi.append(str)
                    str = ''
    return (listNh, listNi)


# 加载模型
def loadModel():
    config = configparser.ConfigParser()
    with open('../show/config.ini', 'r') as cfgfile:
        config.readfp(cfgfile)
    cws_model = config.get('info', 'cws_model')
    pos_model = config.get('info', 'pos_model')
    ner_model = config.get('info', 'ner_model')

    segmentor = Segmentor()
    segmentor.load(cws_model)
    postagger = Postagger()
    postagger.load(pos_model)
    recognizer = NamedEntityRecognizer()
    recognizer.load(ner_model)
    return (segmentor, postagger, recognizer)


# 释放模型
def releaseModel(segmentor, postagger, recognizer):
    segmentor.release()
    postagger.release()
    recognizer.release()


# 主逻辑
def pyltp(text, segmentor, postagger, recognizer):
    (listNh, listNi) = NER(text, segmentor, postagger, recognizer)
    # releaseModel(segmentor, postagger, recognizer)
    cleanList(listNh, listNi)
    return (listNh, listNi)


# 特殊数据清理
def cleanList(listNh, listNi):
    for i,one_Ni in enumerate(listNi):
        listNi[i] = listNi[i].replace('有限公司有限公司','有限公司')
    listNi = list(set(listNi))
    listNh = [x for x in listNh if len(x) > 1]
    return (listNh, listNi)