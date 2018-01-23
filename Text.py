from pyltp import Parser
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import SentenceSplitter

from Tool import get_positive_list, get_negative_list
from Tool import read_from_file


class LTP:
    def __init__(self):
        self.segmentor = Segmentor()  # 分词器
        self.segmentor.load("/home/zhenlingcn/Desktop/ltp_data/cws.model")  # 加载模型
        self.postagger = Postagger()  # 词性分析器
        self.postagger.load("/home/zhenlingcn/Desktop/ltp_data/pos.model")  # 加载模型
        self.parser = Parser()  # 句法分析器
        self.parser.load("/home/zhenlingcn/Desktop/ltp_data/parser.model")  # 加载模型
        self.negative_list = get_negative_list()
        self.positive_list = get_positive_list()

    def __del__(self):
        """
        资源释放
        """
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()


class Text:
    sentences = []

    def __init__(self, ltp: LTP, keywords, path='', text=''):
        """
        初始化(需要注意，存在文本路径的时候，文本内容会失效)
        :param ltp: LTP
        :param keywords: 企业简称列表
        :param path: 文本路径
        :param text: 文本内容
        """
        self.segmentor = ltp.segmentor  # 分词器
        self.postagger = ltp.postagger  # 词性分析器
        self.parser = ltp.parser  # 句法分析器
        self.keywords = keywords
        self.path = path
        self.text = text
        self.read()
        self.negative_list = ltp.negative_list
        self.positive_list = ltp.positive_list

    def read(self):
        """
        读取文件/文本
        """
        self.sentences.clear()
        if self.path != '':
            lines = read_from_file(self.path)
        else:
            lines = [self.text]
        for line in lines:
            if len(line) < 1000:
                self.sentences.extend(SentenceSplitter.split(line))
            else:
                sents = line.split("。")
                for sent in sents:
                    self.sentences.extend(SentenceSplitter.split(sent))

    def score(self):
        """
        文章/文本分数计算
        :return: 总分数,>0代表文本为正面文本，<0代表文本为负面文本
        """
        all_score = 0
        for sentence in self.sentences:
            key_word_mark = ''
            for key_word in self.keywords:
                if key_word in sentence:
                    sentence = sentence.replace(key_word, '^')
                    key_word_mark = key_word
                    break
            # print(sentence)
            words = self.word_split(sentence)
            # print(list(words))
            words = list(map(lambda x: [x.split('^')[0], '^', x.split('^')[1]] if '^' in x else x, words))
            temp = []
            for word in words:
                if isinstance(word, list):
                    temp.extend(x for x in word if x != '')
                else:
                    temp.append(word)
            words = temp
            # foreach(print,words)
            # print(list(words))
            if key_word_mark != '':
                words[list(words).index('^')] = key_word_mark
            # print('\n'.join(words))
            postags = self.part_mark(words)
            arcs = self.syntactic_dependency(words, postags)
            all_score += self.dependence_score(self.keywords, words, arcs)
        return all_score

    def dependence_score(self, key_words, words, arcs):
        """
        句法依存，如果句法依存算法无法判定正负面，将自动调用简化格语法算法
        :param key_words:企业简称列表
        :param words:单词集合
        :param arcs:依存关系集合
        :return:评分
        """
        for key_word in key_words:
            try:
                pos = list(words).index(key_word)
                score = 0
                while pos != -1:
                    if words[pos] in self.negative_list:
                        score -= 2
                    elif words[pos] in self.positive_list:
                        score += 1
                    pos = arcs[pos].head - 1
                if score != 0:
                    return score
            except ValueError:
                pass
        return self.case_grammar_score(key_words, words)

    def case_grammar_score(self, key_words, words):
        """
        简化格语法评分
        :param key_words:企业简称列表
        :param words:单词集合
        :return:评分
        """
        score = 0
        effective = False
        for word in words:
            if word in key_words:
                effective = True
            else:
                if word in self.negative_list:
                    score -= 2
                elif word in self.positive_list:
                    score += 1
        if effective:
            return score
        else:
            return 0

    def word_split(self, sent):
        """
        单词分割
        :param sent:句子
        :return: 单词集合
        """
        words = self.segmentor.segment(sent)  # 单词分割
        return words

    def word_count(self):
        count = {}
        for sent in self.sentences:
            words = self.word_split(sent)
            for word in words:
                if word in count.keys():
                    count[word] += 1
                else:
                    count[word] = 1
        return count

    def part_mark(self, words):
        """
        词性标注
        :param words:单词集合
        :return: 词性集合
        """
        postags = self.postagger.postag(words)  # 词性标注
        return postags

    def syntactic_dependency(self, words, postags):
        """
        句法分析
        :param words:单词集合
        :param postags: 词性集合
        :return: 依存关系集合（即句中单词关系集合）
        """
        arcs = self.parser.parse(words, postags)  # 句法分析
        return arcs
