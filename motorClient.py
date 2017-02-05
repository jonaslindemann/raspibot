
import zerorpc, time

if __name__ == "__main__":

	print("Creating client...")
	robot = zerorpc.Client()

	print("Connecting...")
	robot.connect("tcp://raspi3.home.local:4242")

	try:	
		while(1):
			print("Forward")
			robot.setRotation(90)
			robot.showLetter("F")
			robot.doMotor(9,200);
			robot.doMotor(10,200);
			time.sleep(2)
			print("Backward")
			robot.showLetter("B")
			robot.doMotor(9,-200);
			robot.doMotor(10,-200);
			time.sleep(2)
			print("Stop")
			robot.showLetter("S")
			robot.doMotor(9,0);
			robot.doMotor(10,0);
			time.sleep(2)
			
	finally:
		print("Close robot")
		robot.clear(0,0,0)
		robot.close()
