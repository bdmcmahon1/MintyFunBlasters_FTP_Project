import sys
import re
import time
from socket import *
import select
from Header import Header
import os
import collections

#define global variables
state = 0
fileDict = {}
putFile = ""
#create empty header for use later on
emptyhdr = Header()
emptyhdr.Write()

messageSize = 60
#define constants
serverAddr =('localhost',10000)



#define and create client
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(0)# set blocking to false so timeouts work

#______________________________________________________________________________________________________

#function for gathering inputs
def inputs():
    #define global variables
    global state
    global putFile
    #create header to populate request message with
    while(1):
        datatype = raw_input("GET or PUT a file?\n")
        if (datatype == "GET") or (datatype == "PUT"):
            break
        else:
            print "Please input a proper request (GET or PUT)"
    while(1):
        filename = raw_input("What file do you want/have?\n")
        if datatype == "PUT":
            if os.path.isfile(filename):
                print "Fetching File..."
                putFile = filename
                
                break
            else:
                print "File does not exist. Choose another file..."
        if datatype == "GET":
            break
    print"Processing Request..."

    #create instance of header class
    request = Header()
    #populate it with the input and write a header for the request
    request.datatype = datatype
    request.options = filename
    reqHead = request.Write()
    #update state variable
    if request.datatype == "GET":
        state=1
    else:
        state=2
    #return the header meant to be sent with the request
    return state, reqHead

#______________________________________________________________________________________________________


#function for getting file
def fileGet(reqHead):
    #define global variables
    global state
    global fileDict
    #send request to server
    clientSocket.sendto(reqHead, serverAddr)
    print "request sent - waiting for response"
    #continuously check the socket and handle the mssage storing it to dict
    while(1):
        #check and read the socket
        message=sockRead()
        
        if len(message)==0:
            #server lost and get out of function
            return
        else: #there was a message from the server
            #split the header and message up
            print "message recieved and ready for interpretation"
            
            #parse message and populate the dictionary
            data,index,fileName,messageType = parseMessage(message)
            print "data after parse"
            print data
            print "len of data"
            print len(data)
            #send an ack back to the server that it got the message
            sendAck(index,fileName)

            #check to see if EOF - if EOF break then write to file
            if len(data) == 0:
                print "File Transfer Complete"
                saveFile(reqHead)
                #clear file Dict for next operation
                fileDict = {}
                break
            
    #wait for data
#______________________________________________________________________________________________________

def saveFile(reqHead):
    global fileDict
    print "File Transter complete... Writing File to disk..."
    #filename = open(reqHead.options, "w")
    filename = open('outputTest.txt', "w")
    Keys = fileDict.keys()
    Keys.sort()
    # keys are strings - change them to integers then sort all of them
    intDict = {int(k) : v for k, v in fileDict.items()}
    print "sorted"
    print intDict

    #print sorted(fileDict.keys)
    for key in sorted(intDict.iterkeys()):
        filename.write(intDict[key])
        
    filename.close()
    #print fileDict
    print "File saved to disk"


#______________________________________________________________________________________________________

def sendAck(index,fileName):
    ack = Header()
    #populate it with the sequencenum and file name and ACK message type
    ack.datatype = "ACK"
    ack.sequencenumber = index
    ack.options = fileName
    ackHead = ack.Write()

    #send just the ACK header
    clientSocket.sendto(ackHead, serverAddr)
    

#______________________________________________________________________________________________________
#function for reading the sockets
def sockRead():
    #define global variables
    global state

    print "waiting to hear from server"
    #for reading msgs from server
    readSock = [clientSocket]
    # empty list since we arent writing to sockets(used in queue
    writeSock = []
    # empty list - not interested in errors from select
    errorSock = []
    # time out variable since select has timeout built in
    timeout = 1

    totalTimeout = 0
    
    #check sockets of server
    while(1):

        readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
        # if nothing is present in the sockets print a timeout error
        if not readReady and not writeReady and not errorReady:
            print "timeout: No communication from the server"
            print readReady
            totalTimeout+=1
            if totalTimeout == 5:
                state=0  #reset state variable
                print "connection to server lost"
                message = ""
                return message
        else:
            #something present in the sockets - read it and return it
            for socket in readReady: #dont forget to calculate RTT
                message, serverAddr = socket.recvfrom(2048)
                print "packet recieved..."
        
            return message

#______________________________________________________________________________________________________

def parseMessage(message):
    #if server message is an empty msg with no header - total timeout
    if len(message) == 0:
        return 0,0,0,0
    #otherwise handle the file as normal
    else:
        hdr = Header()
        hdr.Write()
        print"msg"
        print message
        headerData = message[:39]
        print repr(headerData)
        headerdict = hdr.Read(headerData)

    

        #splitMessage = message.split("@")
        messageType = headerdict["datatype"]
        data = message[40:]
        index = headerdict["sequencenumber"]
        fileName = headerdict["options"]
        #index:message populate file dict
        #if data exists its part of the file and should be stored
        if len(data) != 0:
			fileDict[index] = data
        
        return data, index, fileName, messageType


