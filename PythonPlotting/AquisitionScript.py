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
import serial.tools.list_ports


class PlottingApp(QtGui.QMainWindow, PlotDataGUI.Ui_MainWindow):
    """Define class which handles all GUI interaction"""
    # Define class specific, shared variables
    firstRunFlag = True
    runningFlag = False
    updateTimer = QtCore.QTimer()

    dataArray = np.zeros(1)
    currentMaxVolts = 0
    stationaryBeforeScroll = 500
    scrollingFlag = False
    iTicker = 0

    # Look for open COM ports
    availablePorts = serial.tools.list_ports.comports()
    nPorts = len(availablePorts)
    arduinoPort = availablePorts[-1].device

    

#------------------------------------------------------------------------------    
    def __init__(self, parent=None):
        """Define Constructor"""
        # Change pyqtgraph to have white backgound
        pg.setConfigOption('background', 'w')
        # Call constructor in GUI script as chile
        super(PlottingApp, self).__init__(parent)

        # Setup the GUI
        self.setupUi(self)

        # Define information about the plot window specifically
        self.mainPlotWindow.plotItem.showGrid(True, True, 0.7)
        self.mainPlotWindow.setRange(xRange=[0, self.stationaryBeforeScroll], yRange=[0,1.5])  
        self.mainPlotWindow.setLabels(left = 'Voltage (V)',bottom = 'Time')
        self.mainPlotWindow.setAutoPan(x=True)
        self.mainPlotWindow.setAutoVisible(x=True,y=True)
        # self.mainPlotWindow.setLimits(xMin=0,xMax=200,yMin=0,yMax=1.5)

        # Define a maximum voltage reached line
        self.maxVoltsLine = pg.InfiniteLine(angle=0)
        self.maxVoltsLine.setPen(color="FFA500", width=2)
        self.mainPlotWindow.addItem(self.maxVoltsLine)

        # Define the voltage curve to be plotted
        self.voltageCurve = self.mainPlotWindow.plot()
        self.voltageCurve.setPen('b',width=2)

        # Print to status bar
        self.statusbar.showMessage('Ready to go!')

        # Define action  for when start recording is clicked
        self.startPlotting.clicked.connect(self.InitializeRun)

        # Define action for the stop recording button
        self.stopPlotting.clicked.connect(self.StopTicker)

        # Define action for the reset button.
        self.resetPlots.clicked.connect(self.resetUI)

        # Define a timer object to run method Update Ticker every timeout
        self.updateTimer.timeout.connect(self.UpdatePlot)

        # Update the max voltage 
        self.maxVoltsOut.insert("%0.3f" % self.currentMaxVolts)
        
        # Define an message box to open when about/information in menu bar is selected
        self.actionAbout.triggered.connect(self.AboutMessage)

        # Define a message box for help
        self.actionHelp.triggered.connect(self.HelpMessages)

        # Define a dialog box to select the appropriate COM Port
        self.actionSelectCOMPort.triggered.connect(self.dialogSelectPort)

#        self.actionExit_App.triggered.connect(QtWidgets.QApplication.quit())


#------------------------------------------------------------------------------
    def InitializeRun(self):
        """Define write data to file"""
        # Things to be completed during the first activation    
        if self.firstRunFlag == True:
            # Check the comport for functional arduino
            self.statusbar.showMessage("Checking COM port for arduino...")
            # Connect to com port specified by user. Reads one peice of data to make sure
            # it works. If not, will return error message without stopping program.
            try:
                self.arduinoInput = serial.Serial(self.arduinoPort, 9600, timeout=5)
                # Read from serial port. This is encoded in bytes
                dataIn = self.arduinoInput.readline()
                # Decode the byte
                dataIn = float(dataIn[0:len(dataIn)-2].decode("utf-8"))
            except:
                # If there is an exception, return without starting collection
                self.statusbar.showMessage("Connection Failed. Check Port and Arduino.")
                return()
            
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
            return()

        
