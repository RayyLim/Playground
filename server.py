SERVER_ADDRESS = './uds_socket'
RECV_BUFFER = 4096

import os
import socket
import select


class ChatServer():
    def __init__(self, server_address):
        self._socket_server = None
        self._connection_list = []
        self._server_address = server_address

    def create_socket_server(self):
        self._socket_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            os.unlink(self._server_address)
        except OSError:
            if os.path.exists(self._server_address):
                raise
        self._socket_server.bind(self._server_address)
        self._socket_server.listen(10)

    # Function to broadcast chat messages to all connected clients
    def broadcast_data(self, message):
        # Do not send the message to master socket and the client who has send us the message
        for connection in self._connection_list:
            if connection != self._socket_server:
                try:
                    connection.send(message)
                except socket.error:
                    # client connection closed
                    connection.close()
                    if connection in self._connection_list:
                        self._connection_list.remove(connection)

    def handle_disconnected_connection(self, sock):
        print "Client (%s) is offline" % (sock,)
        self.broadcast_data("\rClient (%s) is offline" % (sock.fileno(),))
        sock.close()
        if sock in self._connection_list:
            self._connection_list.remove(sock)

    def handle_new_connection(self):
        # Handle the case in which there is a new connection received through server_socket
        sockfd, _ = self._socket_server.accept()
        print "new connection", sockfd
        self._connection_list.append(sockfd)
        self.broadcast_data("\r[%s] entered room\n" % (sockfd.fileno(),))

    def run(self):
        self.create_socket_server()

        self._connection_list.append(self._socket_server)
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(self._connection_list, [], [])

            for sock in read_sockets:
                if sock is self._socket_server:
                    # New connection
                    self.handle_new_connection()
                else:
                    # Some incoming message from a client
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # Data received from client, process it
                        self.broadcast_data("\r" + '<' + str(sock.fileno()) + '> ' + data)
                    else:
                        # Client disconnected
                        self.handle_disconnected_connection(sock)
                        continue

        self._socket_server.close()

if __name__ == "__main__":
    ChatServer(SERVER_ADDRESS).run()


