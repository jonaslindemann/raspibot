import zerorpc
import serial, time

from lib.mOrion import *
from sense_hat import SenseHat
from picamera import PiCamera
from io import BytesIO

from robotBroadCast import *
from multiprocessing import Process

def broadCaster(iface):
    broadcast = RaspiBotBroadCaster("wlan0")
    broadcast.connect()

    while True:
        broadcast.broadCast()
        time.sleep(4)
    
class RaspiRobot(object):
	def __init__(self):
	        print("Initialising interface to Orion board...")
		self._controller = self.createAndSyncRobot()
		
		print("Initialising SenseHat...")
		self._sense = SenseHat()
		self._sense.set_imu_config(True, True, True)
		
		print("Starting BroadCaster...")
		self.broadCastProcess = Process(target = broadCaster, args = ("wlan0",))
		self.broadCastProcess.start()
		
	def doMotor(self, port, speed):
	        print(port, speed)
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
		return self._sense.get_temperature_from_humidity()

	def getPressure(self):
		return self._sense.get_pressure()

	def getOrientation(self):
		return self._sense.get_orientation_degrees()

	def getCompass(self):
		return self._sense.get_compass()

	def getGyroscope(self):
		return self._sense.get_gyroscope()

	def getAccelerometer(self):
		return self._sense.sense.get_accelerometer()

        def captureImage(self):

            print("Capture image")

            camera = None
            captureOk = True
            
            try:
                image = BytesIO()
                camera = PiCamera()
                camera.resolution = (1280,1024)
                camera.iso = 800
                camera.capture(image, 'png')
            except Exception as e:
                print("Capture image failed...")
                print(e)
                captureOk = False
            finally:
                if camera!=None:
                    camera.close()

            if captureOk:
                print("Returning image...")
                return image.getvalue()
            else:
                return b'0'

	def createAndSyncRobot(self):
		bot = mBot()
		#bot.startWithSerial("/dev/ttyACM0")
		bot.startWithSerial("/dev/ttyUSB0")
		#bot.startWithHID()

		for i in range(5):
			bot.doMotor(9,0)
			bot.doMotor(10,0)

		sleep(3)

		return bot

if __name__ == "__main__":
    	
    	print("RaspiBot Server 1.0 starting...")
	robot = RaspiRobot()
	
	print("Starting ZeroRPC server...")
	s = zerorpc.Server(robot)
	s.bind("tcp://0.0.0.0:4242")
	s.run()    
