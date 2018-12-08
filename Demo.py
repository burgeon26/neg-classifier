from Text import Text, LTP
from Tool import *
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
import json,os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']=\
    'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
db=SQLAlchemy(app)

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String(30))
    degree = db.Column(db.Integer)
    craw_text = db.Column(db.Text)
    score = db.Column(db.Integer)
    neg = db.Column(db.String(20))
    neg_sentence = db.Column(db.Text)

@app.route('/search',methods=['GET', 'POST'])
def search_form():
    data = {'title': '', 'information': ''}

    db.drop_all()
    db.create_all()
    f = open("/home/shimeng.zhan/res.txt", "r")
    for line in f.readlines()[0:100]:
        line = line.replace('\'', '\"')
        line = json.loads(line)
        if len(line['neg']) > 0:
            # print(line)
            record = News(time=line['time'], degree=line['degree'], craw_text=line['craw_text'], score=line['score'],
                          neg=line['neg'][0], neg_sentence=line['neg_sentence'][0])
            db.session.add(record)

    f.close()
    page = request.args.get('page', 1, type=int)
    pagination = News.query.order_by(News.id.desc()).paginate(page, per_page=10, error_out=False)

    if request.method =='GET':
        return render_template('search.html',data=data,pagination=pagination)
    else:
        text=request.form['text'].strip()
        if text:
            return send_post(text,pagination=pagination)
        else:
            return render_template('search.html',data=data,tips="请输入关键词！",pagination=pagination)

def send_post(text,pagination):

    text = Text(ltp, get_abbs(''), text=clear(text))
    text.score()
    text_print = text.print_json()
    data = {'title': text, 'information': text_print}

    return render_template('search.html',data=data,pagination=pagination)


@app.route('/index',methods=['GET', 'POST'])
def index():
    db.drop_all()
    db.create_all()
    f = open("/home/shimeng.zhan/res.txt", "r")
    for line in f.readlines()[0:100]:
        line = line.replace('\'','\"')
        line=json.loads(line)
        if len(line['neg'])>0:
            # print(line)
            record = News(time=line['time'],degree=line['degree'],craw_text=line['craw_text'],score=line['score'],neg=line['neg'][0],neg_sentence=line['neg_sentence'][0])
            db.session.add(record)

    f.close()
    page = request.args.get('page', 1, type=int)
    pagination = News.query.order_by(News.id.desc()).paginate(page, per_page=10, error_out=False)

    # users = pagination.items
    return render_template('index.html', pagination=pagination)

def read_txt():
    f = open('/home/shimeng.zhan/wallstreet_news.txt', 'r')
    f2 = open("/home/shimeng.zhan/res.txt", "a+")
    for line in f.readlines()[0:2000]:
        line=line.strip()
        line=line.replace('@#$%','')
        if not len(line) or line.startswith('#'):  # 判断是否是空行或注释行
            continue
        # print(line.split('\t'))
        result = line.split('\t')
        if len(result) == 3:
            text = Text(ltp, get_abbs(''), text=clear(result[2]))
            text.score()
            text_print = text.print_json()
            t2 = json.loads(text_print)
            # print(text_print)
            if t2['score'] > 1:
                t2['time'] = result[0]
                t2['degree'] = result[1]
                t2['craw_text'] = result[2]
                print(t2)
                f2.write(str(t2) + "\n")
    f.close()
    f2.close()


if __name__ == '__main__':
    ltp = LTP()
    # text = Text(ltp, get_abbs('众安在线财产保险股份有限公司'), path='Data/text.txt')
    # print(text.score())
    # print(get_abbs('北京京东股份有限公司'))
    # print(clear('( 鸿道集团) 被王老吉［投诉］，告上法庭．'))

    app.run()
    # read_txt()

    # text = Text(ltp,get_abbs(''), text=clear(''))
    # text.score()
    # print(text.print_json())

    #道指结束连涨三天的表现，投资者情绪谨慎】@#$%标普500指数收跌5.99点，跌幅0.22%，报2737.80点。@#$%道琼斯工业平均指数收跌27.59点，跌幅0.11%，报25338.84点。@#$%纳斯达克综合指数收跌18.51点，跌幅0.25%，报7273.08点。@#$%
    # 美图手机延续上日跌势，一度跌7%，目前略收窄至6.5%；昨日大跌15.88%。
    # 绿光资本旗舰基金11月亏损3.5%，今年以来累计亏损28%。
    # 绿光资本旗舰基金11月并没有亏损3.5%，今年以来累计亏损28%。
    # 银保监会官员：处置不良资产慎用查封冻结措施】银保监会法规部副主任张劲松：一些金融企业包括债权人往往利用债权人的优势，在诉讼中采取查封、冻结企业账户的行为，往往导致处于困境的企业面临破产，给社会经济的发展带来非常大的麻烦，下一步要进一步规范。市场经济是信用经济，要倡导在平等协商的基础上解决问题，不能因为维护自身合法权益而不顾对方合法权益。（中证网）@#$%