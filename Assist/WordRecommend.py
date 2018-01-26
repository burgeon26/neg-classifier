import Config
from Assist.WordCount import word_count
from Tool import *

RECOMMEND_PATH = Config.RECOMMEND_PATH


def auto_recommend(words, write=False, path='words.txt', limit=500):
    counts = word_count(RECOMMEND_PATH, 'v')
    useful_words = []
    for word, num in counts.items():
        if num > limit and word not in words:
            useful_words.append(word)
    print('推荐词语{}个'.format(len(useful_words)))
    if write:
        write_to_file(path, useful_words)
        print('已成功输出到文件')


if __name__ == '__main__':
    negative_words = list(map(lambda x: x.word, get_negative_list()))
    auto_recommend(negative_words, True, Config.RECOMMEND_SAVE_PATH)
