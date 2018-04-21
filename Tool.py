import requests
import json
from Word import Word
import logging
import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def read_from_file(path):
    """
    读取文件
    :param path:文件路径
    :return: 以行为单位的列表
    """
    with open(path, 'r') as f:
        return f.readlines()


def write_to_file(path, words, type='w'):
    """
    写文件
    :param path: 文件路径
    :param words: 以行为单位的列表
    """
    words = list(map(lambda x: x + '\n', words))
    with open(path, type) as f:
        f.writelines(words)


def foreach(fun, iterator):
    for item in iterator:
        fun(item)


def get_negative_list():
    """
    获取负面词列表
    :return: 负面词列表
    """
    lines = read_from_file(Config.NEGATIVE_CORE_WORD)
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    words = []
    for line in lines:
        # print(line)
        words.append(Word(line.split('	')[0], line.split('	')[1], int(line.split('	')[2])))
    return words


def get_no_list():
    """
    获取否定词列表
    :return: 否定词列表
    """
    lines = read_from_file(Config.NO_WORD)
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    return list(lines)


def get_limit_list():
    """
    获取限制词列表
    :return: 限制词列表
    """
    lines = read_from_file(Config.LIMIT_WORD)
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    return list(lines)


def get_special_list():
    """
    获取特殊修饰词列表
    :return: 特殊修饰词列表
    """
    lines = read_from_file(Config.SPECIAL_WORD)
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    return list(lines)


def clear(ori_str: str):
    """
    字符串格式化（去特殊符号）
    :param ori_str:源字符串
    :return: 格式化字符串
    """
    return ori_str.replace('(', '').replace(')', '').replace('［', '').replace('］', '').replace(' ', '')


def get_abbs(company_name):
    """
    获取企业简称列表
    :param company_name: 企业全称
    :return: 企业简称列表
    """
    company = requests.post(Config.ABBS_URL, company_name.encode('utf-8'))
    # print(json.loads(company.text))
    abbs = json.loads(company.text)['abbs']
    # print(abbs)
    return sorted(list(filter(lambda x: x != '', set(abbs + [company_name]))), key=lambda x: len(x), reverse=True)
