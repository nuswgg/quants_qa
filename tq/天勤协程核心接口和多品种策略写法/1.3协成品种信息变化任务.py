from tqsdk import TqApi

async def 单品种策略(品种):
    quote = api.get_quote(品种)
    async with api.register_update_notify(quote) as update_chan:
        async for _ in update_chan:
            print(品种,quote.last_price,quote.datetime)

api = TqApi(auth="270829786@qq.com,24729220a")

多个合约列表=["SHFE.rb2101","SHFE.hc2101","SHFE.rb2105","SHFE.hc2105"]

for x in 多个合约列表:

    api.create_task(单品种策略(x))
while True:
    api.wait_update()