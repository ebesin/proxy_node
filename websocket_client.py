import asyncio
import websockets as ws
from websockets import ConnectionClosed
from threading import Thread
import time

class WSClient:
    def __init__(self,url,onRecv):
        self.count=0
        self.uri = url
        self.onRecv = onRecv
        self.websocket=None
        self.isConnectToWebSocket = False
        self.ws_thread = Thread(target=self.start_client)
        self.ws_thread.daemon = True
        

    def connect(self):
        self.ws_thread.start()

    async def start(self):
        while True:
            try:
                async with ws.connect(self.uri,max_size=2 ** 25) as self.websocket:
                    self.isConnectToWebSocket = True
                    await self.websocket.send('start')
                    while True:
                        try:
                            message = await self.websocket.recv()
                            self.onRecv(message)
                            pass
                        except ConnectionClosed as e:
                            print(e.code)
                            if e.code == 1006:
                                self.isConnectToWebSocket = True
                                print('reconnecting...')
                                await asyncio.sleep(2)
                                break
            except Exception as e:
                print(e)
                if self.count == 60: 
                    return
                self.count += 1
                await asyncio.sleep(2)

    # 发送消息
    async def sendMsg(self,msg):
        if self.isConnectToWebSocket:
            await self.websocket.send(msg)

    def start_client(self):
        asyncio.run(self.start())

if __name__ == '__main__':
    WSClient()