import QUANTAXIS as QA

# 对站上20天均线进行统计
cn_stock_list = QA.QA_fetch_stock_list_adv().code.to_list()
gold_component = QA.QA_fetch_stock_block_adv().get_block('黄金概念').code
data = QA.QA_fetch_stock_day_adv(gold_component,'2020-01-01','2020-05-15')
def ifup20(data):
    return (data.close - QA.MA(data.close,20)).dropna() > 0
ind = data.add_func(ifup20)
ind.dropna().groupby(level=0).sum()


