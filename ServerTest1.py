from socket import *
import sys
import math
import Header
import select

# Definitions
msgSize = 60
kilobytes = 1024
megabytes = kilobytes * 1000

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
def sockRead(msgResend, clientAddress):
    #define global variables
    global state

    print "waiting to hear from server"
    #for reading msgs from server
    readSock = [sock]
    # empty list since we arent writing to sockets(used in queue
    writeSock = []
    # empty list - not interested in errors from select
    errorSock = []
    # time out variable since select has timeout built in
    timeout = 1

    totalTimeout = 0
    
    # Get message header
    if len(msgResend) > 0:
        msgHeader = msgResend[:40]
        msgHDR = Header.Header()
        msgHDR.Write()
        messageHeader = msgHDR.Read(msgHeader)
    #check sockets of server
    while(1):

        readReady, writeReady, errorReady = select.select(readSock, writeSock, errorSock, timeout)
        # if nothing is present in the sockets print a timeout error
        if not readReady and not writeReady and not errorReady:
            print "timeout: No communication from the client"
            #sock.sendto(msgResend, clientAddress)
            totalTimeout+=1
            if totalTimeout == 5:
                state=0 #reset state variable
                print "connection to server lost"
                message = ""
                return message
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
                    if ackHeader["sequencenumber"] != messageHeader["sequencenumber"]:
                        continue
                print "packet recieved..."
        
            return message, serverAddr

#______________________________________________________________________________________________________

#sock.setblocking(0)

while True:
    print >>sys.stderr, '\nwaiting to receive message'
    #data, address = sock.recvfrom(4096)
    data, address = sockRead("", server_address)
    
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
                    
                    # Send message sequence
                    sent = sock.sendto(messageBytes, address)
                    
                    #STOP-AND-WAIT
                    clientMessage = sockRead(messageBytes, address)
                    seqNumber = seqNumber + 1
                    
                #Send EOF
                sentEOF = sock.sendto(emptyhdr.Write() + "", address)    
            elif recvHDR["datatype"] == "PUT":
                putfile = "true"
            elif recvHDR["datatype"] == "DATA":
                data = "true"
            elif recvHDR["datatype"] == "CLOSE":
                close = "true"
            else:
                close = "true"
                sent = sock.sendto("Not Supported.", address)
    
            #sent = sock.sendto(data, address)
print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)