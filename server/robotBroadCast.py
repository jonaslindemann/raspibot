from time import sleep
from socket import *

import fcntl
import struct

from threading import *

class RaspiBotBroadCaster(object):
    def __init__(self, ifname):
        self.ifname = ifname
        self.port = 50000
        self.magic = "raspibot"
        self.queryIp()
        self.isConnected = False
        
    def queryIp(self):
        s = socket(AF_INET, SOCK_DGRAM)
        self.ipNumber = inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', self.ifname[:15])
        )[20:24])
        
        print("Local ip = %s" % self.ipNumber)
        
    def connect(self):
		self.s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
		self.s.bind(('', 0))
		self.s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
		self.isConnected = True
        
    def close(self):
        if self.isConnected:
            self.s.close()
            
        self.isConnected = False
        
    def broadCast(self):
		if self.isConnected:
			data = self.magic+self.ipNumber
			self.s.sendto(data, ('<broadcast>', self.port))
        
if __name__ == "__main__":

    botBroadCaster = RaspiBotBroadCaster("wlan0")
    botBroadCaster.connect()
    while True:
        print("Sending..")
        botBroadCaster.broadCast()
        sleep(5)
