import asyncio
import datetime
import random
import socket
import websockets
import time
import yr_protocol
from threading import Thread
import json


# UDP接收
class UDPReceive:
    def __init__(self,my_addr,my_port):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.local_addr = (my_addr,my_port)
        self.udp_socket.bind(self.local_addr)
        self.udp_socket.settimeout(None)
    
    def __del__(self):
        self.udp_socket.close()

    def recv(self,recvCB):
        while True:
            try:
                recv_data,addr = self.udp_socket.recvfrom(1024*64)
                recvCB(recv_data)
            except Exception as e:
                print(e)
                pass

    def run_udp_receive(self,recvCB):
        self.udp_thread = Thread(target=self.recv,args=(recvCB,))
        self.udp_thread.start()

# UDP发送
class UDPSend:
    def __init__(self,target_addr,target_port):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target_address = (target_addr, target_port)

    def __del__(self):
        self.udp_socket.close()

    def send(self,msg):
        self.udp_socket.sendto(msg,self.target_address)

class WSServer:
    def __init__(self):
        self.decoder = yr_protocol.YRDecoder()
        self.CONNECTIONS = {}
        self.ALLCONNECTIONS=set()
        self.websocket_addr = "0.0.0.0"
        self.websocket_port = "5678"
        self.udp_recv = UDPReceive("0.0.0.0",8765)
        self.udp_send = UDPSend("127.0.0.1",8764)
        # send_thread = Thread(target=self.udp_send_thread)
        # send_thread.start()
        self.udp_recv.run_udp_receive(self.onUDPMsgRecv)
        self.start_websocket()

    async def register(self,websocket):
        self.ALLCONNECTIONS.add(websocket) 
        # 根据path判断设备
        self.CONNECTIONS[websocket.path] = websocket
        try:
            async for message in websocket:
                if websocket.path == "/vehicle":
                    print("111")
                    self.vehicleCB(message)
                elif websocket.path == "/dji":
                    self.djiCB(message)
                elif websocket.path == "/monitor":
                    self.monitorCB(message)
        except Exception as e:
            pass
        try:
            await websocket.wait_closed()
        finally:
            self.CONNECTIONS.pop(websocket.path)
            self.ALLCONNECTIONS.remove(websocket)

    async def show_time(self):
        while True:
            message = datetime.datetime.utcnow().isoformat() + "Z"
            websockets.broadcast(self.ALLCONNECTIONS, message)
            await asyncio.sleep(random.random() * 2 + 1)    

    # 开启websocket服务
    async def start_server(self):
        async with websockets.serve(self.register, self.websocket_addr, self.websocket_port):
            await self.show_time()

    def websocket_thread(self):
        asyncio.run(self.start_server()) 

    def start_websocket(self):
        self.ws_thread = Thread(target=self.websocket_thread)
        self.ws_thread.start()

    # udp接受消息回调
    def onUDPMsgRecv(self,data):
        print('receive')
        try:
            #todo 接受到UDP消息，根据消息内容将消息发送到不同的设备
            res = self.decoder.decode(data)
            # print(str(res))
            if res['status'] == 'ok':
                if res['topic'].startswith('/domain/vehicle'):
                    if '/vehicle' in self.CONNECTIONS:
                        asyncio.run(self.CONNECTIONS['/vehicle'].send(json.dumps(res)))
                    else:
                        print("vehicle doesn't connect")
                elif res['topic'].startswith('/domain/dji'):
                    if '/dji' in self.CONNECTIONS:
                        asyncio.run(self.CONNECTIONS['/dji'].send(json.dumps(res)))
                    else:
                        print("dji doesn't connect")
                    pass
                else:
                    pass
            pass
        except Exception as e:
            print(e)
            pass

    def udp_send_thread(self):
        while True:
            # self.udp_send.send(b'123')
            time.sleep(0.5)



    def vehicleCB(self,data):
        print(f"receive vehicle data:<{data}>")
        try:
            json_str = json.loads(data)
            b_d = self.decoder.encode(json_str)
            self.udp_send.send(bytes(b_d.hex(),encoding = 'utf8'))
        except Exception as e:
            print(e)
        pass 
    
    def djiCB(self,data):
        print("receive dji data")
        #todo 将data转成规定格式发出去
        pass

    def monitorCB(self,data):
        print("receive monitor data")
        #todo 将data转成规定格式发出去
        pass

if __name__ == "__main__":
    WSServer()