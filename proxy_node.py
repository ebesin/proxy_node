import socket
import time
import asyncio
import websockets
import websocket_client
from threading import Thread


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

class ProxyNode:
    def __init__(self):
        self.udp_recv = UDPReceive("0.0.0.0",8765)
        self.udp_send = UDPSend("127.0.0.1",8764)
        self.ws_client = websocket_client.WSClient('ws://47.108.235.65:5678/monitor',self.onRecv)
        self.udp_recv.run_udp_receive(self.onUDPMsgRecv)
        self.ws_client.connect()

    # websocket 接收回调
    def onRecv(self,msg):
        try:
            # print(msg)
            # print(f"receive from server<{msg}>")
            self.udp_send.send(bytes.fromhex(msg))
        except Exception as e:
            print(e)

    # udp接受消息回调
    def onUDPMsgRecv(self,data):
        try:
            asyncio.run(self.ws_client.sendMsg(bytes(data)))
            pass
        except Exception as e:
            print(e)
            pass

    def udp_send_thread(self):
        while True:
            # self.udp_send.send(b'123')
            time.sleep(0.5)



if __name__ == "__main__":
    ProxyNode()