#______________________________________________________________________________________________________
#function for put file request
def filePut(reqHead):
    #define global variables
    global state
    global fileDict
    global putFile
    global messageSize
    global serverAddr
    global emptyhdr
    
    fileDict = {}
    #send request to server
    messageSend = reqHead
    print "header built. Sending PUT request to server..."
    clientSocket.sendto(messageSend, serverAddr)
    #wait for ACK regarding request
    #check and read the socket
    message=sockReadPut(messageSend)
    #if message is recieved split message to hader and data to check ACK
    data, index, filename, messageType = parseMessage(message)
    #check for ack
    if messageType == "ACK":
        #open file and break it up into fileDict
        print "Server received request. Preparing file for transport..."
        #read file and populate dictionary with it
    elif (len(message) == 0):
        print "Server Timed out. Closing application."
        return
    
    
    #brians way of doing things---------------------------------
        
    #open file and get relevant data out of it for header
    print putFile
    FILE = open(putFile, "rb")
    fileData = FILE.read()
    
    filebytes = len(fileData)
    filepackets = filebytes/messageSize
    packetsize = 100
    FILE.close()


    # STOP-AND-WAIT needed here: Send file parts
    #set up sequence number for sending data
    seqNumber = 1
    #for i (start at 0) to end of file (i increments by message size
    for i in range(0, filebytes+1, messageSize):
        #Create data header
        dataHDR = Header()
        dataHDR.datatype = "DATA"
        dataHDR.filesize = str(filebytes)
        dataHDR.numberofpackets = str(filepackets)
        dataHDR.packetsize = str(packetsize)
        dataHDR.timetolive = "5"
        dataHDR.options = putFile
        dataHDR.sequencenumber = str(seqNumber)
        dataheader = dataHDR.Write()
        #match data types just incase using dataheader doesnt work
        headerBytes = bytearray(dataheader)
        
        # Create the message sequence and join with the header
        #fileOBJ = open(filepath)
        #open the file > step fid in the file where i is (0 then 60 then 120....)
        with open(putFile, "rb") as binary_file:
            #Seek to specified position
            binary_file.seek(i)
            #create message with dataheader and reading msgSize bytes from file
            messageSend = dataheader + binary_file.read(messageSize)
                        
            # Send message sequence
            clientSocket.sendto(messageSend, serverAddr)
                    
            #STOP-AND-WAIT
            serverMessage = sockReadPut(messageSend)
            #check if it is an ACK - parse message first
            data, index, filename, messageType = parseMessage(message)
            #if ack is for correct sequence number increment seq num and start the loop over again
            if messageType == "ACK":
                seqNumber = seqNumber + 1
            #if not ack for correct sequence number restart loop at current sequence number
            #if there was a total timeoutleave this loop - check again in the for loop
            elif len(serverMessage) == 0:
                break
                #file closes automatically with with loop type
    #if there was a total timeout leave the for loop        
		if len(serverMessage) == 0:
			break                  
    #Send EOF (empty data message with dummt header
  
    sentEOF = clientSocket.sendto(emptyhdr.Write() + "", serverAddr)
                

    #-----------------------------------------------------------

#______________________________________________________________________________________________________

def sockReadPut(messageSend):
    #define global variables
    global state
    global serverAddr
    print "waiting to hear from server"
    #for reading msgs from server
    readSock = [clientSocket]
    # empty list since we arent writing to sockets(used in queue
    writeSock = []
    # empty list - not interested in errors from select
    errorSock = []
    # time out variable since select has timeout built in
    timeout = 1

    totalTimeout = 0
    
    #check sockets of server
    while(1):

        readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
        # if nothing is present in the sockets print a timeout error
        if not readReady and not writeReady and not errorReady:
            print "timeout: No communication from the server, Resending Packet"
            #resend message
            clientSocket.sendto(messageSend, serverAddr)
            totalTimeout+=1
            if totalTimeout == 5:
                state=0  #reset state variable
                print "connection to server lost"
                messageRecv = ""
                return messageRecv
        else:
            #something present in the sockets - read it and return it
            for socket in readReady: #dont forget to calculate RTT
                messageRecv, serverAddr = socket.recvfrom(2048)
                print "packet recieved..."
        
            return messageRecv


#______________________________________________________________________________________________________


#asdk for inputs and check program status
while(1):
	state,reqHead = inputs()

	print state, reqHead

	if state == 1:
		fileGet(reqHead)
	else:
		filePut(reqHead)



