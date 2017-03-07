import sys
import zerorpc
import time

from socket import *

class RaspiBot(object):
    def __init__(self):
        print("Creating client...")
        self._client = zerorpc.Client()

        self.ip = ""
    
    def connect(self):
              
        if self.ip == "":
            self.find()

        print("Connecting to %s" % self.ip)
        self._client.connect("tcp://%s:4242" % self.ip)   
        
    def disconnect(self):
        print("Close robot")
        self._client.clear(0, 0, 0)
        print("Stopping sensor thread")
        self._client.close()
            
    def find(self):
        
        PORT = 50000
        MAGIC = b"raspibot"    
    
        print("Opening socket...")
        s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Make Socket Reusable
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) # Allow incoming broadcasts
        s.setblocking(False) # Set socket to non-blocking mode
        print("Binding to port...")
        s.bind(('', PORT))
    
        print("Waiting for response...")
    
        while True:
            try:
                data, addr = s.recvfrom(1024) # Buffer size is 8192. Change as needed.
                if data.startswith(MAGIC):
                    print("got service announcement from", data[len(MAGIC):])
                    break
            except:
                pass
            
            time.sleep(1)
    
        self.ip = str(addr[0])
        
    def sleep(self, seconds):
        time.sleep(seconds)
        
    def doMotor(self, port, speed):
        self._client.doMotor(port, speed)

    def showMessage(self, message):
        self._client.showMessage(message)

    def clear(self, r, g, b):
        self._client.clear(r, g, b)

    def setRotation(self, angle):
        self._client.setRotation(angle)

    def flipVert(self):
        self._client.flipVert()

    def flipHoriz(self):
        self._client.flipHoriz()

    def setPixels(self, pixels):
        self._client.setPixels(pixels)

    def getPixels(self):
        return self._client.getPixels()

    def setPixel(self, x, y, r, g, b):
        self._client.setPixel(x, y, r, g, b)

    def setPixel(self, x, y, pixel):
        self._client.setPixel(x, y, pixel)

    def getPixel(self, x, y):
        return self._client.getPixel(x, y)

    def showLetter(self, s, textColor = [255, 255, 255], backColor = [0,0,0]):
        self._client.showLetter(s, textColor, backColor)

    def setLowLight(self, flag):
        self._client.setLowLight(flag)

    def getHumidity(self):
        return self._client.getHumidity()

    def getTemperature(self):
        return self._client.get_temperature_from_humidity()

    def getPressure(self):
        return self._client.get_pressure()

    def getOrientation(self):
        return self._client.get_orientation_degrees()

    def getCompass(self):
        return self._client.get_compass()

    def getGyroscope(self):
        return self._client.get_gyroscope()

    def getAccelerometer(self):
        return self._sense.sense.get_accelerometer()

    def captureImage(self, filename):
        image = self._client.captureImage()
        
        imageFile = open(filename, "wb")
        imageFile.write(image)
        imageFile.close()
        
        print("Wrote %s to disk." % filename)
        
        
if __name__ == "__main__":
    
    bot = RaspiBot()
    bot.connect()
    bot.setRotation(90)
    bot.showLetter("F")
    bot.doMotor(9, 200)
    bot.doMotor(10, 200)
    bot.sleep(2)
    bot.doMotor(9, 0)
    bot.doMotor(10, 0)
    bot.captureImage("testing.png")
    bot.disconnect()
    
