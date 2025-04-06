# Python script for a Windows USB blocker
# This script blocks USB storage devices from being used on a Windows machine.

import sys as machine # Importing the sys module for system-specific parameters and functions
import os as windows # Importing the os module for operating system dependent functionality
import time # Importing the time module for time-related functions
import argparse # Importing the argparse module for parsing command-line arguments
import threading # Importing the threading module for creating threads
from PyQt5 import QtWidgets, QtGui, QtCore # Importing PyQt5 modules for GUI development
import wmi # Importing the wmi module for Windows Management Instrumentation

# =================================================================================================
# Splash Screen
# This widget displays a full-screen splash with a 10 second countdown timer.
# The splash screen is shown before the main application starts.
# =================================================================================================

class SplashScreen(QtWidgets.QWidget):
    def __init__(self, countdown=10):
        super().__init__()
        self.countdown = countdown
        self.initUI()
        
    def initUI(self):
        # Frameless window and always on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setGeometry(300, 300, 400, 200) # Set the size of the splash screen
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter) # Center the label
       # The line `self.setStyleSheet("background-color: #003366; color: #FFCC00; font-size: 24px;")`
       # in the `SplashScreen` class is setting the style sheet properties for the widget.
        self.setStyleSheet("background-color: #003366; color: #FFCC00; font-size: 24px;")
        self.label.setGeometry(0, 0, 400, 200) # Set the size of the label
        self.label.setText(f"USB Blocker\n\nStarting in {self.countdown} seconds...") # Set the text of the label
        self.timer. = QtCore.QTimer(self) # Create a timer
        self.timer.timeout.connect(self.updateCountdown) # Connect the timeout signal to the updateCountdown method
        self.timer.start(1000)
    
    def updateCountdown(self):
        if self.countdown > 0:
            self.countdown -= 1
            self.label.setText(f"USB Blocker\n\nStarting in {self.countdown} seconds...")
        else:
            self.timer.stop()
            self.close()

class LockScreen(QtWidgets.QtWidget):
    def __init__(self,override_code):
        super().__init__()
        self.override_code = override_code
        self.initUI()

    def initUI(self):
        # Create a full screen borderless window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        
        # Set the background color and text color
        self.setStyleSheet("background-color: white;") 
        
        #Display the lock screen message
        self.label = QtWidgets.QLabel(self)
        self.label.setText("USB Inserted\n\nEnter Override Code To Unlock")
        self.label.setAlignment(QtCore.Qt.AlignCenter) # Center the label
        self.label.setStyleSheet("color: red; font-size: 100px;")
        self.label.setGeometry(0, 200, self.width(), 100) # Set the size of the label
        self.label.setWordWrap(True) # Allow the label to wrap text
        
        # Create a text input field for the override code
        self.input_field = QtWidgets.QLineEdit(self)
        self.input_field.setEchoMode(QtWidgets.QLineEdit.Password) # Set the input field to password mode
        self.input_field.setPlaceholderText("") # Set the placeholder text
        self.input_field.setGeometry(self.width() // 2 - 100, 350, 200, 40) # Set the size of the input field
        self.input_field.setAlignment(QtCore.Qt.AlignCenter) # Center the input field
        self.input_field.setStyleSheet("font-size: 20px;")
        self.input_field.returnPressed.connect(self.checkOverrideCode) # Connect the returnPressed signal to the checkOverrideCode method
        self.input_field.setFocus() # Set focus to the input field
        
        # # Create a button to submit the override code
        # self.submit_button = QtWidgets.QPushButton("Unlock", self)
        # self.submit_button.setGeometry(self.width() // 2 - 50, 400, 100, 40)
        # self.submit_button.setStyleSheet("font-size: 20px;")
        # self.submit_button.clicked.connect(self.checkOverrideCode)
        # self.submit_button.setFocusPolicy(QtCore.Qt.NoFocus) # Set focus policy to prevent focus on the button
        # self.submit_button.setAutoDefault(False) # Disable auto default for the button
        # self.submit_button.setDefault(False) # Disable default for the button
        # self.submit_button.setEnabled(True) # Enable the button
        # self.submit_button.setAutoRepeat(False) # Disable auto repeat for the button
        # self.submit_button.setAutoDefault(False)
    
    # Check the override code entered by the user
    
        
        
    
        
        
        