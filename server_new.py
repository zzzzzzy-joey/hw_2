import threading
import socket
import os
import sys


class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:

            try:
                clientMessage = self.sc.recv(1024).decode('utf-8')
                if clientMessage:
                    print('{}: {!r}'.format(self.sockname, clientMessage))
                    self.server.broadcast(clientMessage, self.sockname)
                else:
                    print('{} has closed the connection'.format(self.sockname))
                    self.sc.close()
                    self.server.remove_connection(self)
                    return
            except ConnectionResetError:
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                self.server.remove_connection(self)
                return

    def send(self, message):
        self.sc.sendall(message.encode('utf-8'))


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(1)
        print('Listening at', sock.getsockname())
        command = Command()
        command.start()


        while True:
            sc, sockname = sock.accept()
            print('Accepted a new connection form {} to {}'.format(sc.getpeername(), sc.getsockname()))

            # Create new thread
            server_socket = ServerSocket(sc, sockname, self)

            # Start new thread
            server_socket.start()

            self.connections.append(server_socket)
            print('Ready to receive messages from', sc.getpeername())

    def broadcast(self, message, source):
        for conn in self.connections:
            if conn.sockname != source:
                conn.send(message)

    def remove_connection(self, conn):
        self.connections.remove(conn)

class Command(threading.Thread):
    def __init__(self):
        super.__init__()
    def run(self):
        while True:
            ipt = input('')
            if ipt == '/quit':
                print()
                for x in server.connections:
                    x.sc.close()
                print()
                os.exit(0)


HOST = '127.0.0.1'
PORT = 8000

server = Server(HOST, PORT)
server.start()
