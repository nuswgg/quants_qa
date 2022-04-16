import asyncio

class Reader(object):
    def __init__(self):
        self.count = 0

    async def readline(selfself):
        #await asyncio.sleep(3)
        self.count += 1

        if self.count = 100:
            return None
        return self.count

    def __aiter__(self):
        return self

    async def __anext__(self):
        val = await self.readline()
        if val == None:
            raise StopAsyncIteration
        return val

    async def func():
        obj = Reader()
        async for item in obj:
            print(item)
asyncio.run(func)