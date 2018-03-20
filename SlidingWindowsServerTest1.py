from socket import *
import sys
import math
import Header
import select
import time
import datetime

# Definitions
last_ACKed = 0
windowSize = 2
msgSize = 60
kilobytes = 1024
megabytes = kilobytes * 1000
state = 0
fileDict = {}

# Create empty packet header
emptyhdr = Header.Header()
emptyhdr.Write()

# Create a UDP socket with Datagram
sock = socket(AF_INET, SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.setblocking(0)
sock.bind(server_address)

#______________________________________________________________________________________________________
#function for reading the sockets
def sockRead(sequenceNumber, clientAddress, window):
    #Use dictionary as parameter? With each packet in window? For resend
    #define global variables
    global state

    print "waiting to hear from client"
    #for reading msgs from client
    readSock = [sock]
    # empty list since we arent writing to sockets(used in queue
    writeSock = []
    # empty list - not interested in errors from select
    errorSock = []
    # time out variable since select has timeout built in
    timeout = 1

    totalTimeout = 0
    d1 = datetime.datetime.strptime(str(datetime.datetime.now().time()), "%H:%M:%S.%f")
    startTime = datetime.timedelta(minutes=d1.minute, seconds=d1.second, microseconds=d1.microsecond)
    timeoutTime = startTime + datetime.timedelta(seconds=3)
    #check sockets of server
    while(1):

        readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
        # if nothing is present in the sockets print a timeout error
        if not readReady and not writeReady and not errorReady:
            #print "timeout: No communication from the client"
            d2 = datetime.datetime.strptime(str(datetime.datetime.now().time()), "%H:%M:%S.%f")
            currentTime = datetime.timedelta(minutes=d2.minute, seconds=d2.second, microseconds=d2.microsecond)
            if currentTime < timeoutTime:
                print "waiting for cumulative ACK..."
            else:
                # Resend window
                totalTimeout+=1
                d3 = datetime.datetime.strptime(str(datetime.datetime.now().time()), "%H:%M:%S.%f")
                resetTime = datetime.timedelta(minutes=d3.minute, seconds=d3.second, microseconds=d3.microsecond)
                timeoutTime = resetTime + datetime.timedelta(seconds=3)
                for packet in window:
                    print "resending window..."
                    sock.sendto(window[packet], clientAddress)
            if totalTimeout == 5:
                state=0 #reset state variable
                print "connection to client lost"
                message = "CONNECTION LOST"
                return message, clientAddress
        else:
            #something present in the sockets - read it and return it
            for socket in readReady: #dont forget to calculate RTT
                message, serverAddr = socket.recvfrom(2048)
                #Confirm ACK
                ackmsgHeader = message[:40]
                ackHDR = Header.Header()
                ackHDR.Write()
                ackHeader = ackHDR.Read(ackmsgHeader)
                if ackHeader["datatype"] != "ACK":
                    continue
                if ackHeader["sequencenumber"] != sequenceNumber:
                    continue
                print "packet recieved..."
        
            return message, serverAddr

#______________________________________________________________________________________________________
#function for reading the sockets
def sockReadPUT():
    #define global variables
    global state

    print "waiting to hear from client"
    #for reading msgs from server
    readSock = [sock]
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
            print "timeout: No communication from the client"
            print readReady
            totalTimeout+=1
            if totalTimeout == 5:
                state=0  #reset state variable
                print "connection to client lost"
                message = ""
                return message
        else:
            #something present in the sockets - read it and return it
            for socket in readReady: #dont forget to calculate RTT
                message, serverAddr = socket.recvfrom(2048)
                print "packet recieved..."
        
            return message
#sock.setblocking(0)
def parseMessage(message):
    hdr = Header.Header()
    hdr.Write()
    print"msg"
    print message
    headerData = message[:39]
    print repr(headerData)
    headerdict = hdr.Read(headerData)

    

    #splitMessage = message.split("@")
    
    data = message[40:]
    index = headerdict["sequencenumber"]
    print "index"
    print index
    fileName = headerdict["options"]
    #index:message populate file dict
    #if data exists its part of the file and should be stored
    if len(data) != 0:
        fileDict[index] = data
    
    return data, index, fileName

def saveFile(reqHead):
    global fileDict
    print "File Transfer complete... Writing File to disk..."
    #filename = open(reqHead.options, "w")
    #filename = open(reqHead["options"], "w")
    filename = open("output.txt", "w")
    print "File DICT"
    print fileDict
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

def sendAck(index,fileName, clientAddress):
    ack = Header.Header()
    #populate it with the sequencenum and file name and ACK message type
    ack.datatype = "ACK"
    ack.sequencenumber = str(index)
    ack.options = str(fileName)
    ackHead = ack.Write()

    #send just the ACK header
    sock.sendto(ackHead, clientAddress)

while True:
    print >>sys.stderr, '\nwaiting to receive message'
    #data, address = sock.recvfrom(4096)
    emptyDictionary = {}
    data, address = sockRead("", server_address, emptyDictionary)
    
    print >>sys.stderr, 'received %s bytes from %s' % (len(data), address)
    print >>sys.stderr, data
    
    if data:
        if len(data) > 39:
            # Parse header
            HDR = Header.Header()
            recvHDR = HDR.Read(data)
            #recvHDR = HDR.Read(testhdr.Write())
            # Check datatype
            if recvHDR["datatype"] == "GET":
                # GET file from local file system
                filename = recvHDR["options"]
                filepath = filename
                fileOBJ = open(filepath)
                # Read entire file and calculate packets for file
                filedata = fileOBJ.read()
                filebytes = len(filedata)
                filepackets = int(math.floor(filebytes/kilobytes + 1))
                fileOBJ.close()
                
                # STOP-AND-WAIT needed here: Send file parts
                binaryDictionary = {}
                seqNumber = 1
                for i in range(0, filebytes+1, msgSize):
                    #Create data header
                    #seqNumber = 1
                    dataHDR = Header.Header()
                    dataHDR.datatype = "DATA"
                    dataHDR.filesize = str(filebytes)
                    dataHDR.numberofpackets = str(filepackets)
                    dataHDR.packetsize = str(kilobytes)
                    dataHDR.timetolive = "5"
                    dataHDR.options = filename
                    dataHDR.sequencenumber = str(seqNumber)
                    dataheader = dataHDR.Write()
                    headerBytes = bytearray(dataheader)
                    
                    # Create the message sequence and join with the header
                    #fileOBJ = open(filepath)
                    with open(filepath, "rb") as binary_file:
                        #Seek to specified position
                        binary_file.seek(i)
                        messageBytes = headerBytes + binary_file.read(msgSize)
                    #messageSequence = fileOBJ.read(kilobytes)
                    #messageBytes = headerBytes + messageSequence
                    #fileOBJ.close()
                    
                    #How to send window size?
                    #Save all binary to dictionary with sequence number
                    binaryDictionary[seqNumber] = messageBytes
                    #Don't send or receive in this loop, move on to another loop outside of this one
                    #Loop through the window size, and send all messages beginning with sequence 1
                    #Save the last ack (sequence number) in the global variable
                    #Sock read with this sequence, and if ack received, continue on with next batch
                    
                    # Send message sequence
                    #sent = sock.sendto(messageBytes, address)
                    
                    #STOP-AND-WAIT
                    #clientMessage = sockRead(messageBytes, address)
                    
                    seqNumber = seqNumber + 1
                    
                #Loop through the window size, and send all messages beginning with sequence 1
                beginWindow = 1
                windowDictionary = {}
                for sequenceNumber, binaryData in binaryDictionary.items():
                    if beginWindow <= windowSize:
                        #Add message to dictionary
                        windowDictionary[sequenceNumber] = binaryData
                        # Send message
                        sock.sendto(binaryData, address)
                        beginWindow = beginWindow + 1
                        #Save the last ack (sequence number) in the global variable
                        last_ACKed = sequenceNumber
                        if beginWindow > windowSize:
                            #Sock read with this sequence, and if ack received, continue on with next batch
                            clientMessage = sockRead(sequenceNumber - 1, address, windowDictionary)
                            if "CONNECTION LOST" in clientMessage:
                                break
                            else:
                                #Reset window
                                beginWindow = 1
                                # Reset window dictionary
                                windowDictionary = {}
                                #Save the last ack (sequence number) in the global variable
                                last_ACKed = sequenceNumber
                    else:
                        #Add message to dictionary
                        #windowDictionary[sequenceNumber] = binaryData
                        #Sock read with this sequence, and if ack received, continue on with next batch
                        #clientMessage = sockRead(sequenceNumber - 1, address, windowDictionary)
                        #Reset window
                        #beginWindow = 1
                        # Reset window dictionary
                        #windowDictionary = {}
                        #Save the last ack (sequence number) in the global variable
                        #last_ACKed = sequenceNumber
                        print "unknown packet"
                #Send EOF
                sentEOF = sock.sendto(emptyhdr.Write() + "", address)    
            elif recvHDR["datatype"] == "PUT":
                putfile = "true"
                print "PUT message received"
                #Send ACK 0
                sendAck(0, recvHDR["options"], address)
                print "PUT ACK SENT"
                #Stop-and-wait here for response; use readsock
                #Get data packet and store to dictionary and repeat
                #Need to check for EOF
                #continuously check the socket and handle the mssage storing it to dict
                while(1):
                    #check and read the socket
                    print "Read Sock for DATA after ACK sent for PUT"
                    message=sockReadPUT()
                    print "DATA message from PUT routine"
                    print message
                    if len(message)==0:
                        #server lost and get out of function
                        print "no message"
                    else: #there was a message from the server
                        #split the header and message up
                        print "message recieved and ready for interpretation"
                        
                        #parse message and populate the dictionary
                        data,index,fileName = parseMessage(message)
                        print "data after parse"
                        print data
                        print "len of data"
                        print len(data)
                        #send an ack back to the server that it got the message
                        sendAck(index,fileName,address)
            
                        #check to see if EOF - if EOF break then write to file
                        if len(data) == 0:
                            print "File Transfer Complete"
                            saveFile(recvHDR)
                            break
                            #Write file
            elif recvHDR["datatype"] == "DATA":
                data = "true"
            elif recvHDR["datatype"] == "CLOSE":
                close = "true"
            else:
                close = "true"
                sent = sock.sendto("Not Supported.", address)
    
            #sent = sock.sendto(data, address)
print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)