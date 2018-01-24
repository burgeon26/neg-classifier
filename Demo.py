from Text import Text, LTP
from Tool import *

if __name__ == '__main__':
    """如果存在一个含义多个关键词的情况，建议选择较短的关键词"""
    ltp = LTP()
    # text = Text(ltp, get_abbs('甘肃省'), path='text.txt')
    # print(text.score())
    print(get_abbs('湖南顺泰钨业股份有限公司'))
    # print(clear('( 鸿道集团) 被王老吉［投诉］，告上法庭．'))
    text = Text(ltp,get_abbs('湖南顺泰钨业股份有限公司'), text=clear('顺泰钨业拖欠员工工资'))
    print(text.score())