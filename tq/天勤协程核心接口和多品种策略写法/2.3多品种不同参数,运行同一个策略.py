import tqsdk
from tqsdk.tafunc import ma  


api=tqsdk.TqApi( tqsdk.TqAccount("simnow","040123","123456") , auth="270829786@qq.com,24729220a")


#设置品种和参数

品种和参数字典={ 
"SHFE.rb2101":(10,20),
"SHFE.hc2101":(20,30),
"SHFE.rb2105":(30,40),
"SHFE.hc2105":(40,50),
}


#订阅数据
数据=[ (x,api.get_kline_serial(x,5),品种和参数字典[x]) for x in 品种和参数字典 ]


def 双均线策略(品种,k线,参数元祖):
    快线= ma(k线.close,参数元祖[0])
    慢线= ma(k线.close,参数元祖[1])
    quote=api.get_quote(品种)
    #死叉 平多 做空
    if 快线.iloc[-3]>慢线.iloc[-3]  and 快线.iloc[-2]<慢线.iloc[-2] :
        持仓=api.get_position(品种)


        #平今日多仓
        if 持仓.pos_long_today>0:
            api.insert_order(品种,"SELL","CLOSETODAY",持仓.pos_long_today,quote.lower_limit)
        #平昨日多仓
        if 持仓.pos_long_his>0:
            api.insert_order(品种,"SELL","CLOSE",持仓.pos_long_today,quote.lower_limit)  
        #开仓
        if 持仓.pos_short==0:
            api.insert_order(品种,"SELL","OPEN",1,quote.lower_limit)
        while True:
            api.wait_update()
            if 持仓.pos_long==0 and 持仓.pos_short>0:
                break
#-----------------------------------------
    #金叉 平空 做多
    if 快线.iloc[-3]<慢线.iloc[-3]  and 快线.iloc[-2]>慢线.iloc[-2] :
        持仓=api.get_position(品种)


        #平今日空仓
        if 持仓.pos_short_today>0:
            api.insert_order(品种,"BUY","CLOSETODAY",持仓.pos_short_today,quote.upper_limit)
        #平昨日空仓
        if 持仓.pos_short_his>0:
            api.insert_order(品种,"BUY","CLOSE",持仓.pos_short_his,quote.upper_limit)  
        #开仓
        if 持仓.pos_long==0:
            api.insert_order(品种,"BUY","OPEN",1,quote.upper_limit)
        while True:
            api.wait_update()
            if 持仓.pos_short==0 and 持仓.pos_long>0:
                break
while True:
    api.wait_update()
    #print(主连日线)
    for x in 数据:
        双均线策略(x[0],x[1],x[2])
