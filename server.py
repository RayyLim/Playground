SERVER_ADDRESS = './uds_socket'
RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2

import os
import socket
import select

# Function to broadcast chat messages to all connected clients
def broadcast_data(connection_list, socket_server, message):
    # Do not send the message to master socket and the client who has send us the message
    for connection in connection_list:
        if connection != server_socket:
            try:
                connection.send(message)
            except socket.error:
                # client connection closed
                connection.close()
                if connection in connection_list:
                    connection_list.remove(sock)


def create_socket_server():
    sock_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        os.unlink(SERVER_ADDRESS)
    except OSError:
        if os.path.exists(SERVER_ADDRESS):
            raise
    sock_server.bind(SERVER_ADDRESS)
    sock_server.listen(10)
    return sock_server


if __name__ == "__main__":

    # List to keep track of socket descriptors
    connection_list = []

    server_socket = create_socket_server()

    # Add server socket to the list of readable connections
    connection_list.append(server_socket)

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])

        for sock in read_sockets:
            # New connection
            if sock == server_socket:
                print "new connection"
                # Handle the case in which there is a new connection received through server_socket
                sockfd, addr = server_socket.accept()
                print "new connection", sockfd, addr
                connection_list.append(sockfd)

                broadcast_data(connection_list, server_socket, "[%s:%s] entered room\n" % (sockfd, addr))

            # Some incoming message from a client
            else:
                # Data received from client, process it
                data = sock.recv(RECV_BUFFER)
                if data:
                    broadcast_data(connection_list, server_socket,
                                   "\r" + '<' + str(sock.getpeername()) + '> ' + data)
                else:
                    print "Client (%s, %s) is offline" % (sock, addr)
                    broadcast_data(connection_list, server_socket, "Client (%s, %s) is offline" % (sock, addr))

                    sock.close()
                    if sock in connection_list:
                        connection_list.remove(sock)
                    continue

    server_socket.close()

