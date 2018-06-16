# -*- coding: utf-8 -*-
"""
Python script which handles how the GUI window behaves

    Created By:   D.C. Hartlen, EIT
    Created On:   16-JUN-2018
    Modified By:  
    Modified On:  

Requires: PoltDataGUI.py (contains all Qt objects and layout)

"""

import PlotDataGUI  # This imports py script containing all GUI elements
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import sys
import numpy as np
import time
import serial


class ExampleApp(QtGui.QMainWindow, PlotDataGUI.Ui_MainWindow):
    """Define class which handles all GUI interaction"""
    # Define class specific, shared variables
    firstRunFlag = True
    runningFlag = False
    updateTimer = QtCore.QTimer()
    arduinoInput = serial.Serial('COM9', 9600, timeout=5)
    dataArray = np.zeros(1)
    currentMaxVolts = 0
    stationaryBeforeScroll = 500
    scrollingFlag = False

#------------------------------------------------------------------------------    
    def __init__(self, parent=None):
        """Define Constructor"""
        # Change pyqtgraph to have white backgound
        pg.setConfigOption('background', 'w')
        # Call constructor in GUI script as chile
        super(ExampleApp, self).__init__(parent)

        # Setup the GUI
        self.setupUi(self)

        # Define information about the plot window specifically
        self.mainPlotWindow.plotItem.showGrid(True, True, 0.7)
        # self.mainPlotWindow.setRange(xRange=[0, self.stationaryBeforeScroll])  
        self.mainPlotWindow.setLabels(left = 'Amplitude',bottom = 'Timestep')
        # self.mainPlotWindow.setAutoPan(x=True)
        # self.mainPlotWindow.setLimits(xMin=0,xMax=200,yMin=0,yMax=1.5)

        # Define the voltage curve to be plotted
        self.voltageCurve = self.mainPlotWindow.plot()
        self.voltageCurve.setPen('b',width=2)

        # Define a maximum voltage reached line
        self.maxVoltsLine = pg.InfiniteLine(angle=0)
        self.maxVoltsLine.setPen(color="FFA500", width=2)
        self.mainPlotWindow.addItem(self.maxVoltsLine)

        # Print to status bar
        self.statusbar.showMessage('Ready')

        # Define action  for when start recording is clicked
        self.startPlotting.clicked.connect(self.InitializeRun)

        # Define action for the stop recording button
        self.stopPlotting.clicked.connect(self.StopTicker)

        # Define action for the reset button.
        self.resetPlots.clicked.connect(self.resetUI)

        # Define a timer object to run method Update Ticker every timeout
        self.updateTimer.timeout.connect(self.UpdatePlot)

        # Update the max voltage 
        self.maxVoltsOut.insert("0.00")
        
        # Define an message box to open when about/information in menu bar is selected
        # self.actionInformation.triggered.connect(self.AboutMessage)

#        self.actionExit_App.triggered.connect(QtWidgets.QApplication.quit())


#------------------------------------------------------------------------------
    def InitializeRun(self):
        """Define write data to file"""
        print('DataCollection Class activated') #Print Debug Note
        self.statusbar.showMessage('Executing First Run Tasks')
        # Things to be completed during the first activation    
        if self.firstRunFlag == True:
            print('First Run Activated')    # Debug Notice
            self.statusbar.showMessage('Executing First Run Tasks') # Insitu debug

            # Change the first run flag to false
            self.firstRunFlag = False
            self.runningFlag = True

            # Disable start button
            self.startPlotting.setEnabled(False)
            
            # Start timer for updating the plot
            self.updateTimer.start(5)

            # flush serial inputs so far
            self.arduinoInput.flushInput()
 
        else:
            # Debug message
            print('Not First Run\n')
            return()

        
#------------------------------------------------------------------------------             
    def StopTicker(self):
        """ Stops the ticker plot, closes output file."""
        if self.runningFlag == True:
            self.runningFlag = False
            self.updateTimer.stop()
            self.stopPlotting.setEnabled(False)
            print('STOP STOP STOP STOP\n')
            self.statusbar.showMessage('Plotting Stopped. Waiting Reset')
        else:
            return()

#------------------------------------------------------------------------------             
    def resetUI(self):
        """ Reinitalizes the GUI for the next run """
        if self.runningFlag == False & self.firstRunFlag == False:
            # Enable both buttons
            self.stopPlotting.setEnabled(True)
            self.startPlotting.setEnabled(True)

            # Reset flags
            self.firstRunFlag = True

            # Reset data array and max volt tracker to zero
            self.dataArray = np.zeros(1)
            self.currentMaxVolts = 0

            # Reset dialog box and plot
            self.maxVoltsOut.clear()
            self.maxVoltsOut.insert(str(self.currentMaxVolts))
            self.maxVoltsLine.setValue(self.currentMaxVolts)
            self.voltageCurve.setData(self.dataArray)
            self.statusbar.showMessage("Ready for data")

            self.arduinoInput.flush()
        else:
            self.statusbar("Unable to reset at this time")
            return()
        
#------------------------------------------------------------------------------
    def UpdatePlot(self):
        """Updates ticker plot with data from serial port"""
        if self.runningFlag == True:
            # Read from serial port. This is encoded in bytes
            dataIn = self.arduinoInput.readline()
            # Decode the byte
            dataIn = float(dataIn[0:len(dataIn)-2].decode("utf-8"))
            # append new data to existing data array
            self.dataArray = np.append(self.dataArray,dataIn)
            # Update the data in the curve related to motor voltage
            self.voltageCurve.setData(self.dataArray)
            # Print the current input to the status bar
            self.statusbar.showMessage(str(dataIn))

            # if new voltage is large than maximum voltage, replace max
            if dataIn > self.currentMaxVolts:
                self.currentMaxVolts = dataIn
                self.maxVoltsOut.clear()
                self.maxVoltsOut.insert(str(self.currentMaxVolts))
                self.maxVoltsLine.setValue(self.currentMaxVolts)
                    
        else:
            print('Not Recording\n')        
        
#------------------------------------------------------------------------------         
    def AboutMessage(self):
        """ Method to create message box which displays "about" information"""
        self.statusbar.showMessage('About Information selected')
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText('Curlsmart Data Aquistion System\n'\
                       'Developed by D. Hartlen\n'\
                       'All rights reserved')
        msgbox.exec()
        
        
#------------------------------------------------------------------------------ 
# This conditional executes the loop
if __name__=="__main__":
    # Define that the app will draw from pyqt4
    app = QtGui.QApplication(sys.argv)
    # Set style of app to 'CleanLooks'
    style = app.setStyle('CleanLooks')
    # Set the layout and behavour of the app by linking it to class generated above
    form = ExampleApp()
    # Start the app
    form.show()
    form.update() #start with something
    sys.exit(app.exec_())
    # Print debug on exit
    print("DONE")