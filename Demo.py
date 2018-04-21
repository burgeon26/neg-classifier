from Text import Text, LTP
from Tool import *

if __name__ == '__main__':
    ltp = LTP()
    # text = Text(ltp, get_abbs('众安在线财产保险股份有限公司'), path='Data/text.txt')
    # print(text.score())
    # print(get_abbs('北京京东股份有限公司'))
    # print(clear('( 鸿道集团) 被王老吉［投诉］，告上法庭．'))
    text = Text(ltp,get_abbs('北京京东股份有限公司'), text=clear('北京京东被深圳华为举报'))
    print(text.score())