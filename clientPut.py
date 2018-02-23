import sys
import re
import time
from socket import *
import select
from Header import Header
import os

#define constants
serverAddr =('localhost',50000)
msgSize = 60 #number of bytes in message (header is 40 bytes)
#if total timeout reacheed connection is lost
def connLost():
    #code to run when connection to server is lost

    print "Connection to Server lost"
    #after connection lost revert back to idle and ask for input


#function for gather input
def input():
    reqType = raw_input("Get or Put?")
    fileName = raw_input)"Which File?")
    

#define the header

# Create test header
testhdr = Header()
testhdr.datatype = "PUT"
testhdr.filesize = "X"
testhdr.numberofpackets = "1"
testhdr.sequencenumber = "1"
testhdr.packetsize = "100"
testhdr.timetolive = "5"
testhdr.options = "charlie_test.py"
head = testhdr.Write()

print repr(head)

#open file to read
fp = open(testhdr.options, "r")
#read the file and store into dict with index
putDict = {}
index=0
while True:
    putDict[index] = fp.read(msgSize)
    
    if len(putDict[index])<80:
        print "EOF"
        break
    index+=1
print "dict of file with indicies", repr(putDict)

#close file
fp.close()

print repr(putDict)



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

#create header module



# create clientSocket object
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(0)# set blocking to false so timeouts work

# set up client socket to recieve# get input from the user


# set up lists to be used in select

#function
#for reading msgs from server
readSock = [clientSocket]
# empty list since we arent writing to sockets(used in queue
writeSock = []
# empty list - not interested in errors from select
errorSock = []
# time out variable since select has timeout built in
timeout = 5

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
    totalTimeout+=1
    if totalTimeout == 5:
        connLost()

#if there is something present in the read sockets read it and print it out
for socket in readReady: #dont forget to calculate RTT
    message, serverAddr = socket.recvfrom(2048)
    print message
