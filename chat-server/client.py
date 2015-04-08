RECV_BUFFER = 4096
SOCKET_ADDRESS = './uds_socket'
__author__ = 'ray'

import socket
import select
import sys


class ChatClient():
    def __init__(self):
        self._socketobject = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def connect_to_server(self):
        self._socketobject.settimeout(2)
        self._socketobject.connect(SOCKET_ADDRESS)

    def run(self):
        self.connect_to_server()

        print 'Connected to remote host. Start sending messages'
        prompt()

        while 1:
            socket_list = [sys.stdin, self._socketobject]

            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

            for sock in read_sockets:
                # incoming message from remote server
                if sock == self._socketobject:
                    data = sock.recv(RECV_BUFFER)
                    if not data:
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else:
                        sys.stdout.write(data)
                        prompt()

                # user entered a message
                else:
                    msg = sys.stdin.readline()
                    self._socketobject.send(msg)
                    prompt()


def prompt(p='You'):
    sys.stdout.write('<%s> ' % p)
    sys.stdout.flush()


if __name__ == "__main__":
    ChatClient().run()



