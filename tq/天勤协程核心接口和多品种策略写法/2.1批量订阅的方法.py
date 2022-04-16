import tqsdk



api=tqsdk.TqApi(auth="270829786@qq.com,24729220a")


#订阅全品种
全品列表=api.query_quotes(ins_class="FUTURE")

print(len(全品列表))
#订阅某个所的

上期所=api.query_quotes(ins_class="FUTURE",exchange_id ="SHFE")

print(len(上期所))

#订阅主连,并且获取行情

主连=api.query_quotes(ins_class="CONT")

#获取日线
主连日线=[  api.get_kline_serial(x,60*60*24) for x in 主连]

while True:
    api.wait_update()
    #print(主连日线)
    for x in 主连日线:
        print(x)