import socket
import sys
import math

# Header class
class Header(object):
    def __init__(self):
        self.datatype = "X"
        self.filesize = "X"
        self.numberofpackets = "X"
        self.sequencenumber = "X"
        self.packetsize = "X"
        self.timetolive = "X"
        self.options = "X"
    def Write(self):
        return self.datatype + "-" + self.filesize + "-" + self.numberofpackets + "-" + self.sequencenumber + "-" + self.packetsize + "-" + self.timetolive + "-" + self.options
    def Read(self, hdr):
        # Return dictionary
        hdrdictionary = {}
        n = 0
        for s in hdr.split("-"):
            hdrdictionary[n] = s
            n = n + 1
        hdrdictionary["datatype"] = hdrdictionary.pop(0)
        hdrdictionary["filesize"] = hdrdictionary.pop(1)
        hdrdictionary["numberofpackets"] = hdrdictionary.pop(2)
        hdrdictionary["sequencenumber"] = hdrdictionary.pop(3)
        hdrdictionary["packetsize"] = hdrdictionary.pop(4)
        hdrdictionary["timetolive"] = hdrdictionary.pop(5)
        hdrdictionary["options"] = hdrdictionary.pop(6)
        return hdrdictionary

# Definitions
kilobytes = 1024
megabytes = kilobytes * 1000

# Create test header
testhdr = Header()
testhdr.datatype = "GET"
testhdr.filesize = "X"
testhdr.numberofpackets = "1"
testhdr.sequencenumber = "1"
testhdr.packetsize = "1024"
testhdr.timetolive = "5"
testhdr.options = "filename.txt"
testhdr.Write()

# Create a TCP/IP socket with Datagram
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
        # Parse header
        HDR = Header()
        recvHDR = HDR.Read(testhdr.Write())
        # Check datatype
        if recvHDR["datatype"] == "GET":
            # GET file from local file system
            filename = recvHDR["options"]
            filepath = "C:\\" + filename
            fileOBJ = open(filepath)
            # Read entire file and calculate packets for file
            filedata = fileOBJ.read()
            filebytes = len(filedata)
            filepackets = int(math.floor(filebytes/kilobytes + 1))
            fileOBJ.close()
            
            # STOP-AND-WAIT needed here: Send file parts
            for i in range(0, filebytes+1, kilobytes):
                #Create data header
                seqNumber = 1
                dataHDR = Header()
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
                fileOBJ = open(filepath)
                messageSequence = fileOBJ.read(kilobytes)
                messageBytes = headerBytes + messageSequence
                fileOBJ.close()
                
                # Send message sequence
                sent = sock.sendto(messageBytes, address)
                seqNumber = seqNumber + 1
                
        elif recvHDR["datatype"] == "PUT":
            putfile = "true"
        elif recvHDR["datatype"] == "DATA":
            data = "true"
        elif recvHDR["datatype"] == "CLOSE":
            close = "true"
        else:
            close = "true"

        #sent = sock.sendto(data, address)
print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)