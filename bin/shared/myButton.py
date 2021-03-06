# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 11:59:14 2021

@author: andre
"""

import RPi.GPIO as GPIO
import time
import threading

ACTION_TYPE_KEY_PRESSED = 1
ACTION_TYPE_KEY_RELEASED = 2
ACTION_TYPE_KEY_HOLD = 3
ACTION_TYPE_KEY_HOLD_SINGLE = 4

class myButton:
    
    def __init__(self, gpioPin, bounceTime):
        self.gpioPin = gpioPin

        self.keyPressedActions = []
        self.keyReleasedActions = []
        self.keyHoldActions = []
        self.keyHoldActionsSingle = []
        
        self.bounceTime = bounceTime
        #self.__buttonThread = threading.Thread(target = self.buttonThread, args = (lambda : self.isButtonReleased, self.actionList)) 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpioPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        
        
        self.buttonPressTimeForRelease = 0
        self.lastButtonPressTime = time.time()
        
        self.hasRegisteredEvent = False
        self.buttonIsPressed = False
        self.timerActive = False
        
        self.timerThread = 0
    def __del__(self):
        GPIO.cleanup()
        
        
    def buttonThread(self, isButtonReleased, actionList):
        startTime = time.time()
        
        actionPressed = False
        while(True):
            if isButtonReleased():
                break
            
            buttonTime = round((time.time()- startTime) * 1000)
            
            if not actionPressed:
                if (buttonTime >= actionList["MinTime"]):
                    actionList["Callback"]()
                    actionPressed = True
                    
            
            time.sleep(0.01)
            
            
        
    def buttonAction(self, channel):
        time.sleep(0.001)
        if (GPIO.input(channel) == 0):
            self.buttonPressed()
        else:
            self.buttonReleased()
        
        
    def buttonHold(self):
        
        #Check if button is still pressed
        if (GPIO.input(self.gpioPin) == 0):
            self.keyHoldActions[1]()
            self.timerThread = threading.Timer(self.keyHoldActions[0] / 1000, self.buttonHold)
            self.timerThread.start()
            
    def buttonHoldSingle(self):
        
        #Check if button is still pressed
        if (GPIO.input(self.gpioPin) == 0):
            self.keyHoldActionsSingle[1]()
            
                
    def buttonPressed(self):
        if (not self.buttonIsPressed):
            self.buttonIsPressed = True
            pressTime = (time.time() - self.lastButtonPressTime) * 1000
            
            
            # Start a thread with the min duration to check if a button was hold for the period of time.
            if len(self.keyHoldActions):
                self.timerThread = threading.Timer(self.keyHoldActions[0] / 1000, self.buttonHold)
                self.timerThread.start()
                self.timerActive = True
                
            # Start a thread with the min duration to check if a button was hold for the period of time.
            if len(self.keyHoldActionsSingle):
                self.timerThread = threading.Timer(self.keyHoldActionsSingle[0] / 1000, self.buttonHoldSingle)
                self.timerThread.start()
                self.timerActive = True
            
            
            if len(self.keyPressedActions):
                if (pressTime) > self.keyPressedActions[0]:
                    self.lastButtonPressTime = time.time()
                    self.keyPressedActions[1]()
                    
                    
            if (self.buttonPressTimeForRelease == 0):
                self.buttonPressTimeForRelease = time.time()
                
    
    def buttonReleased(self):
        self.buttonIsPressed = False
        releaseTime = (time.time() - self.buttonPressTimeForRelease) * 1000
        if len(self.keyReleasedActions):
            if (releaseTime) > self.keyReleasedActions[0]:
                self.keyReleasedActions[1]()
        if self.timerActive:
            self.timerActive = False
            self.timerThread.cancel()
        self.buttonPressTimeForRelease = 0

        
    
    
    def addButtonAction(self, actionType, callbackFunction, time):
                
        if (not self.hasRegisteredEvent):
            GPIO.add_event_detect(self.gpioPin, GPIO.BOTH, callback=self.buttonAction , bouncetime = self.bounceTime)
            self.hasRegisteredEvent = True
            
        if (actionType == ACTION_TYPE_KEY_PRESSED):
            self.keyPressedActions = [time, callbackFunction]
        elif (actionType == ACTION_TYPE_KEY_RELEASED):
            self.keyReleasedActions = [time, callbackFunction]
        elif (actionType == ACTION_TYPE_KEY_HOLD):
            self.keyHoldActions = [time, callbackFunction]
        elif (actionType == ACTION_TYPE_KEY_HOLD_SINGLE):
            self.keyHoldActionsSingle = [time, callbackFunction]
            


    
    