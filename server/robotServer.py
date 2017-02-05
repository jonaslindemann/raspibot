import zerorpc
import serial, time

from lib.mOrion import *
from sense_hat import SenseHat

class RaspiRobot(object):
	def __init__(self):
		self._controller = self.createAndSyncRobot()
		self._sense = SenseHat()	

	def doMotor(self, port, speed):
		self._controller.doMotor(port, speed)

	def showMessage(self, message):
		self._sense.show_message(message)

	def clear(self, r, g, b):
		self._sense.clear([r, g, b])

	def setRotation(self, angle):
		self._sense.set_rotation(angle)

	def flipVert(self):
		self._sense.flip_v()

	def flipHoriz(self):
		self._sense.flip_h()

	def setPixels(self, pixels):
		self._sense.set_pixels(pixels)

	def getPixels(self):
		return self._sense.get_pixels()

	def setPixel(self, x, y, r, g, b):
		self._sense.set_pixel(x, y, r, g, b)

	def setPixel(self, x, y, pixel):
		self._sense.set_pixel(x, y, pixel)

	def getPixel(self, x, y):
		return self._sense.get_pixel(x, y)

	def showLetter(self, s, textColor = [255, 255, 255], backColor = [0,0,0]):
		self._sense.show_letter(s, textColor, backColor)

	def setLowLight(self, flag):
		self._sense.low_light = flag

	def getHumidity(self):
		return self._sense.get_humidity()

	def getTemperature(self):
		return self._sense.get_temperature()

	def createAndSyncRobot(self):
		bot = mBot()
		bot.startWithSerial("/dev/ttyUSB0")
		#bot.startWithHID()

		print("Syncing with Orion board...")

		for i in range(5):
			bot.doMotor(9,0)
			bot.doMotor(10,0)

		sleep(3)
		print("Completed...")

		return bot

if __name__ == "__main__":
    	
    	print("Creating robot controller class...")
	robot = RaspiRobot()
	
	print("Start ZeroRPC server...")
	s = zerorpc.Server(robot)
	s.bind("tcp://0.0.0.0:4242")
	s.run()    