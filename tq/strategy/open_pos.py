#  平仓，可以为平多，可以为平空
import asyncio
from time import time
from datetime import datetime
from tqsdk import TqApi, TargetPosTask,TqBacktest,TqAuth,TqSim

# async def OpenClose(api,quote={},position={},kaiping='',lot=0,price=None, advanced=None,che_time=0,block=False):

api = TqApi(TqSim(init_balance=100000), auth=TqAuth("天勤123", "tianqin123"))
async def OpenClose(api,quote={},position={},kaiping='',lot=0,price=None, advanced=None,che_time=0,block=False):
    position = api.get_position()
    acct = api.get_account()
