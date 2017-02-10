import sys
import zerorpc, time

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.uic import loadUi
from math import *

from joystick import Joystick


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
            self.parent.orientation = sensors.getOrientation()
            self.update.emit()
            self.msleep(500)

    def stop(self):
        self.terminate()


class JoystickThread(QThread):
    update = pyqtSignal()

    def __init__(self, parent, joystick):
        super(JoystickThread, self).__init__(parent)
        self.joystick = joystick

    def run(self):
        while True:
            self.joystick.poll()
            self.msleep(100)
            self.update.emit()

    def stop(self):
        self.terminate()


class RemoteControlWindow(QWidget):
    def __init__(self, *args):
        """Constructor"""
        super(RemoteControlWindow, self).__init__(*args)

        # Defined speed limits

        self.forwardSpeed = 250
        self.backwardSpeed = 250
        self.rotateSpeed = 150

        self.moving = False

        self.temperature = 0.0
        self.humidity = 0.0
        self.orientation = None

        self.sensorThread = None

        # Initalise joystick object

        i = 0
        self.joystick = Joystick(0)
        while not self.joystick.connected:
            i = i + 1
            self.joystick = Joystick(i)
            if i > 4:
                break

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

    def on_joystick_update(self):
        """Handle joystick updates"""

        x = self.joystick.x
        y = self.joystick.y
        lt = self.joystick.lt
        rx = self.joystick.rx
        ry = self.joystick.ry
        rt = self.joystick.rt
        buttons_list = self.joystick.buttons_text.split()
        # print("\r(% .3f % .3f % .3f) (% .3f % .3f % .3f)%s%s" % (x, y, lt, rx, ry, rt, self.joystick.buttons_text, "                                "))
        # print(buttons_text.split())
        if len(buttons_list) > 0:
            if buttons_list[0] == "a":
                self.robot.clear(255, 255, 255)
            if buttons_list[0] == "b":
                self.robot.clear(0,0,0)
        #    self.robot.clear(0, 0, 0)

        # print("T=%g C, Humidity=%g" % (self.temperature, self.humidity))
        # print(self.orientation)

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
        print("sensor update")
        self.pitchDial.setValue(self.orientation[b"pitch"])
        self.rollDial.setValue(self.orientation[b"roll"])
        self.yawDial.setValue(self.orientation[b"yaw"])

    @pyqtSlot()
    def on_connectButton_clicked(self):
        print("Creating client...")
        self.robot = zerorpc.Client()

        print("Connecting...")
        self.robot.connect("tcp://raspi3.home.local:4242")

        if self.joystick.connected:
            self.joystickThread = JoystickThread(self, self.joystick)
            self.joystickThread.setTerminationEnabled(True)
            self.joystickThread.update.connect(self.on_joystick_update)        

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
        print("Stopping joystick thread")
        self.joystickThread.stop()
        print("Stopping sensor thread")
        self.sensorThread.stop()
        self.robot.close()

        self.disable_controls()

    @pyqtSlot()
    def on_testButton_clicked(self):
        self.robot.showLetter("T")
        time.sleep(2)
        self.robot.clear(0, 0, 0)

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
