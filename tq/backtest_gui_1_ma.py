from datetime import date
from tqsdk import TqApi, TqAuth, TqBacktest, TargetPosTask
# 在创建 api 实例时传入 TqBacktest 就会进入回测模式,设置web_gui=True开启图形化界面
# api = TqApi(backtest=TqBacktest(start_dt=date(2021, 1, 1), end_dt=date(2021, 3, 18)),web_gui="http://192.168.1.4:9876", auth=TqAuth("nuswgg", "541278"))
api = TqApi(backtest=TqBacktest(start_dt=date(2021, 3, 1), end_dt=date(2021, 3, 18)),web_gui="http://172.16.83.232:9876", auth=TqAuth("nuswgg", "541278"))
# 获得 SHFE.cu2105 5分钟K线的引用
klines = api.get_kline_serial("SHFE.cu2105", 5 * 60, data_length=150)
# 创建 cu2105 的目标持仓 task，该 task 负责调整 cu2105 的仓位到指定的目标仓位
target_pos = TargetPosTask(api, "SHFE.cu2105")
# while True:
#     api.wait_update()
#     if api.is_changing(klines):
#         ma1 = sum(klines.close.iloc[-5:]) / 5
#     #     # ma2 = sum(klines.close.iloc[-10:]) / 10
#     #     # ma3 = sum(klines.close.iloc[-20:]) / 20
#     #     # pct_chg = klines.close.pct_change()
#     #     # mazf1 = sum(abs(pct_chg).iloc[-10:])/10
#     #     # bd =
#     #
#     #     print("最新价", klines.close.iloc[-1], "MA", ma)
#         if klines.close.iloc[-1] > ma1:
#     #         print("最新价大于MA: 目标多头5手")
#     #         # 设置目标持仓为多头5手
#             target_pos.set_target_volume(5)
#         elif klines.close.iloc[-1] < ma1:
#     #         print("最新价小于MA: 目标空仓")
#     #         # 设置目标持仓为空仓
#             target_pos.set_target_volume(0)


while True:
    api.wait_update()
    if api.is_changing(klines):
        ma = sum(klines.close.iloc[-15:]) / 15
        print("最新价", klines.close.iloc[-1], "MA", ma)
        if klines.close.iloc[-1] > ma:
            print("最新价大于MA: 目标多头5手")
            # 设置目标持仓为多头5手
            target_pos.set_target_volume(5)
        elif klines.close.iloc[-1] < ma:
            print("最新价小于MA: 目标空仓")
            # 设置目标持仓为空仓
            target_pos.set_target_volume(0)