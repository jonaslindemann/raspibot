import sys
import zerorpc, time

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.uic import loadUi


class RemoteControlWindow(QWidget):
    def __init__(self, *args):
        super(RemoteControlWindow, self).__init__(*args)
        self.forwardSpeed = 150
        self.backwardSpeed = 150
        self.rotateSpeed = 150

        loadUi('remote_control.ui', self)

    @pyqtSlot()
    def on_connectButton_clicked(self):
        print("Creating client...")
        self.robot = zerorpc.Client()

        print("Connecting...")
        self.robot.connect("tcp://raspi3.home.local:4242")

    @pyqtSlot()
    def on_disconnectButton_clicked(self):
        print("Close robot")
        self.robot.clear(0,0,0)
        self.robot.close()

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