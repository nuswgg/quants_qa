from tqsdk import TqApi, TqAuth
import talib as ta
import pandas as pd
import akshare as ak
# 创建api实例，设置web_gui=True生成图形化界面
# api = TqApi(web_gui="http://192.168.1.4:9875", auth=TqAuth("nuswgg", "541278"))
api = TqApi(auth=TqAuth("nuswgg", "541278"))
klines = api.get_kline_serial("SZSE.000001", 60*60*24,1500)
open,high,close,low=klines.open.values,klines.high.values,klines.close.values,klines.low.values
df = pd.DataFrame({})
df['morningstar'] = ta.CDLMORNINGSTAR(open,high,low,close,penetration=0)

df[df.morningstar==100]

stock_industry_sina_df = ak.stock_sector_spot(indicator="新浪行业")