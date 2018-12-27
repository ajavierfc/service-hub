import socket
import errno
import traceback

class Socket(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._connected = False
        self._socket = None

    def reconnect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._connected = False
            self._socket.settimeout(2)
            self._socket.connect((self._host, self._port))
            self._socket.settimeout(0.2)
            self._connected = True
            print("Connected to {}:{}".format(self._host, self._port))
        except socket.timeout:
            print("Timeout connecting to {}:{}".format(self._host, self._port))
        except:
            traceback.print_exc()

    def send(self, data):
        response_data = bytearray()

        while self._connected:
            try:
                self._socket.send(data)
                print("Sent to {}:{} >{}<".format(self._host, self._port, data))

                while True:
                    response_data += self._socket.recv(1024)
                    if not response_data: break

                return response_data

            except socket.timeout:
                if response_data: return response_data
                print("Timeout sending to {}:{} >{}<".format(self._host, self._port, data))
                return

            except socket.error as error:
                if error.errno == errno.EPIPE:
                    print("Connection lost. Reconnecting")
                    client_socket.reconnect()

                elif error.errno == errno.ECONNRESET:
                    print("Connection closed.")
                    return

                else:
                    raise

    def close(self):
        self._connected = False
        if self._socket:
            self._socket.close()

    def is_connected(self):
        return self._connected


class Sockets(object):

    def __init__(self):
        self._client_sockets = [
            Socket('localhost', 1883),
            Socket('localhost', 18831),
            Socket('localhost', 18832),
        ]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for s in self._client_sockets:
            s.close()

    def send(self, data):
        response = None

        for client_socket in self._client_sockets:
            if not client_socket.is_connected():
                client_socket.reconnect()

            if client_socket.is_connected():
                server_data = client_socket.send(data)
                print("Server data: >{}<".format(str(data)))

                if not response and server_data:
                    response = server_data

        return response
