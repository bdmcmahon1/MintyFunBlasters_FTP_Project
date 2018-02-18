import sys, re
import time
from socket import *
import select

serverAddr = ('localhost', 50000)

def usage():
    print "usage: %s [--serverAddr host:port]" % sys.argv[0]
    sys.exit(1)

try:
    args = sys.argv[1: ]
    while args:
        sw = args[0];
        del args[0]
        if sw == "--serverAddr":
            addr, port = re.split(":", args[0]); del args[0]
            serverAddr = (addr, int(port))
        else :
            print "unexpected parameter %s" % args[0]
            usage();

except:
    usage()


# create clientSocket object
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(0)# set blocking to false so timeouts work

# set up client socket to recieve# get input from the user
message = raw_input("Input lowercase msg:")

# set up lists to be used in select

#function
#for reading msgs from server
readSock = [clientSocket]
writeSock = []# empty list since we arent writing to sockets(used in queue ? )
errorSock = []# empty list - not interested in errors from select
timeout = 5# time out variable since select has timeout built in

#mark start time for RTT calc
# startTime = time.time()# send the data to the server
clientSocket.sendto(message, serverAddr)
print "message sent. Ready to recieve" 
#recieve message from server

readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
# if nothing is present in the sockets print a timeout error
if not readReady and not writeReady and not errorReady:
    print "timeout: No communication from the server"

#if there is something present in the read sockets read it and print it out
for socket in readReady: #dont forget to calculate RTT
    message, serverAddr = socket.recvfrom(2048)
    print message
