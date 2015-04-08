__author__ = 'ray'

# import socket
# import sys
#
# # Create a UDS socket
# sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#
# # Connect the socket to the port where the server is listening
# server_address = './uds_socket'
# print >>sys.stderr, 'connecting to %s' % server_address
# try:
#     sock.connect(server_address)
# except socket.error, msg:
#     print >>sys.stderr, msg
#     sys.exit(1)
#
# try:
#
#     # Send data
#     message = 'This is the message.  It will be repeated.'
#     print >>sys.stderr, 'sending "%s"' % message
#     sock.sendall(message)
#
#     amount_received = 0
#     amount_expected = len(message)
#
#     while amount_received < amount_expected:
#         data = sock.recv(16)
#         amount_received += len(data)
#         print >>sys.stderr, 'received "%s"' % data
#
# finally:
#     print >>sys.stderr, 'closing socket'
#     sock.close()
#

# telnet program example
import socket, select, string, sys

def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()

#main function
if __name__ == "__main__":

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        server_address = './uds_socket'
        s.connect(server_address)
    except:
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host. Start sending messages'
    prompt()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    prompt()

            #user entered a message
            else :
                msg = sys.stdin.readline()
                s.send(msg)
                prompt()