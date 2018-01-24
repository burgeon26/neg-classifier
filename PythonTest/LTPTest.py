# from pyltp import SentenceSplitter
#
# sents = SentenceSplitter.split('元芳你怎么看？我就趴窗口上看呗！')  # 分句
# print('\n'.join(sents))

from pyltp import Segmentor
from Tool import clear, foreach

segmentor = Segmentor()  # 初始化实例
segmentor.load("/home/zhenlingcn/Desktop/ltp_data/cws.model")  # 加载模型
sent=clear('合法权益得不到有效保障')
print(sent)
words = segmentor.segment(sent)  # 分词
# print(len(words))
# foreach(print,words)
print('   '.join(words))
segmentor.release()  # 释放模型

from pyltp import Postagger

postagger = Postagger()  # 初始化实例
postagger.load("/home/zhenlingcn/Desktop/ltp_data/pos.model")  # 加载模型

postags = postagger.postag(words)  # 词性标注

print('\t'.join(postags))
postagger.release()  # 释放模型

from pyltp import NamedEntityRecognizer

recognizer = NamedEntityRecognizer()  # 初始化实例
recognizer.load("/home/zhenlingcn/Desktop/ltp_data/ner.model")  # 加载模型

netags = recognizer.recognize(words, postags)  # 命名实体识别

print('\t'.join(netags))
recognizer.release()  # 释放模型

from pyltp import Parser

parser = Parser()  # 初始化实例
parser.load("/home/zhenlingcn/Desktop/ltp_data/parser.model")  # 加载模型

arcs = parser.parse(words, postags)  # 句法分析

print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
parser.release()  # 释放模型

from pyltp import SementicRoleLabeller

labeller = SementicRoleLabeller()  # 初始化实例
labeller.load("/home/zhenlingcn/Desktop/ltp_data/pisrl.model")  # 加载模型

# arcs 使用依存句法分析的结果
roles = labeller.label(words, postags, arcs)  # 语义角色标注

# 打印结果
for role in roles:
    print(role.index, "".join(
        ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end)
         for arg in role.arguments]))
labeller.release()  # 释放模型
