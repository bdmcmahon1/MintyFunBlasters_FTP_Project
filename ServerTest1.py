from socket import *
import sys
import math
import Header

# Definitions
msgSize = 60
kilobytes = 1024
megabytes = kilobytes * 1000

# Create empty packet header
emptyhdr = Header.Header()
emptyhdr.Write()

# Create a UDP socket with Datagram
sock = socket(AF_INET, SOCK_DGRAM)
#sock.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

while True:
    print >>sys.stderr, '\nwaiting to receive message'
    data, address = sock.recvfrom(4096)
    
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
                for i in range(0, filebytes+1, msgSize):
                    #Create data header
                    seqNumber = 1
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