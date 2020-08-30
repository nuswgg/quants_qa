import QUANTAXIS as QA
import pandas as pd
import tushare as ts
import numpy as np
# import TA-Lib as ta
import scipy.signal as signal
import matplotlib.pyplot as plt

#################################### 常用数据 ####################################
#whole stock list
cn_stk_list = QA.QA_fetch_stock_list()
cn_stk_list = cn_stk_list.loc[~cn_stk_list['name'].str.contains('ST|退')]
cn_stk_code = cn_stk_list['code'].to_list()
# cn_stock_list = QA.QA_fetch_stock_list_adv().code.tolist()
cn_stock_basic = ts.get_stock_basics()
#399300 stock component
hs300component = QA.QA_fetch_stock_block_adv().get_block('沪深300').code
#获取市场的日线数据
cn_1mon_day1_data = QA.QA_fetch_stock_day_adv(cn_stk_code,'2020-05-01','2020-05-22')
#获取沪深300成分股的日线数据
hs_data = QA.QA_fetch_stock_day_adv(hs300component,'2019-10-01','2020-05-09')

#获取市场1周的1分钟数据
cn_1week_min1_data = QA.QA_fetch_stock_min_adv(cn_stk_code,'2020-05-21','2020-05-22','1min')

#获得板块数据
cn_blk = QA.QA_fetch_stock_block_adv()
#               source type
#index
#blockname code tdx     gn

idx_list = QA.QA_fetch_index_list_adv() ##dataframe

#################################### 技术指标 ####################################
# define sma function
def sma_4l(data,n1=5,n2=10,n3=20,n4=40):
     try:
         return pd.DataFrame({'ma1':QA.SMA(data.close,n1),'ma2':QA.SMA(data.close,n2),'ma3':QA.SMA(data.close,n3),'ma4':QA.SMA(data.close,n4)})
     except Exception as e:
         print(e)

def vol_ind(data,n1=6,n2=60,n3=120):
    try:
        return pd.DataFrame({'mv1':QA.MA(data.volume,n1),'mv2':QA.MA(data.volume,n2),'mv3':QA.MA(data.volume,n3),})
    except Exception as e:
        print(e)

 def macd_jcsc(data,short=9,long=12,m=9):
     close = data.close
     diff = QA.EMA(close,short)-QA.EMA(close,long)
     dea = QA.EMA(diff,m)
     macd = 2*(diff - dea)
     jc = QA.CROSS(diff,dea)
     sc = QA.CROSS(dea,diff)
     zero = 0
     return pd.DataFrame({'diff':diff,'dea':dea,'macd': macd, 'jc': jc, 'sc': sc, 'zero': 0})



sma = data2.add_func(sma_4l)

date_index = data2.index.levels[0]

code_index = data2.index.levels[1]
#################################### 市场统计 ####################################
# to show the trend of ifup20

def ifup20(data):
    return (data.close-QA.MA(data.close,20)).dropna()>0
ind1 = data1.add_func(ifup20)
stat1 = ind1.dropna().groupby(level=0).sum()
stat1.plot()

#################################### 市场分类 ####################################
main_idx = ['000001','000016','399300','399005','399006','399106','399295']
# 蓝筹 '000016','399300'，‘399295’
#中小创 '399005','399006','000045' 上证小盘


#################################### 行业概念指数 ####################################

all_blk_component = QA.QA_fetch_stock_block_adv().view_block
all_blk_component['黄金概念']
all_blk_component['半导体']

# idx_wanted = idx_list['880301':'880981'].index.to_list()
idx_wanted = idx_list['880301':'880981']#.name  #dataframe
coal_list = all_blk_component[idx_wanted[1]]
coal_data = QA.QA_fetch_stock_day_adv(coal_list,'2020-01-01','2020-05-01')

# blk_in_opprty to be found through model for blk
# find stk_in_opprty in blk_in_opprty through model for stock

