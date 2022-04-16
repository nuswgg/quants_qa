import tqsdk

api=tqsdk.TqApi( tqsdk.TqAccount("simnow","040123","123456") , auth="270829786@qq.com,24729220a")


a=api.get_order()
print(a)

a2=api.get_position()
print(a2)

a3=api.get_trade()
print(a3)

a4=api.get_account()
print(a4)

api.close()