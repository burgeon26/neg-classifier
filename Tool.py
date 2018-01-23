import requests
import json


def read_from_file(path):
    """
    读取文件
    :param path:文件路径
    :return: 以行为单位的列表
    """
    with open(path, 'r') as f:
        return f.readlines()


def write_to_file(path, words):
    """
    写文件
    :param path: 文件路径
    :param words: 以行为单位的列表
    """
    words = list(map(lambda x: x + '\n', words))
    with open(path, 'w') as f:
        f.writelines(words)


def foreach(fun, iterator):
    for item in iterator:
        fun(item)


def get_negative_list():
    """
    获取负面词列表
    :return: 负面词列表
    """
    lines = read_from_file('/home/zhenlingcn/Documents/ZFTP/negative.txt')
    lines = map(lambda x: x.replace('\n', '').replace('\ufeff', ''), lines)
    return list(lines)


def get_positive_list():
    """
    获取正面词列表
    :return: 正面词列表
    """
    lines = read_from_file('/home/zhenlingcn/Documents/ZFTP/positive.txt')
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
    company = requests.post('http://218.77.58.173:5005/api/abb', company_name.encode('utf-8'))
    abbs = json.loads(company.text)['abbs']
    # print(abbs)
    return abbs
