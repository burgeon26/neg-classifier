# 辅助工具相关配置
WORD_COUNT_PATH = '/Users/xesdiny/workspace/python/webtext-classifier/Data/content'  # 词库统计模块分析的目录
WORD_COUNT_SAVE_PATH = '/Users/xesdiny/workspace/python/webtext-classifier/Data/wordscount.txt'  # 词库统计分析结果保存路径
RECOMMEND_PATH = '/home/zhenlingcn/Desktop/test/content'  # 单词推荐模块分析目录
RECOMMEND_SAVE_PATH = '/home/zhenlingcn/Desktop/test/recommend.txt'  # 推荐单词列表保存路径
STOP_WORD_PATH = '/Users/xesdiny/wnd/data/Chinese/stopwords.dat' # 停用词保存路径
#测评模块配置
LOG_PATH='/home/zhenlingcn/Desktop/test/log.log'    #测评记录日志路径，用于异常恢复
REVIEW_OUTPUT_PATH='/home/zhenlingcn/Desktop/test/key.txt' #测评结果输出路径
REVIEW_PATH='/home/zhenlingcn/Desktop/report_analysis_intel'    #测评目录
# 核心类配置
SEGMENTOR_PATH = '/Users/xesdiny/wnd/data/Chinese/ltp_model/cws.model'  # 分词模型路径
PERSONAL_SEGMENTOR_PATH = 'Data/word.txt'  # 自定义词库路径
POSTAGGER_PATH = '/Users/xesdiny/wnd/data/Chinese/ltp_model/pos.model'  # 词性标注模型路径
NAMED_ENTITY_RECONGNTION_PATH = '/Users/xesdiny/wnd/data/Chinese/ltp_model/ner.model'   # 命名实体识别模型路径
PARSER_PATH = '/Users/xesdiny/wnd/data/Chinese/ltp_model/parser.model'  # 语法依存模型路径
LABELLER_PATH = '/Users/xesdiny/wnd/data/Chinese/ltp_model/pisrl.model'  # 语义角色模型路径

# 词库配置
NEGATIVE_CORE_WORD='Data/negative_core_word.txt' #核心负面词
NO_WORD='Data/no_word.txt'   #否定词
LIMIT_WORD='Data/limit_word.txt' #限定词
SPECIAL_WORD='Data/special_word.txt' #修饰词
#企业简称接口
ABBS_URL='http://218.77.58.173:5005/api/abb'