from pyltp import Parser
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import SentenceSplitter

from Tool import *
from Word import Word


class LTP:
    def __init__(self):
        self.segmentor = Segmentor()  # 分词器
        self.segmentor.load("/home/zhenlingcn/Desktop/ltp_data/cws.model")  # 加载模型
        self.postagger = Postagger()  # 词性分析器
        self.postagger.load("/home/zhenlingcn/Desktop/ltp_data/pos.model")  # 加载模型
        self.parser = Parser()  # 句法分析器
        self.parser.load("/home/zhenlingcn/Desktop/ltp_data/parser.model")  # 加载模型
        self.negative_list = get_negative_list()
        self.no_list = get_no_list()
        self.limit_list = get_limit_list()

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
        self.no_list = ltp.no_list
        self.limit_list = ltp.limit_list

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

    def split_insert(self, key, origin_key, word, temp):
        """
        由于分词系统存在特殊替换字符和普通词语黏连的情况，因此需要进行剥离
        :param key: 特殊替换字符
        :param origin_key:被替换字符串（源字符串）
        :param word: 待剥离字符串
        :param temp: 临时存储列表
        """
        if isinstance(key, list):
            if word.split(key)[0] != '':
                temp.append(word.split(key)[0])
            temp.append(origin_key)
            if word.split(key)[1] != '':
                temp.append(word.split(key)[1])
        else:
            temp.append(origin_key)

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
                    sentence = sentence.replace(key_word, '^')  ##分词前，替换关键词，防止关键词分割
                    key_word_mark = key_word
                    break
            negative_mark = ''
            for negative_word in self.negative_list:
                negative_word = negative_word.word
                if negative_word in sentence:
                    sentence = sentence.replace(negative_word, '①')  ##分词前，替换关键词，防止关键词分割
                    negative_mark = negative_word
                    break
            if key_word_mark == '' or negative_mark == '':
                continue

            words = self.word_split(sentence)
            temp = []
            for word in words:
                if '①' in word:
                    self.split_insert('①', negative_mark, word, temp)
                elif '^' in word:
                    self.split_insert('^', key_word_mark, word, temp)
                else:
                    temp.append(word)
            words = temp  # 恢复单词列表
            self.words=words
            postags = self.part_mark(words)  # 词性标注
            # print(list(words))
            arcs = self.syntactic_dependency(words, postags)  # 句法依存
            # print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
            all_score += self.dependence_score(key_word_mark, words, arcs)
        return all_score

    def negative_dfs(self, pos):
        """
        从企业关键词开始查找中心负面词
        :param pos:企业简称位置
        :return: 负面词权重（如果权重为0，则代表没有负面词）
        """
        if pos == -1:
            return 0, -1
        for word in self.negative_list:
            if self.words[pos] == word.word:
                # print(word.word)
                return word.weight, pos
        return self.negative_dfs(self.nodes[pos].father)

    def limit_dfs(self,pos):
        """
        从限定词和否定词位置开始向上DFS查找是否修饰负面词
        :return: 是否存在限定词和否定词修饰
        """
        for word in (self.limit_list + self.no_list):
            if word in self.words:
                # print(word)
                weight,find_pos=self.negative_dfs(self.words.index(word))
                if find_pos==pos:
                    return False
        # print('good')
        return True

    def passive_check(self, key_word, negative_pos):
        """
        被动语态检查
        例如'鸿道集团被王老吉投诉，告上法庭'，这里的王老吉处于被和负面词之间，因此负面词修饰的不是王老吉，在判定时需要进行过滤
        :param key_word: 企业简称
        :param negative_pos: 负面词位置
        :return: True代表关键词不位于无效位置，False代表关键词位于无效位置
        """
        if '被' in self.words:
            passive_index = self.words.index('被')
            sub_str = ''.join(self.words[passive_index + 1:negative_pos])
            if key_word in sub_str:
                return False
        return True

    def dependence_score(self, key_word, words, arcs):
        """
        核心算法：句法依存，如果句法依存算法无法判定正负面，将自动调用简化格语法算法
        :param key_words:企业简称列表
        :param words:单词集合
        :param arcs:依存关系集合
        :return:评分
        """
        # print('调用句法依存')
        # print(key_word)
        self.nodes = [Node() for i in range(len(words))]
        for pos, arc in zip(range(len(arcs)), arcs):
            self.nodes[pos].father = arc.head - 1
            self.nodes[arc.head - 1].son.append(pos)
        pos = list(words).index(key_word)
        score, negative_pos = self.negative_dfs(pos)
        # print(score)
        if score != 0 and self.limit_dfs(negative_pos) and self.passive_check(key_word, negative_pos):
            return score
        return 0
        # 由于简化格语法算法过于粗糙，此处不考虑使用
        # return self.case_grammar_score(words)

    def case_grammar_score(self, words):
        """
        简化格语法评分
        :param words:单词集合
        :return:评分
        """
        score = 0
        for word in words:
            for negative_word in self.negative_list:
                if word == negative_word.word:
                    score += negative_word.weight
        return score

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


class Node:
    def __init__(self):
        self.father = -1
        self.son = []
