from tqsdk import TqApi, TqAuth
from tqsdk.ta import MA
api = TqApi(auth=TqAuth("信易账号", "密码"),web_gui=True)
# 订阅1分钟K线
kline = api.get_kline_serial("SHFE.rb2105", 60,data_length=100)
# 通过浏览器访问TqSdk指定的地址，需保持程序运行
while True:
    # 计算收盘价的10日简单均线
    ma = MA(kline,10) #均线是包含一列ma的Dataframe格式数据
    # 为K线增加一列ma_MAIN，把均线值赋值给此列
    kline["ma_MAIN"] = ma.ma  # 在主图中画一根默认颜色（红色）的 ma 指标线
    api.wait_update()
api.close()