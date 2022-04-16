from datetime import datetime
from tqsdk import TqApi, TqAuth
from tqsdk.ta import MA
api = TqApi(auth=TqAuth("信易账号", "密码"),web_gui=True)
kline = api.get_kline_serial("SHFE.rb2105", 60,data_length=200)
#定义指标线穿越函数
def cross(api,kline,indicator1:str,indicator2:str):
    for i in range(1,len(kline)):
        # 金叉
        if kline.iloc[-i][indicator1]>kline.iloc[-i][indicator2] and \
           kline.iloc[-i-1][indicator1]<=kline.iloc[-i-1][indicator2]:
            api.draw_text(kline, "买入", x=-i, y=kline.iloc[-i].high + 5, color='red')
        # 死叉
        elif kline.iloc[-i][indicator1]<kline.iloc[-i][indicator2] and \
           kline.iloc[-i-1][indicator1]>=kline.iloc[-i-1][indicator2]:
            api.draw_text(kline, "卖出", x=-i, y=kline.iloc[-i].low - 5, color='green')

# 通过浏览器访问TqSdk指定的地址，需保持程序运行
while True:
    # 计算收盘价的10日简单均线
    ma1 = MA(kline,5)
    ma2 = MA(kline,10)
    # 为K线增加两条均线
    kline["ma1"] = ma1.ma
    kline["ma2"] = ma2.ma
    kline["ma2.color"] = 'blue'
    cross(api,kline,'ma1','ma2')
    api.wait_update()
api.close()