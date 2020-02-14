import socket
import time
import errno
import traceback
from _thread import *
from server_access import Sockets


def client_thread(connected_client):
    connected_client.settimeout(5)

    try:
        with Sockets() as sockets:
            while True:
                try:
                    data = connected_client.recv(1048576)
                    if not data: break
                    print("Data from connected client >" + str(data) +"<")
                except socket.timeout:
                    print("Coudn't get data from connected client: timeout")
                    break

                data = sockets.send(data)
                if data:
                    connected_client.send(data)
    finally:
        connected_client.close()


if __name__ == '__main__':

    listen = ('localhost', 8888)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(listen)
    server_socket.listen(5)

    print("Server listening on " + str(listen))

    try:
        while 1:
            conn, addr = server_socket.accept()
            start_new_thread(client_thread, (conn,))
    except:
        traceback.print_exc()
        server_socket.close()
        raise