#------------------------------------------------------------------------------             
    def StopTicker(self):
        """ Stops the ticker plot, closes output file."""
        if self.runningFlag == True:
            self.runningFlag = False
            self.updateTimer.stop()
            self.stopPlotting.setEnabled(False)

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
            self.maxVoltsOut.insert("%0.3f" % self.currentMaxVolts)
            self.maxVoltsLine.setValue(self.currentMaxVolts)
            self.voltageCurve.setData(self.dataArray)
            self.statusbar.showMessage("Ready for go!")

            self.arduinoInput.close()
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

            # If the number of data points is less than the size of the screen,
            # accumulate data
            if self.iTicker < self.stationaryBeforeScroll:
                # append new data to existing data array
                self.dataArray = np.append(self.dataArray,dataIn)

                self.iTicker += 1
            # Start scrolling data otherwise.
            else:
                # slice data array such that all data is rolled back one index
                self.dataArray[:-1] = self.dataArray[1:]
                # Overwrite last value in array
                self.dataArray[-1] = dataIn

            # Print the current input to the status bar
            self.statusbar.showMessage("Running: V = %0.3f V" % dataIn)
            # Update the data in the curve related to motor voltage
            self.voltageCurve.setData(self.dataArray)

            # if new voltage is large than maximum voltage, replace max
            if dataIn > self.currentMaxVolts:
                self.currentMaxVolts = dataIn
                self.maxVoltsOut.clear()
                self.maxVoltsOut.insert("%0.3f" % self.currentMaxVolts)
                self.maxVoltsLine.setValue(self.currentMaxVolts)
                    
        else:
            self.statusbar.showMessage('Not Recording')        
        
#------------------------------------------------------------------------------         
    def AboutMessage(self):
        """ Method to create message box which displays "about" information"""
        self.statusbar.showMessage('About Information selected')
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle('About')
        msgbox.setText('Wind Energy Demonstration\n'\
                       'Data Collection and Plotting\n'\
                       'Developed by D.C. Hartlen, 2018\n'\
                       'Distributed under MIT License\n\n'\
                       'Qt used in GUI development.\n'\
                       'Qt distrubited under GNU LPGL')
        msgbox.exec()

#------------------------------------------------------------------------------         
    def HelpMessages(self):
        """ Method to create message box which provides instructions"""
        self.statusbar.showMessage('Help selected')
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle('Help')
        msgbox.setText('Operation:\n'\
                       '1) System attempts to select available COM Port as this is\n'\
                       '   typically where the arduino is located. To manually\n'\
                       '   specify the COM port, go to file and select select \n'\
                       '   "Select COM Port". Choose the appropriate port and OK.\n'\
                       '2) Press Start to start collecting and and plotting data.\n'\
                       '3) press Stop to stop plotting. Does not reset plotted data.\n'\
                       '4) Press Reset to clear plotted dataand prepare for next run.')
        msgbox.exec()
#------------------------------------------------------------------------------         
    def dialogSelectPort(self):
        """ Method creates a dialog box for the selection of avaiable com ports"""
        #Initalize an empty list of comports
        items = [None] * self.nPorts
        # Populate list
        for i in range(self.nPorts):
            items[i] = self.availablePorts[i].device
        # Create a dialog instance
        selectedPort, okPressed = QtWidgets.QInputDialog.getItem(self,
                                               "Select COM Port", 
                                               "Select COM Port:",
                                               items,
                                               0,
                                               False)
        # If an item from the list is selected and ok is  pressed, return
        # the comport name and exit the menu.
        if okPressed and selectedPort:
            self.statusbar.showMessage(selectedPort)
            self.arduinoPort = selectedPort
             
        
#------------------------------------------------------------------------------ 
# This conditional executes the loop
if __name__=="__main__":
    # Define that the app will draw from pyqt4
    app = QtGui.QApplication(sys.argv)
    # Set style of app to 'CleanLooks'
    style = app.setStyle('CleanLooks')
    # Set the layout and behavour of the app by linking it to class generated above
    form = PlottingApp()
    # Start the app
    form.show()
    form.update() #start with something
    sys.exit(app.exec_())
    # Print debug on exit