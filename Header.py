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