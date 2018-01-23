from Text import Text, LTP
from Tool import get_abbs

if __name__ == '__main__':
    """如果存在一个含义多个关键词的情况，建议选择较短的关键词"""
    ltp = LTP()
    text = Text(ltp, get_abbs('河南易成新能源股份有限公司'), path='text.txt')
    print(text.score())
    # text = Text('甘肃', text='甘肃省因火灾损失了近千万')
    # print(text.score())
