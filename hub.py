import socket
import time
import errno
import traceback
from _thread import *
from server_access import Sockets


def client_thread(connected_client):
    connected_client.settimeout(1)

    try:
        with Sockets() as sockets:
            while True:
                try:
                    data = connected_client.recv(1024)
                    print("Data from connected client >" + str(data) +"<")
                except socket.timeout:
                    print("Coudn't get data from connected client: timeout")
                    break

                if data:
                    data = sockets.send(data)
                    if data:
                        connected_client.send(data)
                else:
                    break
    finally:
        connected_client.close()


if __name__ == '__main__':

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888))
    server_socket.listen(100)

    print("Server listening")

    try:
        while 1:
            conn, addr = server_socket.accept()
            start_new_thread(client_thread, (conn,))
    except:
        traceback.print_exc()
        server_socket.close()
        client_socket.close()
        raise
