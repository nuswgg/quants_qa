class TargetPosTaskSingleton(type): #检查下单方向及品种目标持仓task是否重复
    _instances = {}
    def __call__(cls, api, symbol, price="ACTIVE", offset_priority="今昨,开", trade_chan=None, *args, **kwargs):
        if symbol not in TargetPosTaskSingleton._instances:
            TargetPosTaskSingleton._instances[symbol] = super(TargetPosTaskSingleton, cls).__call__(api, symbol, price,**kwargs)
        else:
            instance = TargetPosTaskSingleton._instances[symbol]
            if instance._offset_priority != offset_priority:
                raise Exception("您试图用不同的 offset_priority 参数创建两个 %s 调仓任务, offset_priority参数原为 %s, 现为 %s" % (
                    symbol, instance._offset_priority, offset_priority))
            if instance._price != price:
                raise Exception("您试图用不同的 price 参数创建两个 %s 调仓任务, price参数原为 %s, 现为 %s" % (symbol, instance._price, price))
        return TargetPosTaskSingleton._instances[symbol]
class TargetPosTask(object, metaclass=TargetPosTaskSingleton):
    """目标持仓 task, 该 task 可以将指定合约调整到目标头寸"""
    def __init__() -> None:
        super(TargetPosTask, self).__init__()
        self._pos_chan = TqChan(self._api, last_only=True) #目标持仓队列
        self._task = self._api.create_task(self._target_pos_task()) #创建目标持仓task
    def set_target_volume(self, volume: int) -> None:
        """
        设置目标持仓手数
        """
        self._pos_chan.send_nowait(int(volume)) #该函数就这一个作用，把目标持仓放入目标持仓队列
    def _get_order(self, offset, vol, pending_frozen):
        """
        根据指定的offset和预期下单手数vol, 返回符合要求的委托单最大报单手数
        """
        return order_offset, order_dir, order_volume #返回开平方向、买卖方向、下单手数
    async def _target_pos_task(self):
        """负责调整目标持仓的task"""
        try:
            async for target_pos in self._pos_chan:
                target_pos = self._pos_chan.recv_latest(target_pos)  # 获取最后一个target_pos目标仓位
                # 确定调仓增减方向
                delta_volume = target_pos - self._pos.pos #计算目标持仓和净持仓的差值
                for each_priority in self._offset_priority + ",":  # 按不同模式的优先级顺序报出不同的offset单，股指(“昨开”)平昨优先从不平今就先报平昨，原油平今优先("今昨开")就报平今
                    #返回开平方向、买卖方向、下单手数
                    order_offset, order_dir, order_volume = self._get_order()
                    order_task = InsertOrderUntilAllTradedTask()
class InsertOrderUntilAllTradedTask(object):
    """追价下单task, 该task会在行情变化后自动撤单重下，直到全部成交
     （注：此类主要在tqsdk内部使用，并非简单用法，不建议用户使用）"""
    def __init__():
        """
        创建追价下单task实例
        """
        self._task = self._api.create_task(self._run()) #创建追价下单task
    async def _run(self):
        """负责追价下单的task"""
        async with self._api.register_update_notify() as update_chan:
            while self._volume != 0:
                insert_order_task = InsertOrderTask()
                order = await insert_order_task._order_chan.recv()
                check_chan = TqChan(self._api, last_only=True)
                check_task = self._api.create_task(self._check_price()) #检查价格是否变化
                try:
                    await asyncio.shield(insert_order_task._task)
                    order = insert_order_task._order_chan.recv_latest(order)
                    self._volume = order.volume_left
                    if self._api.get_order().status == "ALIVE":
                        # 当 task 被 cancel 时，主动撤掉未成交的挂单
                        self._api.cancel_order(order.order_id, account=self._account)
                    # 在每次退出时，都等到 insert_order_task 执行完，此时 order 状态一定是 FINISHED；self._trade_chan 也一定会收到全部的成交手数
                    await insert_order_task._task
    def _get_price(self, direction, price_mode):
        """根据最新行情和下单方式计算出最优的下单价格"""
        # 主动买的价格序列(优先判断卖价，如果没有则用买价)
        return limit_price
    async def _check_price(self, update_chan, order_price, order):
        """判断价格是否变化的task"""
class InsertOrderTask(object):
    """下单task （注：此类主要在tqsdk内部使用，并非简单用法，不建议用户使用）"""
    def __init__():
        """
        创建下单task实例
        """
        self._task = self._api.create_task(self._run())
    async def _run(self):
        """负责下单的task"""
        order_id = _generate_uuid("PYSDK_target")
        order = self._api.insert_order(self._symbol, self._direction, self._offset, self._volume, self._limit_price,
                                       order_id=order_id, account=self._account)