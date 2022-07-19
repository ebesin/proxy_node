import socket
import threading

class UDPReceive:
    def __init__(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.local_addr = ("127.0.0.1",8764)
        self.udp_socket.bind(self.local_addr)
        self.udp_socket.settimeout(None)
    
    def __del__(self):
        self.udp_socket.close()

    def recv(self):
        while True:
            recv_data,addr = self.udp_socket.recvfrom(1024*64)
            print(recv_data)

    def run_udp_receive(self):
        self.udp_thread = threading.Thread(target=self.recv)
        self.udp_thread.start()

if __name__ == "__main__":
    UDPReceive().run_udp_receive()