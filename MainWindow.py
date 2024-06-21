import os
import sys
import io

from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsColorizeEffect
from PyQt5.QtGui import QFontDatabase, QPixmap, QImage
from PyQt5.QtCore import QThread, QEvent, pyqtSignal

import folium

import cv2
import socket
import pickle
import struct

import csv
from time import sleep
from threading import Thread
import signal

import base64
import numpy as np

from ui_interface import *

from src.client.threads.threadClient import threadClient
from src.map.threads.threadMap import threadMap

class MainWindow(QMainWindow):     
    def __init__(self, Camera, Map, xavierip, xavierport, esp32ip, esp32port, parent=None):
        QMainWindow.__init__(self)
        
        self.Camera = Camera
        self.Map = Map
        self.esp32ip = esp32ip
        self.esp32port = esp32port
        self.xavierip = xavierip
        self.xavierport = xavierport

        self.allProcesses = []

        ################################################################################################
        # Setup the UI main window
        ################################################################################################
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        ################################################################################################
        # Show window
        ################################################################################################
        self.show()

        ################################################################################################
        # HIDE LEFT/RIGHT ARROW SIGNAL
        ################################################################################################
        self.ui.lb_Left_Signal.setVisible(False)
        self.ui.lb_Right_Signal.setVisible(False)

        ################################################################################################
        # CUSTOMIZE ANALOGUE GAUGE SPEED WIDGET
        ################################################################################################
        self.ui.Analog_Gauge_Speed.enableBarGraph = True
        self.ui.Analog_Gauge_Speed.valueNeedleSnapzone = 1

        ################################################################################################
        # Set Angle Offset
        ################################################################################################
        Speed_Gauge_Offset = 0
        self.ui.Analog_Gauge_Speed.updateAngleOffset(Speed_Gauge_Offset)

        ################################################################################################
        # Set gauge units
        ################################################################################################
        self.ui.Analog_Gauge_Speed.units = "Km/h"

        ################################################################################################
        # Set minimum gauge value
        ################################################################################################
        self.ui.Analog_Gauge_Speed.minValue = 0
        ################################################################################################
        # Set maximum gauge value
        ################################################################################################
        self.ui.Analog_Gauge_Speed.maxValue = 100

        ################################################################################################
        # Set scale divisions
        ################################################################################################
        self.ui.Analog_Gauge_Speed.scalaCount = 10
        self.ui.Analog_Gauge_Speed.updateValue(int(self.ui.Analog_Gauge_Speed.maxValue - self.ui.Analog_Gauge_Speed.minValue)/2)

        ################################################################################################
        # Select gauge theme
        ################################################################################################
        self.ui.Analog_Gauge_Speed.setCustomGaugeTheme(
            color1 = "red",
            color2 = "orange",
            color3 = "green"
        )

        self.ui.Analog_Gauge_Speed.setNeedleCenterColor(
            color1 = "dark gray"
        )

        self.ui.Analog_Gauge_Speed.setOuterCircleColor(
            color1 = "dark gray"
        )

        self.ui.Analog_Gauge_Speed.setBigScaleColor("yellow")
        self.ui.Analog_Gauge_Speed.setFineScaleColor("blue")

        if self.Camera:
            self.CameraWorker = threadClient(self.xavierip, self.xavierport)
            self.CameraWorker.start()
            self.CameraWorker.ImageUpdate.connect(self.ImageUpdateSlot)

        if self.Camera:
            self.OutputImageWorker = threadClient(self.xavierip, self.xavierport+1)
            self.OutputImageWorker.start()
            self.OutputImageWorker.ImageUpdate.connect(self.OutputImageUpdateSlot)

        if self.Map:
            self.MapWorker = threadMap(self.esp32ip, self.esp32port)
            self.MapWorker.start()
            self.MapWorker.MapUpdate.connect(self.WebviewUpdateSlot)

        #Register signal for program exit!
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        print("\nCatching a Keyboard Interruption exception! Shutdown all processes.\n")
        if self.Camera:
            self.CameraWorker.stop()
            self.OutputImageWorker.stop()
        if self.Map:
            self.MapWorker.stop()
        sys.exit(0)

    def ImageUpdateSlot(self, image):
        self.ui.lb_Raw_Img.setPixmap(QPixmap.fromImage(image))

    def OutputImageUpdateSlot(self, image):
        self.ui.lb_Output_Img.setPixmap(QPixmap.fromImage(image))

    def WebviewUpdateSlot(self, map_data):
        # Update the WebView with the updated map data
        self.ui.WebView.setHtml(map_data.decode())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.ui.lb_Left_Signal.setVisible(True)   # Show the left arrow signal
        elif event.key() == Qt.Key.Key_Right:
            self.ui.lb_Right_Signal.setVisible(True)  # Show the right arrow signal
            
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.ui.lb_Left_Signal.setVisible(False)   # Hide the left arrow signal
        elif event.key() == Qt.Key.Key_Right:
            self.ui.lb_Right_Signal.setVisible(False)  # Hide the right arrow signal