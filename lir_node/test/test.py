import socket
import time
import os

if __name__ == "__main__":
    print(all(["False"]))
    print(os.getenv("LISTEN_PORT"))
    # while True:
    #     udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     udp_socket.sendto("ffffff".encode(), ("192.168.0.6", 31313))
    #     time.sleep(1)
