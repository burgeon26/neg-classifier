"""系统评测工具"""
import os
from Text import Text, LTP
from Tool import *
import pickle
import traceback


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
    news_num = 0
    bad_news = 0
    error_file = 0
    type = 'w'
    if os.path.exists('/home/zhenlingcn/Desktop/test/log.log'):
        with open('/home/zhenlingcn/Desktop/test/log.log','rb') as f:
            log = pickle.load(f)
            news_num = log['news_num']
            bad_news = log['bad_news']
            error_file = log['error_file']
            type = 'a'
    else:
        log = {'vis_xls': set(), 'vis_index': set(), 'news_num': 0, 'bad_news': 0, 'error_file': 0}
    try:
        for file in files:
            if '.xls' in file and file not in log['vis_xls']:
                # print(file)
                indexes = get_index_list(os.path.join(path, file))
                for index in indexes:
                    if index in log['vis_index']:
                        continue
                    if news_num % 20 == 0:
                        print('扫描新闻数:{}'.format(news_num))
                    print(index)
                    news_num += 1
                    try:
                        text = Text(ltp, get_abbs(file.replace('.xls', '')),
                                    os.path.join(os.path.join(path, 'content'), index + '.txt'))
                        score = text.score()
                        if score > 0:
                            bad_news += 1
                    except FileNotFoundError:
                        error_file += 1
                    log['vis_index'].add(index)
                log['vis_xls'].add(file)
                log['vis_index'].clear()
        print('总文件数:{}\n'
              '有效文件数:{}\n'
              '负面新闻数:{}\n'
              '中立新闻数:{}\n'.format(news_num, news_num - error_file, bad_news,
                                  news_num - error_file - bad_news))
        write_to_file('/home/zhenlingcn/Desktop/test/key.txt', ltp.key_sentences, type)
        if os.path.exists('/home/zhenlingcn/Desktop/test/log.log'):
            os.remove('/home/zhenlingcn/Desktop/test/log.log')
    except Exception:
        log['news_num'] = news_num
        log['bad_news'] = bad_news
        log['error_file'] = error_file
        with open('/home/zhenlingcn/Desktop/test/log.log', 'wb') as f:
            pickle.dump(log, f)
        write_to_file('/home/zhenlingcn/Desktop/test/key.txt', ltp.key_sentences,type)
        print(traceback.format_exc())
        print('出现异常，日志已记录')


if __name__ == '__main__':
    dir_test('/home/zhenlingcn/Desktop/report_analysis_intel')
