# 引入TqSdk模块
from tqsdk import TqApi, TqAuth,TqSim
# 创建api实例，设置web_gui=True生成图形化界面
api = TqApi(TqSim(init_balance=100000), auth=TqAuth("nuswgg", "541278"))

# 订阅 cu2002 合约的10秒线
klines = api.get_kline_serial("SHFE.cu2105", 60)
quote = api.get_quote("SHFE.cu2105")
while True:
    # 通过wait_update刷新数据
    api.wait_update()
    print(quote.last_price)