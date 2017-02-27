#!/usr/bin/env python

from raspibot import *
from raspicontrol import *

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
    
    remoteControl(bot)
    
    bot.disconnect()
    
