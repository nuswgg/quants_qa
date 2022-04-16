# https://zhuanlan.zhihu.com/p/364825694

import pandas as pd
url = 'http://www.shfe.com.cn/products/cu/' #上期所铜结算参数地址
data =pd.read_html(url) #读取网页上的表格
dt=data[4].drop([0],axis=0).append(data[5],ignore_index=True) #提取结算参数到DataFrame格式
#调整格式
dt.columns=dt.iloc[0]
dt.drop([0],axis=0,inplace=True)
dt.set_index('合约代码',inplace=True)
print(dt) #输出铜的结算参数
print(float(dt['投机买(%)']['cu2109'])) #铜cu2109的保证金比例
print(float(dt['交易手续费率(‰)']['cu2109'])) #铜cu2109的手续费率
print(float(dt['交易手续费额(元/手)']['cu2109'])) #铜cu2109的手续费额