#################################### 多股同图 ####################################
sample = ['600500','000001','600652','600676']
sample_data = QA.QA_fetch_stock_day_adv(sample,'2020-01-01','2020-05-01')
fig = plt.figure(figsize=(12,8))
sample_data.groupby(level=1).close.apply(lambda x:x.plot())

#################################### financial report ####################################
hs_financial = QA.QA_fetch_financial_report_adv(hs300component,'2018-01-01','2020-05-01',ltype='CN')
hs_financial.colunms_cn  #see detail column name


#################################### 分析模型 ####################################
###从个股分析板块
###找出牛股  4天连续涨停 或者更多
#获得沪深300成分股的数据
data_hs300_min1=QA.QA_fetch_stock_min_adv(hs300component,'2020-05-01','2020-05-15')
#找出1分钟张2%的股票
dailymin_data.fast_moving(0.02)
#获取市场的日线数据
cn_1mon_day1_data = QA.QA_fetch_stock_day_adv(cn_stock_list,'2020-04-22','2020-05-22')
#找出涨停的股票
high_limit = cn_1mon_day1_data[cn_1mon_day1_data.close==cn_1mon_day1_data.high_limit]

#找出1分钟拉5%的股票
cn_1week_min1_data.fast_moving(0.05)
#获得股票代码结果
get_code_result = cn_1week_min1_data.fast_moving(0.05).droplevel('datetime',axis=0).index.to_list()

cn_1week_min5_data = QA.QA_fetch_stock_day_adv(cn_stock_list,'2020-05-11','2020-05-15''5min')
get_result = cn_1week_min1_data.fast_moving(0.05).droplevel('datetime',axis=0).index.to_list()



#################################### 涨停分析 ####################################
high_limit = cn_1mon_day1_data[cn_1mon_day1_data.close==cn_1mon_day1_data.high_limit]
#统计每天的涨停个数
high_limit.data.groupby(level=0).count().close

#################################### 异动分析 ####################################
chk_pct = QA.QA_fetch_stock_day_adv(cn_stock_list,'2020-05-21','2020-05-22').to_qfq().close_pct_change()#.reset_index()
df_pct_chg = pd.DataFrame(chk_pct)
one_d_pct_chg = df_pct_chg.loc['2020-05-22'].droplevel('date')
result = one_d_pct_chg[(one_d_pct_chg['close_pct_change']<0.03) & (one_d_pct_chg['close_pct_change']>-0.01)]
result_min = QA.QA_fetch_stock_min_adv(result.index.to_list(),'2020-05-22','2020-05-22','1min')
selection = result_min.fast_moving(0.02).droplevel('datetime',axis=0).index.unique().to_list()
# export data
pd.DataFrame(selection).to_csv('selection.csv')

data = QA.QA_fetch_stock_min_adv(result.index.to_list(),'2020-05-22','2020-05-22')

cn_stock_basic.assign(pct_chg=cn_stock_basic.index.to_list().apply())

yd_data = cn_1mon_day1_data.select_code(high_limit.code).fast_moving(0.02)
yd=yd_data.reset_index().rename(columns={0:'pct_change'})
yd1 = yd[yd.code!='300832']
cn_1mon_day1_data.select_time_with_gap('2020-05-20',2,'gte')


block=QA.QA_fetch_stock_block_adv()
code1=QA.QA_fetch_stock_list_adv().set_index('code')

# yd1.code.apply(lambda x:block.get_code(x).block_name)

#选择每天的每一个时刻(如下午2:30)
data = QA.QA_fetch_future_min_adv('RBL8','2020-07-01','2020-07-20', '15min')
data.data.loc[data.datetime.map(lambda x: x.minute==30 and x.hour==14), slice(None)]

##################################### 财务类分析方法 ####################################
# EPS在过去5季都大于5

num_of_quarter = 5
EPS = 5
para = lambda x: x > EPS

# 方法1
df.data.groupby(level=1).tail(num_of_quarter).query("基本每股收益 > 5").groupby('code').filter(lambda x: len(x) == num_of_quarter)
df.data.groupby(level=1).tail(5).query("基本每股收益 > 2").groupby('code').filter(lambda x: len(x) == 5)['stock_code'].value_counts().index.tolist()

