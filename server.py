__author__ = 'ray'

# import socket
# import sys
# import os
#
# server_address = './uds_socket'
#
# # Make sure the socket does not already exist
# try:
#     os.unlink(server_address)
# except OSError:
#     if os.path.exists(server_address):
#         raise
#
# # Create a UDS socket
# sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#
#
# # Bind the socket to the port
# print >>sys.stderr, 'starting up on %s' % server_address
# sock.bind(server_address)
#
# # Listen for incoming connections
# sock.listen(1)
#
# while True:
#     # Wait for a connection
#     print >>sys.stderr, 'waiting for a connection'
#     connection, client_address = sock.accept()
#     try:
#         print >>sys.stderr, 'connection from', client_address
#
#         # Receive the data in small chunks and retransmit it
#         while True:
#             data = connection.recv(16)
#             print >>sys.stderr, 'received "%s"' % data
#             if data:
#                 print >>sys.stderr, 'sending data back to the client'
#                 connection.sendall(data)
#             else:
#                 print >>sys.stderr, 'no more data from', client_address
#                 break
#
#     finally:
#         # Clean up the connection
#         connection.close()

# Tcp Chat server

import socket, select

#Function to broadcast chat messages to all connected clients
def broadcast_data (sock, message):
    #Do not send the message to master socket and the client who has send us the message
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection may be, chat client pressed ctrl+c for example
                socket.close()
                CONNECTION_LIST.remove(socket)

if __name__ == "__main__":

    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2

    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = './uds_socket'
    server_socket.bind(server_address)
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            #New connection
            if sock == server_socket:
                print "new connection"
                # Handle the case in which there is a new connection received through server_socket
                sockfd, addr = server_socket.accept()
                print "new connection", sockfd, addr
                CONNECTION_LIST.append(sockfd)

                broadcast_data(sockfd, "[%s:%s] entered room\n" % (sockfd, addr))

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        broadcast_data(sock, "\r" + '<' + str(sock.getpeername()) + '> ' + data)

                except:
                    broadcast_data(sock, "Client (%s, %s) is offline" % (sockfd, addr))
                    print "Client (%s, %s) is offline" % (sockfd, addr)
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue

    server_socket.close()