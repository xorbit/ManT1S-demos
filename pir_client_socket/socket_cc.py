import asyncio
import json


class CommChannel:
    def __init__(self, port=17217):
        self.port = port
        self.conn = {}
        self.server = None
        self.cmd_handler = {}
    async def listen(self):
        if self.server is None:
            self.server = await asyncio.start_server(self._handler, '0.0.0.0', self.port)
        async with self.server:
            await self.server.wait_closed()
    def add_handler(self, cmd):
        def decorator(handler):
            self.cmd_handler[cmd] = handler
            return handler
        return decorator
    async def _handler(self, reader, writer):
        while True:
            cmd = (await reader.readline())[:-1].decode('utf-8')
            if cmd:
                data_len = int.from_bytes(await reader.read(2), 'little')
                if data_len:
                    data = json.loads((await reader.read(data_len)).decode('utf-8'))
                else:
                    data = None
            if cmd:
                if cmd in self.cmd_handler:
                    await self.cmd_handler[cmd](data)
                else:
                    print (f'Unknown command {cmd}')
            else:
                break
        writer.close()
        reader.close()
    async def send(self, address, cmd, data=None):
        if address in self.conn:
            conn = self.conn[address]
        else:
            conn = None
            while conn is None:
                try:
                    _, conn = writer = await asyncio.open_connection(address, self.port)
                except:
                    await asyncio.sleep(1)
            self.conn[address] = conn
        conn.write(cmd.encode('utf-8'))
        conn.write(b'\n')
        if data is not None:
            data = json.dumps(data).encode('utf-8')
            conn.write(int.to_bytes(len(data), 2, 'little'))
            conn.write(data)
        else:
            conn.write(int.to_bytes(0, 2, 'little'))
        await conn.drain()

