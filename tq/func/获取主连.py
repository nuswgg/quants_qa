from tqsdk import TqApi,TqKq , TqAuth
# api = TqApi(auth=TqAuth("信易账号", "密码"))
# api = TqApi(TqSim(init_balance=100000), auth=TqAuth("天勤123", "tianqin123"))
api = TqApi( auth=TqAuth("天勤123", "tianqin123"))
# 获取上期所全部主连
MC = api.query_quotes(ins_class='CONT',exchange_id='SHFE')
# 获取大商所全部指数
I = api.query_quotes(ins_class='INDEX',exchange_id='DCE')
# 获取上期所黄金未下市的期权合约
AuOp = api.query_quotes(ins_class='OPTION',exchange_id='SHFE',product_id='au',expired=False)
# 获取上期所全部主力合约
M = api.query_cont_quotes(exchange_id='SHFE')
# 订阅螺纹钢主连
quote = api.get_quote("KQ.m@SHFE.rb")
# 打印现在螺纹钢主连的标的合约
print("螺纹钢主连对应的主力合约：",quote.underlying_symbol)
# 获取黄金标的为au2103全部未下市看涨期权
AuOpC = api.query_options(underlying_symbol='SHFE.au2103',option_class='CALL',expired=False)
#获取黄金指数
aui = api.query_quotes(ins_class="INDEX", product_id="au")
print('上期所全部主连:')
print(MC)
print('大商所全部指数:')
print(I)
print('黄金未下市的期权合约:')
print(AuOp)
print('上期所全部主力合约:')
print(M)
print('黄金标的为au2103全部未下市看涨期权:')
print(AuOpC)
print('黄金指数',aui)

api.close()
'''
部分输出值：
螺纹钢主连对应的主力合约： SHFE.rb2105
上期所全部主连:
...
大商所全部指数:
...
黄金未下市的期权合约:
...
['SHFE.wr2105', 'SHFE.al2103', 'SHFE.pb2103', 'SHFE.bu2106', 'SHFE.ss2104', 'SHFE.hc2105', 
'SHFE.au2106', 'SHFE.cu2103', 'SHFE.zn2103', 'SHFE.sp2105', 'SHFE.sn2104', 'SHFE.ru2105', 
'SHFE.ni2104', 'SHFE.fu2105', 'SHFE.ag2106', 'SHFE.rb2105']
黄金标的为au2103全部未下市看涨期权:
['SHFE.au2103C364', 'SHFE.au2103C336', 'SHFE.au2103C316', 'SHFE.au2103C332', 'SHFE.au2103C380'
, 'SHFE.au2103C324', 'SHFE.au2103C372','SHFE.au2103C352', 'SHFE.au2103C392', 'SHFE.au2103C344'
, 'SHFE.au2103C424', 'SHFE.au2103C384', 'SHFE.au2103C456', 'SHFE.au2103C340', 'SHFE.au2103C312'
, 'SHFE.au2103C388', 'SHFE.au2103C328', 'SHFE.au2103C360', 'SHFE.au2103C396', 'SHFE.au2103C416'
, 'SHFE.au2103C440', 'SHFE.au2103C400', 'SHFE.au2103C348', 'SHFE.au2103C448', 'SHFE.au2103C320'
, 'SHFE.au2103C408', 'SHFE.au2103C356', 'SHFE.au2103C368', 'SHFE.au2103C376', 'SHFE.au2103C432']
黄金指数 ['KQ.i@SHFE.au']