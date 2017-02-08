import sys
import zerorpc, time

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.uic import loadUi
from math import *

from joystick import Joystick

class JoystickThread(QThread):
    update = pyqtSignal()
    def __init__(self, parent, joystick):
        super(JoystickThread, self).__init__(parent)
        self.joystick = joystick

    def run(self):
        while True:
            self.joystick.poll()
            self.update.emit()
            time.sleep(0.1)

    def stop(self):
        self.terminate()

class RemoteControlWindow(QWidget):
    def __init__(self, *args):
        """Constructor"""
        super(RemoteControlWindow, self).__init__(*args)

        # Defined speed limits
        
        self.forwardSpeed = 200
        self.backwardSpeed = 200
        self.rotateSpeed = 150

        # Initalise joystick object

        i = 0
        self.joystick = Joystick(i)
        while not self.joystick.connected:
            i = i + 1
            self.joystick = Joystick(i)
            if i>4:
                break

        if self.joystick.connected:
            self.joystickThread = JoystickThread(self, self.joystick)
            self.joystickThread.setTerminationEnabled(True)
            self.joystickThread.update.connect(self.on_joystickUpdate)

        # Load user interface from UI-file

        loadUi('remote_control.ui', self)

        # Initially disable controls

        self.disableControls()

    def disableControls(self):
        """Disable all controls"""
        self.backButton.setEnabled(False)
        self.forwardButton.setEnabled(False)
        self.turnLeftButton.setEnabled(False)
        self.turnRightButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.disconnectButton.setEnabled(False)
        self.testButton.setEnabled(False)
        self.connectButton.setEnabled(True)
        
    def enableControls(self):
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
        buttons_text = self.joystick.buttons_text
        #print("\r(% .3f % .3f % .3f) (% .3f % .3f % .3f)%s%s" % (x, y, lt, rx, ry, rt, buttons_text, "                                "))

        d = sqrt(pow(x,2)+pow(y,2))

        if d>0.1:
            self.robot.doMotor(9,-self.forwardSpeed*(y+x));
            self.robot.doMotor(10,-self.forwardSpeed*(y-x));
        else:
            self.robot.doMotor(9,0);
            self.robot.doMotor(10,0);

    @pyqtSlot()
    def on_connectButton_clicked(self):
        print("Creating client...")
        self.robot = zerorpc.Client()

        print("Connecting...")
        self.robot.connect("tcp://raspi3.home.local:4242")

        if self.joystick.connected:
            print("Starting joystick thread...")
            self.joystickThread.start()

        self.enableControls()

    @pyqtSlot()
    def on_disconnectButton_clicked(self):
        print("Close robot")
        self.robot.clear(0,0,0)
        self.robot.close()

        print("Stopping joystick thread")
        self.joystickThread.stop()
        self.disableControls()
        
    @pyqtSlot()
    def on_testButton_clicked(self):
        self.robot.showLetter("T")
        time.sleep(2)
        self.robot.clear(0,0,0)

    @pyqtSlot()
    def on_forwardButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("F")
        self.robot.doMotor(9,self.forwardSpeed);
        self.robot.doMotor(10,self.forwardSpeed);

    @pyqtSlot()
    def on_forwardButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0,0,0)
        self.robot.doMotor(9,0);
        self.robot.doMotor(10,0);

    @pyqtSlot()
    def on_backButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("B")
        self.robot.doMotor(9,-self.backwardSpeed);
        self.robot.doMotor(10,-self.backwardSpeed);

    @pyqtSlot()
    def on_backButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0,0,0)
        self.robot.doMotor(9,0);
        self.robot.doMotor(10,0);

    @pyqtSlot()
    def on_turnLeftButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("L")
        self.robot.doMotor(9, self.rotateSpeed);
        self.robot.doMotor(10,-self.rotateSpeed);

    @pyqtSlot()
    def on_turnLeftButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0,0,0)
        self.robot.doMotor(9,0);
        self.robot.doMotor(10,0);

    @pyqtSlot()
    def on_turnRightButton_pressed(self):
        self.robot.setRotation(90)
        self.robot.showLetter("R")
        self.robot.doMotor(9, -self.rotateSpeed);
        self.robot.doMotor(10,self.rotateSpeed);

    @pyqtSlot()
    def on_turnRightButton_released(self):
        self.robot.setRotation(90)
        self.robot.clear(0,0,0)
        self.robot.doMotor(9,0);
        self.robot.doMotor(10,0);

    @pyqtSlot()
    def on_stopButton_clicked(self):
        self.robot.doMotor(9,0);
        self.robot.doMotor(10,0);

    @pyqtSlot(int)
    def on_maxForwardSpeedDial_valueChanged(self, value):
        self.forwardSpeed = value

    @pyqtSlot(int)
    def on_maxBackwardSpeedDial_valueChanged(self, value):
        self.backwardSpeed = value

    @pyqtSlot(int)
    def on_maxRotationSpeedDial_valueChanged(self, value):
        self.rotateSpeed = value
    

app = QApplication(sys.argv)
widget = RemoteControlWindow()
widget.show()
sys.exit(app.exec_())