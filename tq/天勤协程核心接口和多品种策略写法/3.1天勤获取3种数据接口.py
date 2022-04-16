import tqsdk

api=tqsdk.TqApi(auth="270829786@qq.com,24729220a")

tick切片=api.get_quote("SHFE.rb2101")
print(tick切片)

tick线=api.get_tick_serial("SHFE.rb2101",5)
print(tick线)

K线=api.get_kline_serial("SHFE.rb2101",60,10)
print(K线)

while True:
    api.wait_update()
    print(tick切片,tick线,K线)

api.close()