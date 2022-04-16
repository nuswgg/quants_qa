import tqsdk



api=tqsdk.TqApi(auth="270829786@qq.com,24729220a")


#设置品种和参数

品种和参数字典={ 
"SHFE.rb2101":(10,20),
"SHFE.hc2101":(20,30),
"SHFE.rb2105":(30,40),
"SHFE.hc2105":(40,50),
}


#订阅数据
主连日线=[ (x,api.get_kline_serial(x,60),品种和参数字典[x]) for x in 品种和参数字典 ]
n=0
while True:
    api.wait_update()
    #print(主连日线)
    if n==0:
        n+=1
        for x in 主连日线:
            print(x)
