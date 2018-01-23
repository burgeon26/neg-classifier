"""系统评测工具"""
import os
from Text import Text, LTP
from Tool import get_abbs


def get_index_list(url):
    """
    读取Excel索引
    :param url: Excel文件路径
    :return:
    """
    with open(url, "r", encoding="utf-8") as file:
        content_list = file.readlines()
        indexes = []
        for content in content_list:
            try:
                index = content.split("	")[7].replace("\n", "")
                if index != "索引":
                    indexes.append(index)
            except IndexError:
                pass
        return indexes


def dir_test(path):
    """
    基于目录的整体性能评测
    目录结构必须为，根目录下为XLS文件，XLS文件里包含文件名称索引
    :param path:
    """
    ltp = LTP()
    files = os.listdir(path)
    # print(path)
    news_num = 0
    bad_news, good_news = 0, 0
    error_file = 0
    for file in files:
        if '.xls' in file:
            # print(file)
            indexes = get_index_list(os.path.join(path, file))
            for index in indexes:
                if news_num % 20 == 0:
                    print('扫描新闻数:{}'.format(news_num))
                print(index)
                news_num += 1
                try:
                    text = Text(ltp, get_abbs(file.replace('.xls', '')),
                                os.path.join(os.path.join(path, 'content'), index + '.txt'))
                    score = text.score()
                    # print(score)
                    if score < 0:
                        bad_news += 1
                    elif score > 0:
                        good_news += 1
                except FileNotFoundError:
                    error_file += 1
    print('总文件数:{}\n'
          '有效文件数:{}\n'
          '正面新闻数:{}\n'
          '负面新闻数:{}\n'
          '中立新闻数:{}\n'.format(news_num, news_num - error_file, good_news, bad_news,
                              news_num - error_file - good_news - bad_news))


if __name__ == '__main__':
    dir_test('/home/zhenlingcn/Desktop/test')
