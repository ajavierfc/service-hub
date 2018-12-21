import socket
import time
import errno
import traceback
from _thread import *


class Socket(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._connected = False

    def reconnect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(5)
        try:
            self._connected = False
            self._socket.connect((self._host, self._port))
            self._connected = True
            print("Connected to {}:{}".format(self._host, self._port))
        except socket.timeout:
            print("Timeout connecting to " + self._host)
        except:
            traceback.print_exc()

    def send(self, data):
        if self._connected:
            self._socket.send(data)
            print("SENT TO {}:{} >{}<".format(self._host, self._port, data))

    def recv(self, bufsize, data):
        if not self._connected:
            return
        try:
            return self._socket.recv(bufsize)
        except socket.timeout:
            print("Timeout receiving {}:{} >{}<".format(self._host, self._port, data))

    def close(self):
        self._connected = False
        self._socket.close()

    def is_connected(self):
        return self._connected


client_sockets = [
    Socket('localhost', 1883),
    Socket('localhost', 18831),
    Socket('localhost', 18832),
]


def send(client_socket, data):
    if not client_socket.is_connected():
        client_socket.reconnect()

    while True:
        try:
            client_socket.send(data)
            server_data = client_socket.recv(1024, data)
            break

        except socket.timeout:
            print("SERVER: timeout")
            return ""

        except socket.error as error:
            if error.errno == errno.EPIPE:
                print("Connection lost. Reconnecting")
                client_socket.reconnect()
            elif error.errno == errno.ECONNRESET:
                print("Connection closed.")
                return ""
            else:
                raise

    #client_socket.close()

    print("SERVER: >" + str(server_data) +"<")

    return server_data


def send_to_servers(data):
    global client_sockets

    server_data = None

    for client_socket in client_sockets:
        got = send(client_socket, data)
        if got:
            server_data = got

    return server_data


def connect_to_servers():
    global client_sockets
    for client_socket in client_sockets:
        client_socket.reconnect()


def client_thread(connected_client):
    connected_client.settimeout(1)
    connect_to_servers()
    while True:
        try:
            data = connected_client.recv(1024)
            print("CLIENT: >" + str(data) +"<")
        except socket.timeout:
            print("CLIENT: timeout")
            break

        if data:
            data = send_to_servers(data)
            if data is not None:
                connected_client.send(data)
        else:
            break

    connected_client.close()


if __name__ == '__main__':

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 8888))
    server_socket.listen(100)

    print("Server listening")

    try:
        while 1:
            conn, addr = server_socket.accept()
            start_new_thread(client_thread, (conn,))
    except KeyboardInterrupt:
        server_socket.close()
        client_socket.close()
        raise
