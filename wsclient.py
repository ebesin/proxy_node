import websocket
import time
from threading import Thread


class WSClient:
    def __init__(self,uri,onRecv):
        self.ws=None
        self.uri = uri
        self.onRecv = onRecv
        self.reconnect_count=0
        self.connect()

    def connect(self):
        thread = Thread(target=self.connection_tmp)
        thread.daemon = True
        thread.start()

    def connection_tmp(self):
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.uri,
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_open=self.on_open)
        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.ws.close()
        except Exception as e:
            print(e)

    def sendMsg(self,msg):
        try:
            if(self.ws):
                print('send msg')
                self.ws.send(msg,opcode=websocket.ABNF.OPCODE_BINARY)
        except Exception as e:
            print(e)

    def on_message(self,ws,message):
        # print(message)
        self.onRecv(message)

    def on_open(self,ws):
        self.ws.send("hello")

    def on_error(self,ws, error):
        print(error)
        print("reconnect_count:%d"%self.reconnect_count)
        self.reconnect_count+=1
        time.sleep(1)
        self.connection_tmp()

def onRecv(msg):
    print('received')
        
if __name__ == "__main__":
    client = WSClient('ws://47.108.235.65:5678/monitor',onRecv)
    