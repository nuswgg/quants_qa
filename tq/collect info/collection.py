# 引入TqSdk模块
from tqsdk import TqApi, TqAuth
# 创建api实例，设置web_gui=True生成图形化界面
api = TqApi(web_gui="http://192.168.1.4:9875", auth=TqAuth("nuswgg", "541278"))
# 订阅 cu2002 合约的10秒线

#获取中金所所有的当前合约
# curr_f =api.query_cont_quotes("CFFEX")

#获取所有的交易所期货的交易时间段
exchange = ["CFFEX","SHFE","DCE","CZCE","INE"]
for x in exchange:
    curr_f = api.query_cont_quotes(x)
    for fut in curr_f:
        quote = api.get_quote(fut)
        trading_p = quote.trading_time
        print(fut,trading_p)

while True:
    # 通过wait_update刷新数据
    api.wait_update()