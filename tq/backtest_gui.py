from datetime import date
from tqsdk import TqApi, TqAuth, TqBacktest, TargetPosTask,tafunc
# 在创建 api 实例时传入 TqBacktest 就会进入回测模式,设置web_gui=True开启图形化界面
# api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 18)),web_gui="http://192.168.1.4:9876", auth=TqAuth("nuswgg", "541278"))
# api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 18)),web_gui="http://172.16.83.232:9876", auth=TqAuth("nuswgg", "541278"))
api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 10), end_dt=date(2021, 3, 18)),web_gui="http://192.168.43.176:9876", auth=TqAuth("nuswgg", "541278"))
# 获得 SHFE.cu2105 5分钟K线的引用
# klines = api.get_kline_serial("SHFE.cu2105", 5 * 60, data_length=15)
# 创建 cu2105 的目标持仓 task，该 task 负责调整 cu2105 的仓位到指定的目标仓位
# target_pos = TargetPosTask(api, "SHFE.cu2105")
# while True:
#     api.wait_update()
#     if api.is_changing(klines):
#         ma = sum(klines.close.iloc[-15:]) / 15
#         print("最新价", klines.close.iloc[-1], "MA", ma)
#         if klines.close.iloc[-1] > ma:
#             print("最新价大于MA: 目标多头5手")
#             # 设置目标持仓为多头5手
#             target_pos.set_target_volume(5)
#         elif klines.close.iloc[-1] < ma:
#             print("最新价小于MA: 目标空仓")
#             # 设置目标持仓为空仓
#             target_pos.set_target_volume(0)

##############################################################################
# quote = api.get_quote('CFFEX.IF2104') #订阅盘口行情
# kline = api.get_kline_serial('CFFEX.IF2104',60,5) #订阅1分钟k线5根
# target_pos = TargetPosTask(api, "CFFEX.IF2104") #设置调仓task，默认对手价下单
# while True:
#     # 前一根K线收盘价低于结算价，最新一根收盘价高于结算价
#     # 应该等最新一根K收完避免信号闪烁，收完序号即变为-2
#     if kline.iloc[-3].close < quote.average and kline.iloc[-2].close > quote.average:
#         target_pos.set_target_volume(2) #设置为多头2手
#     # 收盘价下穿结算价
#     elif kline.iloc[-3].close > quote.average and kline.iloc[-2].close < quote.average:
#         target_pos.set_target_volume(-2) #设置为空头2手
#     api.wait_update()
#

###########################################################################
# 双均线策略

quote = api.get_quote('CFFEX.IF2104') #订阅盘口行情
kline = api.get_kline_serial('CFFEX.IF2104', 60, 200) #订阅1分钟k线5根
target_pos = TargetPosTask(api, "CFFEX.IF2104") #设置调仓task，默认对手价下单
# MaLong = tafunc.ma(kline.close, 20)  # 计算20日均线
# MaShort = tafunc.ma(kline.close, 10)  # 计算10日均线
while True:
    MaLong = tafunc.ma(kline.close, 20)  # 计算20日均线
    MaShort = tafunc.ma(kline.close, 10)  # 计算10日均线
    # 金叉
    if MaShort.iloc[-2]>MaLong.iloc[-2] and MaShort.iloc[-4]<MaLong.iloc[-4]:
        target_pos.set_target_volume(2) #设置为多头2手
    # 死叉
    elif MaShort.iloc[-2]<MaLong.iloc[-2] and MaShort.iloc[-4]>MaLong.iloc[-4]:
        target_pos.set_target_volume(-2) #设置为多头2手
    api.wait_update()
    print(MaShort.iloc[-2], MaLong.iloc[-2])
    #03-01 to 03-18 no trade

