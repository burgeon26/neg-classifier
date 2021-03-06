# 互联网文本正负面判断和严重程度分级
项目结构  
- Tool 核心判定算法类  
- Config 核心配置类  
- Demo 演示示例  
- Tool 工具类  
- Word 负面单词类  
- Assist  
    - ReviewTool 系统评测模块
    - WordCount 词库分析统计模块
    - WordRecommend 词库推荐模块
- Data
    - negative_core_word.txt 负面核心词汇表
    - no_word.txt 否定词汇表
    - limit_word.txt 限定词汇表
    - passive_word.txt 特殊修饰词汇表
    - text.txt 供Demo调试使用的文本  
    - word.txt 商业词汇词库文件

关于特殊修饰词汇表
有一些负面词企业关键词可以同时作为施事者和受事者，例如A公司举报B公司，这里B公司是受事者，从语义角色上来判断，也就是A公司处于A0角色，B公司处于A1角色，举报这个行为仅针对A1有效。

算法思路  
判定算法主要分为两部分：句法依存和语义角色  
句法依存部分算法流程如下：
1. 首先查找企业关键词是否存在于句子中
2. 查找有负面词为关键词的祖先，若有，此句话赋分
3. 查找负面词是否有否定词和限定词修饰，如果存在修饰，则此句话分数置零
4. 查找是否为被动语态，如果恰好处于“被..负面词”这种结构中间，例如“被（华为）举报”，那么被动语态
5. 如果公司关键词处于特殊修饰词位置，且为SBV，即主语位置。则此句话分数置零（例如“（华为）举报XX”）
6. 如果分数为0，则调用语义角色分析（由于语义角色分析所需内存较大，因此如果句子长度》=80，则不进行语义角色分析）

语义角色分析算法流程如下：
1. 首先查找是否有谓词为负面词，如果存在负面词，在继续下一步操作
2. 分析语义角色，如果为A0，则为施事格，如果为A1，则为受事格。如果公司关键词处于施事格，且负面词不是特殊修饰词，则判定为负面消息。如果公司关键词处于受事格，则判定为负面消息。


更新日志 

2018.01.26
1. 完成词库推荐模块，基于词性推荐，暂时不能自动分类正面次和负面词
2. 提取配置路径，相关路径配置可在Config.py中统一配置

2018.01.25
1. 算法优化，结合语义角色分析模块进行负面消息判定
2. 引入特殊修饰词概念，例如“举报”，特殊修饰词之前的词语不判定为负面
3. 基于搜狗、百度、腾讯细胞词库制作商业领域词库12万条
4. 系统评测模块支持断点恢复，自动记录异常断点，下次运行从异常断点处运行

2018.01.24
1. 判定逻辑增强，删去了简化格语法判定，所有判定算法全部基于句法依存实现，可以保证极高的精确率。目前召回率较低，粗略估计只有20%
2. 删除正面词词典，改用限定词和否定词词典

2018.01.23
1. 完成词库分析统计模块，可以扫描整个数据文件夹，分析词库质量，并进行词条优化
2. 完成系统评测模块，支持自动读取文件夹中的Excel，自动提取公司名称，自动读取相应文件，自动判断新闻属性并给出模型评测报告
3. 优化词库，词库规模缩小85%  
4. 强化算法，利用企业名简称接口强化新闻识别的准确率  
5. 优化代码逻辑，修复BUG  

2018.01.22  
1. 项目初始化，完成基本判断算法