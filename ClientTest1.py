import sys, re
import time
from socket import *
import select
import Header
import os

serverAddr = ('localhost', 50000)

#define constants
msgSize = 80
readData = {}

def usage():
    print "usage: %s [--serverAddr host:port]" % sys.argv[0]
    sys.exit(1)
#idle state
def input():
    header = Header()
    header.datatype = raw_input("What would you like to do:")
    header.options = raw_input("Which file would you like to GET/PUT?")
    header.filesize = os.path.getsize(header.options())

#put request state    
def putFile(header.options(),msgSize,readData):
    fp = open(header.options(), "rb")
    
    index=0
    while True:
        #populate a dictionary with messages of broken up file
        #keys are indexes and values are the messages for each index
        readData["index"] = fp.read(msgsize)
        index++
        if readData[-1] < msgSize:
            break
#total time out return to idle        
def connLost():
    #code to run when connection to server is lost

    print "Connection to Server lost"
    #after connection lost revert back to idle and ask for input
    input()
    
def getFile():
    #Send get message to server

    #create file w/ file name from user to store data

    #use select/recieveMsg() to recieve message
    


def recieveMsg():
    #code that will recieve a message and split the header

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

#create header module



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

totalTimeout = 0

#mark start time for RTT calc
# startTime = time.time()# send the data to the server
clientSocket.sendto(message, serverAddr)
print "message sent. Ready to recieve" 
#recieve message from server

readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
# if nothing is present in the sockets print a timeout error
if not readReady and not writeReady and not errorReady:
    print "timeout: No communication from the server"
    totalTimeout++
    if totalTimeout == 5:
        connLost()

#if there is something present in the read sockets read it and print it out
for socket in readReady: #dont forget to calculate RTT
    message, serverAddr = socket.recvfrom(2048)
    print message
