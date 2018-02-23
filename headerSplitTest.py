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

#define constants
serverAddr =('localhost',50000)

#define and create client
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.setblocking(0)# set blocking to false so timeouts work

#______________________________________________________________________________________________________

#function for gathering inputs
def inputs():
    #define global variables
    global state
    
    #create header to populate request message with
    
    datatype = raw_input("GET or PUT a file?\n")
    filename = raw_input("What file do you want/have?\n")
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
def getFile(reqHead):
    #define global variables
    global state
    fileDict = {}
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
            splitMessage,data,index,fileName = parseMessage(message)

            #send an ack back to the server that it got the message
            sendAck(index,fileName)

            #check to see if EOF - if EOF break then write to file
            if len(data) == 0:
                print "File Transfer Complete"
                saveFile(reqHead)
                break
            
    #wait for data
#______________________________________________________________________________________________________

def saveFile(reqHead):
    
    print "File Transter complete... Writing File to disk..."
    filename = open(reqHead.options, "w")
    for keys in fdict:
        filename.write(fdict[keys])
    filename.close()

    print "File saved to disk"


#______________________________________________________________________________________________________

def sendAck(index,fileName):
    ack = Header()
    #populate it with the sequencenum and file name and ACK message type
    ack.datatype = ACK
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
    timeout = 5

    totalTimeout = 0
    
    #check sockets of server
    while(1):

        readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
        # if nothing is present in the sockets print a timeout error
        if not readReady and not writeReady and not errorReady:
            print "timeout: No communication from the server"
            totalTimeout+=1
            if totalTimeout == 5:
                state=0 #reset state variable
                print "connection to server lost"
                break
        else:
            #there is something to read just get out of loop
            break
    
    if totalTimeout == 5:
        #conenction to server lost leave function
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
    splitMessage = message.split("@")
    
    data = splitMessage[-1]
    index = splitMessage[1]
    fileName = splitMessage[-2]
    #index:message populate file dict
    #if data exists its part of the file and should be stored
    if len(data) != 0:
        fileDict[index] = data
    
    return splitMessage, data, index, fileName


#______________________________________________________________________________________________________

#______________________________________________________________________________________________________

#______________________________________________________________________________________________________


#asdk for inputs and check program status

state,reqHead = inputs()

print state, reqHead

if state == 1:
    getFile(reqHead);
else:
    putFile(reqHead);




'''
#test opening and splitting a header from the message

message1 = "GET@1@storeFileTest.py@message1 data fart "
message2 = "GET@2@storeFileTest.py@message2 data fart "
message3 = "GET@3@storeFileTest.py@message3 data fart  "


splitMessage1 = message1.split("@")
splitMessage2 = message2.split("@")
splitMessage3 = message3.split("@")

allMessages = [splitMessage1,splitMessage2,splitMessage3]

fileDict = {}
for msg in allMessages :
    fileDict[msg[1]] = msg[-1]


print fileDict

orderedFileDict = collections.OrderedDict(sorted(fileDict.items()))

print 'ordered dict'
print orderedFileDict

#ok now stor that shit in a file

#create a file
file = open(splitMessage1[2], "w")
file.write(splitMessage1[-1])
file.write(splitMessage2[-1])
file.write(splitMessage3[-1])
file.close()
'''
