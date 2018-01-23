from Tool import read_from_file, write_to_file, get_positive_list, get_negative_list
from Text import Text, LTP
import os, sys

WORD_COUNT_PATH = '/home/zhenlingcn/Desktop/test/content'  # 进行WordCount统计分析的目录


def word_count(files):
    """
    词频统计函数
    :param files: 统计文件列表
    :return: 词频统计字典
    """
    ltp = LTP()
    all_count = {}
    for file in files:
        print(file)
        path = os.path.join(os.path.abspath(WORD_COUNT_PATH), file)
        if os.path.isfile(path):
            text = Text(ltp, '', path)
            count = text.word_count()
            for word, num in count.items():
                # print(word,num)
                if word in all_count.keys():
                    all_count[word] += num
                else:
                    all_count[word] = num
    return all_count


def auto_analysis(words, write=False, path='words.txt', limit=10):
    """
    词库统计分析函数
    :param words: 词库单词列表
    :param write: 是否写入到文件
    :param path: 写入文件路径
    :param limit: 低频词语判定限制（即出现次数小于limit次判定为低频）
    """
    count = word_count(os.listdir(WORD_COUNT_PATH))
    no_use = 0
    few_use = 0
    useful_words = []
    for word in words:
        if word in count:
            if count[word] >= limit:
                useful_words.append(word)
            else:
                few_use += 1
        else:
            no_use += 1
    print('统计如下:\n'
          '高频词语:{}个\n'
          '低频词语:{}个\n'
          '从未使用词语:{}个\n'.format(len(useful_words), few_use, no_use))
    if write:
        write_to_file(path, useful_words)
        print('已成功输出到文件')


if __name__ == '__main__':
    positive_words = get_negative_list()
    auto_analysis(positive_words, True, '/home/zhenlingcn/Desktop/test/words.txt')
