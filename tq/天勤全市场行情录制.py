import os
import time
from peewee import (
    Model,
    AutoField,
    CharField,
    DateTimeField,
    FloatField,
    MySQLDatabase,
    SqliteDatabase,
)
from numpy import isnan
from threading import Thread
from tqsdk import TqApi, TqSim

# db = MySQLDatabase("quote", user="root", passwd="123456")
db = SqliteDatabase(
    "quote.db", pragmas={"journal_mode": "wal", "cache_size": -1024 * 64}
)


class TickData(Model):
    """
    Tick data
    """

    id = AutoField()

    symbol: str = CharField()
    exchange: str = CharField()
    datetime: datetime = DateTimeField()

    name: str = CharField()
    volume: float = FloatField()
    open_interest: float = FloatField()
    last_price: float = FloatField()
    limit_up: float = FloatField()
    limit_down: float = FloatField()

    open_price: float = FloatField()
    high_price: float = FloatField()
    low_price: float = FloatField()
    pre_close: float = FloatField()

    bid_price_1: float = FloatField()
    bid_price_2: float = FloatField(null=True)
    bid_price_3: float = FloatField(null=True)
    bid_price_4: float = FloatField(null=True)
    bid_price_5: float = FloatField(null=True)

    ask_price_1: float = FloatField()
    ask_price_2: float = FloatField(null=True)
    ask_price_3: float = FloatField(null=True)
    ask_price_4: float = FloatField(null=True)
    ask_price_5: float = FloatField(null=True)

    bid_volume_1: float = FloatField()
    bid_volume_2: float = FloatField(null=True)
    bid_volume_3: float = FloatField(null=True)
    bid_volume_4: float = FloatField(null=True)
    bid_volume_5: float = FloatField(null=True)

    ask_volume_1: float = FloatField()
    ask_volume_2: float = FloatField(null=True)
    ask_volume_3: float = FloatField(null=True)
    ask_volume_4: float = FloatField(null=True)
    ask_volume_5: float = FloatField(null=True)

    class Meta:
        database = db
        indexes = ((("symbol", "exchange", "datetime"), True),)


class TianQinDataRecorder:
    def __init__(self, instruments):
        """
        instruments: 订阅行情类型
        database_string: 数据库连接字段
        """
        try:
            self.api = TqApi(TqSim())
            if self.api:
                self.is_connected = True
                self.quote_thread = Thread(target=self.update_quote)
                self.quote_thread.start()

                all_symbols = [
                    k
                    for k, v in self.api._data["quotes"].items()
                    if v.ins_class in instruments and not v.expired
                ]
                self.all_symbols = list(set(all_symbols))
            db.connect()
            db.create_tables([TickData])

        except Exception as e:
            self.is_connected = False
            print(e)

        self.subscribe_symbols = []
        self.quote_objs = []

    def save_to_database(self, quote):
        if not quote["last_price"] or isnan(quote["last_price"]):
            return
        TickData.create(
            symbol=quote["instrument_id"],
            exchange=quote["exchange_id"],
            datetime=quote["datetime"],
            name=quote["instrument_id"],
            volume=quote["volume"],
            open_interest=quote["open_interest"],
            last_price=quote["last_price"],
            limit_up=quote["upper_limit"],
            limit_down=quote["lower_limit"],
            open_price=quote["open"],
            high_price=quote["highest"],
            low_price=quote["lowest"],
            pre_close=quote["pre_close"],
            bid_price_1=quote["bid_price1"],
            bid_price_2=quote["bid_price2"],
            bid_price_3=quote["bid_price3"],
            bid_price_4=quote["bid_price4"],
            bid_price_5=quote["bid_price5"],
            ask_price_1=quote["ask_price1"],
            ask_price_2=quote["ask_price2"],
            ask_price_3=quote["ask_price3"],
            ask_price_4=quote["ask_price4"],
            ask_price_5=quote["ask_price5"],
            bid_volume_1=quote["bid_volume1"],
            bid_volume_2=quote["bid_volume2"],
            bid_volume_3=quote["bid_volume3"],
            bid_volume_4=quote["bid_volume4"],
            bid_volume_5=quote["bid_volume5"],
            ask_volume_1=quote["ask_volume1"],
            ask_volume_2=quote["ask_volume2"],
            ask_volume_3=quote["ask_volume3"],
            ask_volume_4=quote["ask_volume4"],
            ask_volume_5=quote["ask_volume5"],
        ).save()

    def start(self):
        for symbol in self.subscribe_symbols:
            quote = self.api.get_quote(symbol)
            self.quote_objs.append(quote)

    def update_quote(self):
        while self.api.wait_update():
            for quote in self.quote_objs:
                if self.api.is_changing(quote):
                    self.save_to_database(quote)

    def subscribe(self, symbol):
        if symbol in self.all_symbols:
            print(f"开始订阅{symbol}行情")
            self.subscribe_symbols.append(symbol)
        else:
            print("无法订阅行情")

    def subscribe_all(self):
        for symbol in self.all_symbols:
            self.subscribe(symbol)


if __name__ == "__main__":
    recorder = TianQinDataRecorder(["FUTURE"])
    # 全市场录制
    recorder.subscribe_all()
    # 部分录制
    # recorder.subscribe("SHFE.ni2101")
    # recorder.subscribe("SHFE.ni2105")
    recorder.start()
    while True:
        time.sleep(1)
