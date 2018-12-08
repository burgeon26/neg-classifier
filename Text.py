import queue
import re

from pyltp import Parser, SementicRoleLabeller, NamedEntityRecognizer
from pyltp import Postagger
from pyltp import Segmentor
from pyltp import SentenceSplitter

import Config
from Tool import *
from ltp import pyltp


class LTP:
    def __init__(self):
        self.segmentor = Segmentor()  # 分词器
        self.segmentor.load_with_lexicon(Config.SEGMENTOR_PATH,
                                         Config.PERSONAL_SEGMENTOR_PATH)  # 加载模型
        self.postagger = Postagger()  # 词性分析器
        self.postagger.load(Config.POSTAGGER_PATH)  # 加载模型
        self.parser = Parser()  # 句法分析器
        self.recognizer = NamedEntityRecognizer()
        self.recognizer.load(Config.NAMED_ENTITY_RECONGNTION_PATH)
        self.parser.load(Config.PARSER_PATH)  # 加载模型
        self.labeller = SementicRoleLabeller()  # 语义角色分析器
        self.labeller.load(Config.LABELLER_PATH)  # 加载模型
        self.negative_list = get_negative_list()
        self.no_list = get_no_list()
        self.limit_list = get_limit_list()
        self.special_list = get_special_list()
        self.key_sentences = []

    def __del__(self):
        """
        资源释放
        """
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()
        self.labeller.release()


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
        self.labeller = ltp.labeller  # 语义角色分析器
        self.recognizer = ltp.recognizer  # 命名实体分析器
        # self.key_sentences = ltp.key_sentences
        self.key_sentences = list()
        self.keywords = keywords
        self.path = path
        self.text = text
        self.read()
        self.negative_list = ltp.negative_list
        self.no_list = ltp.no_list
        self.limit_list = ltp.limit_list
        self.special_list = ltp.special_list
        self.neg_human = list()
        self.neg_org = list()
        self.all_score = 0
        self.stopwords = get_stop_words_list()

    @staticmethod
    def line_spilt(lines, split_word):
        """
        对字符串列表里的字符串按照一定规则进行分割
        :param lines: 待分割字符串列表
        :param split_word: 分割字符
        :return: 分割后的字符串组成的列表
        """
        temp = []
        for line in lines:
            temp.extend(line.split(split_word))
        return filter(lambda x: x != '', temp)

    @staticmethod
    def js_code_check(lines):
        """
        检查字符串是否为JS代码，如果为JS代码，则不进行处理
        :param lines: 待检查字符串列表
        :return: 合法字符串列表
        """
        temp = []
        for line in lines:
            english_num = 0
            if '=' in line:
                for c in line:
                    if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
                        english_num += 1
            if english_num < 10:
                temp.append(line)
        return temp

    def read(self):
        """
        读取文件/文本
        """
        self.sentences.clear()
        if self.path != '':
            lines = read_from_file(self.path)
        else:
            lines = [self.text]
        lines = self.js_code_check(lines)
        split_words = ['\n', '\t', '。', '&nbsp;', '！', '；', '，', '】', '【', '@#$%']
        for split_word in split_words:
            lines = self.line_spilt(lines, split_word)
        for line in lines:
            if len(line) < 1000:
                self.sentences.extend(SentenceSplitter.split(line))
            else:
                sents = line.split("。")
                for sent in sents:
                    self.sentences.extend(SentenceSplitter.split(sent))

    @staticmethod
    def split_insert(key, origin_key, word, temp):
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
        文章/文本负面分数计算
        :return: 总分数,>0代表文本为正面文本，<0代表文本为负面文本
        """
        all_score = 0
        for sentence in self.sentences:
            # key_word_mark = self.keywords[0]
            hn_names, cp_names = pyltp(sentence, self.segmentor, self.postagger, self.recognizer)  # 实体识别
            '''取关键词'''
            if not self.keywords:
                if len(cp_names) > 0:
                    self.keywords.append(cp_names[0])
                    self.neg_human.extend(cp_names)
                    self.neg_org = list()
                elif len(hn_names) > 0:
                    self.keywords.append(hn_names[0])
                    self.neg_human.extend(hn_names)

            key_word_mark = ''
            for key_word in self.keywords:
                if key_word in sentence:
                    sentence = sentence.replace(key_word, '^')  # 分词前，替换关键词，防止关键词分割
                    key_word_mark = key_word
                    break
            negative_mark = ''
            for negative_word in self.negative_list:
                negative_word = negative_word.word
                if negative_word in sentence:
                    sentence = sentence.replace(negative_word, '①')  # 分词前，替换关键词，防止关键词分割
                    negative_mark = negative_word
                    break
            if negative_mark == '':
                continue

            words = self.word_split(sentence)
            temp = []
            for word in words:
                if '①' in word and '^' in word:
                    indexa = word.index('①')
                    indexb = word.index('^')
                    split_word = re.split('[①^]', word)
                    if indexa < indexb:
                        temp.extend([split_word[0], negative_mark, split_word[1], key_word_mark, split_word[2]])
                    else:
                        temp.extend([split_word[0], key_word_mark, split_word[1], negative_mark, split_word[2]])
                elif '①' in word:
                    self.split_insert('①', negative_mark, word, temp)
                elif '^' in word:
                    self.split_insert('^', key_word_mark, word, temp)
                else:
                    temp.append(word)
            words = temp  # 恢复单词列表
            self.tmp_sent_words = words
            postags = self.part_mark(words)  # 词性标注
            arcs = self.syntactic_dependency(words, postags)  # 句法依存
            now_score = self.dependence_score(key_word_mark, words, postags, arcs)  # 句法依存正负面判断
            if now_score > 0:
                self.key_sentences.append(''.join(words))
            all_score += now_score
        self.all_score = all_score
        return all_score

    def print_json(self):
        """
        输出分析结果集合
        :return:
        """
        result = json.dumps({'score': self.all_score,'neg':self.neg_human+self.neg_org, 'neg_sentence': self.key_sentences}, ensure_ascii=False)
        return result

    def negative_dfs(self, pos):
        """
        从企业关键词开始查找中心负面词
        :param pos:企业简称位置
        :return: 负面词权重（如果权重为0，则代表没有负面词）
        """
        if pos == -1:
            return 0, -1
        for word in self.negative_list:
            if self.tmp_sent_words[pos] == word.word:
                # print(word.word)
                return word.weight, pos
        return self.negative_dfs(self.nodes[pos].father)

    def limit_dfs(self, pos):
        """
        从限定词和否定词位置开始向上DFS查找是否修饰负面词
        :return: 是否存在限定词和否定词修饰
        """
        for word in (self.limit_list + self.no_list):
            if word in self.tmp_sent_words:
                # print(word)
                weight, find_pos = self.negative_dfs(self.tmp_sent_words.index(word))
                if find_pos == pos:
                    return False
        # print('good')
        return True

    def passive_check(self, key_word, negative_pos, arc):
        """
        被动语态检查
        例如'鸿道集团被王老吉投诉，告上法庭'，这里的王老吉处于被和负面词之间，因此负面词修饰的不是王老吉，在判定时需要进行过滤
        特殊词检查
        例如'A公司投诉B公司'，这里A公司在句子中所处的位置关系为SBV，因此判定投诉对于A无效
        :param key_word: 企业简称
        :param negative_pos: 负面词位置
        :param arc: 语法依存关系
        :return: True代表关键词不位于无效位置，False代表关键词位于无效位置
        """
        if '被' in self.tmp_sent_words:
            passive_index = self.tmp_sent_words.index('被')
            sub_str = ''.join(self.tmp_sent_words[passive_index + 1:negative_pos])
            if key_word in sub_str:
                return False
        # 特殊词检查,不能为SBV关系
        if self.tmp_sent_words[negative_pos] in self.special_list:
            if arc.relation == 'SBV':
                return False
        return True

    def dependence_score(self, key_word, words, postags, arcs):
        """
        句法依存负面判定算法，如果句法依存负面判定算法无法判定正负面，将自动调用语义角色判定算法
        :param key_word:企业简称
        :param words:单词集合
        :param postags: 词性标注列表
        :param arcs:依存关系集合
        :return:评分
        """
        # print('调用句法依存')
        # print(key_word)
        self.nodes = [Node() for i in range(len(words))]
        for pos, arc in zip(range(len(arcs)), arcs):
            self.nodes[pos].father = arc.head - 1
            self.nodes[pos].tag = arc.relation
            self.nodes[arc.head - 1].son.append(pos)

        if not key_word:
            for i,seg_word in enumerate(words):
                for word in self.negative_list:
                    if seg_word == word.word:
                        # print(word.word)
                        source_pos = negative_pos = i
                        score = word.weight
                        break
        else:
            source_pos = list(words).index(key_word)
            score, negative_pos = self.negative_dfs(source_pos)
        # print(score)
        # score = 0
        # negative_pos = -1
        if score != 0 and self.limit_dfs(negative_pos) and self.passive_check(key_word, negative_pos, arcs[source_pos]):
            return score
        if len(''.join(words)) < 80:
            return self.role_score(key_word, words, postags, arcs)
        else:
            return 0

    def role_score(self, key_word, words, postags, arcs):
        """
        基于语义角色标注的负面算法
        :param key_word: 企业关键词
        :param words:单词列表
        :param postags:词性标注列表
        :param arcs:语法依存关系列表
        :return:评分
        """
        roles = self.labeller.label(words, postags, arcs)  # 语义角色标注
        score = 0
        for role in roles:
            # print(role.index, "".join(
            #     ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end)
            #      for arg in role.arguments]))
            # print(words[role.index])
            for negative_word in self.negative_list:
                if words[role.index] == negative_word.word:
                    for argument in role.arguments:
                        if argument.name == 'A0' and words[role.index] not in self.special_list and key_word in ''.join(
                                words[argument.range.start:argument.range.end + 1]):
                            # print('A0',''.join(words[argument.range.start:argument.range.end+1]))
                            score += negative_word.weight
                        elif argument.name == 'A1' and key_word in ''.join(
                                words[argument.range.start:argument.range.end + 1]):
                            # print('A1',''.join(words[argument.range.start:argument.range.end+1]))
                            score += negative_word.weight
        if score != 0:
            return score
        return 0

    def word_split(self, sent):
        """
        单词分割
        :param sent:句子
        :return: 单词集合
        """
        words = self.segmentor.segment(sent)  # 单词分割
        return words

    def word_count(self,stopwords=False):
        """
        单词频率统计，用于词库统计分析模块
        :return: 单词统计表
        """
        count = {}
        for sent in self.sentences:
            words = self.word_split(sent)
            for word in words:
                if stopwords and word in self.stopwords:
                    continue
                if word in count.keys():
                    count[word] += 1
                else:
                    count[word] = 1
        return count

    def word_count_by_type(self, type=''):
        """
        特定词性的单词频率统计，用于单词推荐模块
        :return: 单词统计表
        """
        count = {}
        for sent in self.sentences:
            words = self.word_split(sent)
            postags = self.part_mark(words)
            for word, postag in zip(words, postags):
                if postag == type:
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
    # 句法依存树结点
    def __init__(self):
        self.father = -1
        self.son = []
        self.tag = None
