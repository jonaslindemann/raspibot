import sys
import zerorpc, time

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from math import *

from joystick import *

class JoystickThread(QThread):
    update = pyqtSignal()
    def __init__(self, parent, joystick):
        super(JoystickThread, self).__init__(parent)
        self.joystick = joystick

    def run(self):
        while True:
            self.joystick.poll()
            self.update.emit()
            time.sleep(0.2)

    def stop(self):
        self.terminate()

class SensorThread(QThread):
    update = pyqtSignal()

    def __init__(self, parent):
        super(SensorThread, self).__init__(parent)
        self.parent = parent

    def run(self):
        sensors = zerorpc.Client()
        sensors.connect("tcp://raspi3.home.local:4242")
        
        while True:
            self.parent.temperature = sensors.getTemperature()
            self.parent.humidity = sensors.getHumidity()
            self.parent.pressure = sensors.getPressure()
            self.parent.orientation = sensors.getOrientation()
            self.update.emit()
            self.msleep(500)

    def stop(self):
        self.terminate()


class RemoteControlWindow(QWidget):
    def __init__(self, *args):
        """Constructor"""
        super(RemoteControlWindow, self).__init__(*args)

        # Defined speed limits

        self.forwardSpeed = 500
        self.backwardSpeed = 500
        self.rotateSpeed = 300

        self.moving = False

        self.temperature = 0.0
        self.humidity = 0.0
        self.orientation = None

        self.sensorThread = None

        self.hasJoystick = False
        self.x = 0
        self.y = 0

        # Initialise xinput joystick
        
        # Initalise joystick object

        i = 0
        self.joystick = Joystick(i)
        while not self.joystick.connected:
            i = i + 1
            self.joystick = Joystick(i)
            if i > 4:
                break

        if self.joystick.connected:
            self.joystickThread = JoystickThread(self, self.joystick)
            self.joystickThread.setTerminationEnabled(True)
            self.joystickThread.update.connect(self.on_joystickUpdate)
       
        # Load user interface from UI-file

        loadUi('remote_control.ui', self)

        # Initially disable controls        

        self.disable_controls()

    def disable_controls(self):
        """Disable all controls"""
        self.backButton.setEnabled(False)
        self.forwardButton.setEnabled(False)
        self.turnLeftButton.setEnabled(False)
        self.turnRightButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.testButton.setEnabled(False)
        self.connectButton.setEnabled(True)

    def enable_controls(self):
        """Enable all controls"""
        self.backButton.setEnabled(True)
        self.forwardButton.setEnabled(True)
        self.turnLeftButton.setEnabled(True)
        self.turnRightButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.disconnectButton.setEnabled(True)
        self.testButton.setEnabled(True)
        self.connectButton.setEnabled(False)
        
    def on_joystickUpdate(self):
        """Handle joystick updates"""
        
        x = self.joystick.x
        y = self.joystick.y
        lt = self.joystick.lt
        rx = self.joystick.rx
        ry = self.joystick.ry
        rt = self.joystick.rt
        buttons_list = self.joystick.buttons_text.split()
        # print("\r(% .3f % .3f % .3f) (% .3f % .3f % .3f)%s%s" % (x, y, lt, rx, ry, rt, buttons_list, "                                "))
        # print(buttons_text.split())
        if len(buttons_list) > 0:
            if buttons_list[0] == "a":
                self.robot.clear(255, 255, 255)
        else:
            self.robot.clear(0, 0, 0)

        self.temperature = self.robot.getTemperature()
        self.humidity = self.robot.getHumidity()
        

        d = sqrt(pow(x, 2) + pow(y, 2))

        if d > 0.1:
            self.robot.doMotor(9, -self.forwardSpeed * (y + x));
            self.robot.doMotor(10, -self.forwardSpeed * (y - x));
            self.moving = True
        else:
            if self.moving:
                self.robot.doMotor(9, 0);
                self.robot.doMotor(10, 0);
                self.moving = False  
                
    def on_sensor_update(self):
        self.pitchDial.setValue(self.orientation[b"pitch"])
        self.rollDial.setValue(self.orientation[b"roll"])
        self.yawDial.setValue(self.orientation[b"yaw"])
        self.temperatureSlider.setValue(self.temperature)
        self.humiditySlider.setValue(self.humidity)
        self.pressureSlider.setValue(self.pressure)

    @pyqtSlot()
    def on_connectButton_clicked(self):
        print("Creating client...")
        self.robot = zerorpc.Client()

        print("Connecting...")
        self.robot.connect("tcp://raspi3.home.local:4242")

        if self.joystick.connected:
            print("Starting joystick thread...")
            self.joystickThread.start()

        print("Starting sensor thread...")
        self.sensorThread = SensorThread(self)
        self.sensorThread.setTerminationEnabled(True)
        self.sensorThread.update.connect(self.on_sensor_update)
        self.sensorThread.start()

        self.enable_controls()

    @pyqtSlot()
    def on_disconnectButton_clicked(self):
        print("Close robot")
        self.robot.clear(0, 0, 0)
        self.timer.stop()
        # if self.hasJoystick:
        #    print("Stopping joystick thread")
        #    self.joystickThread.stop()
        print("Stopping sensor thread")
        self.sensorThread.stop()
        self.robot.close()

        self.disable_controls()

    @pyqtSlot()
    def on_testButton_clicked(self):
        print("Capturing image start...")
        image = self.robot.captureImage()

        pixmap = QPixmap()
        pixmap.loadFromData(image)

        self.previewImageLabel.setPixmap(pixmap)
        
        # imageFile = open("image.png", "wb")
        # imageFile.write(image)
        # imageFile.close()
        print("Capture complete.")

    @pyqtSlot()
    def on_forwardButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("F")
        self.robot.doMotor(9, self.forwardSpeed);
        self.robot.doMotor(10, self.forwardSpeed);

    @pyqtSlot()
    def on_forwardButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0, 0, 0)
        self.robot.doMotor(9, 0);
        self.robot.doMotor(10, 0);

    @pyqtSlot()
    def on_backButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("B")
        self.robot.doMotor(9, -self.backwardSpeed);
        self.robot.doMotor(10, -self.backwardSpeed);

    @pyqtSlot()
    def on_backButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0, 0, 0)
        self.robot.doMotor(9, 0);
        self.robot.doMotor(10, 0);

    @pyqtSlot()
    def on_turnLeftButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("L")
        self.robot.doMotor(9, self.rotateSpeed);
        self.robot.doMotor(10, -self.rotateSpeed);

    @pyqtSlot()
    def on_turnLeftButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0, 0, 0)
        self.robot.doMotor(9, 0);
        self.robot.doMotor(10, 0);

    @pyqtSlot()
    def on_turnRightButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("R")
        self.robot.doMotor(9, -self.rotateSpeed);
        self.robot.doMotor(10, self.rotateSpeed);

    @pyqtSlot()
    def on_turnRightButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0, 0, 0)
        self.robot.doMotor(9, 0);
        self.robot.doMotor(10, 0);

    @pyqtSlot()
    def on_stopButton_clicked(self):
        self.robot.doMotor(9, 0);
        self.robot.doMotor(10, 0);


app = QApplication(sys.argv)
widget = RemoteControlWindow()
widget.show()
sys.exit(app.exec_())