# 方法2
d = df.data.groupby(level=1).tail(num_of_quarter)
d[d['基本每股收益']>EPS].groupby('code').filter(lambda x: len(x) == num_of_quarter)
d[d['基本每股收益'].apply(para)].groupby('code').filter(lambda x: len(x) == num_of_quarter)
# EPS 较去年同期增加10%以上

df.data['past_EPS_pct_c'] = round(df.data.groupby(level=1)['基本每股收益'].pct_change(periods=4) * 100, 2)
df.data.groupby(level=1).tail(1).query('past_EPS_pct_c > 10')
# 营业利润增长率 连续N个季度高于上一季

df.data.rename({'营业利润增长率(%)':'OPGR'}, axis=1, inplace=True)
df.data.groupby(level=1).tail(3).query('OPGR > 0').groupby('code').filter(lambda x: len(x) == 3)
# 营业收入增长率 连续N个季度高于去度同期

num_of_quarter = 3
df.data.rename({'营业收入增长率(%)':'ORS_contrast'}, axis=1, inplace=True)
df.data.groupby(level=1).tail(3).query('ORS_contrast > 0').groupby('code').filter(lambda x: len(x) == 3)
# 累计营业收入 比去年同期增加30%以上

df.data['past_OR_pct_c'] = round(df.data.groupby(level=1)['其中：营业收入'].pct_change(periods=4) * 100, 2)
df.data.groupby(level=1).tail(1).query('past_OR_pct_c > 30')
# 连续N个季度亏损，转盈余

num_of_lose = 3
# 转盈余
num_of_profit = 1

if profit:
    num = num_of_lose + num_of_profit
else:
    num = num_of_lose

if num == num_of_lose:
    df.data.groupby(level=1).tail(num).query('营业收入 < 0').groupby('code').filter(lambda x: len(x) == num)
else:
    date_l = list(set(df.data['report_date']))
    date_l.sort()
    # N个季度亏损
    df.data.groupby(level=1).tail(num).query('report_date < ' + lst[-1*num_of_profit].strftime('%Y%m%d')).query('营业收入 < 0').groupby('code').filter(lambda x: len(x) == num)
    # 转盈余
    df.data.groupby(level=1).tail(num_of_profit).query('营业收入 > 0')

##################################### 一阳穿三线 ####################################
def get_stock(data):
t1=(data.close-data.open).shift().rolling(3).max().apply(lambda x:1 if x<0 else 0)#前三天连续阴线
t2=(data.close-data.close.shift().rolling(3).max()).apply(lambda x:1 if x>0 else 0)#收盘价大于前三天收盘价的最大值
t3=pd.concat([(QA.MA(data.close.shift(),x)-data.close) for x in [5,13,35,55]],axis=1).dropna().min(axis=1).apply(lambda x:1 if x<0 else 0)#当日收盘价大于均价
t4=data.volume.diff().shift().rolling(3).max().apply(lambda x:1 if x<0 else 0)#前三天连续缩量
#t4=pd.concat([QA.CROSS(QA.MA(data.close.shift(),5),QA.MA(data.close.shift(),x) for x in [13,35,55])],axis=1,sort=False).any(axis=1)
res=pd.concat([t1,t2,t3,t4],axis=1,sort=False).all(axis=1)
#print(t3)
return pd.DataFrame({
‘t1’:t1,
‘t2’:t2,
‘t3’:t3,
‘t4’:t4,
‘res’:res})
stock_list = QA.QA_fetch_stock_list_adv()
stocklist_all = stock_list[~stock_list.name.apply(lambda x: ‘ST’ in x)].code.tolist()
data = QA.QA_fetch_stock_day_adv(stocklist_all,‘2019-01-01’,‘2020-02-21’)
ind=data.add_func(get_stock)
ind[ind.res==1].query(‘date>“2020-02-01”’).dropna()

