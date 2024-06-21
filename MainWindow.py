import os
import sys
import io

from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsColorizeEffect
from PyQt5.QtGui import QFontDatabase, QPixmap, QImage
from PyQt5.QtCore import QThread, QEvent, pyqtSignal

import qdarktheme

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

class MainWindow(QMainWindow):     
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        
        self.allProcesses = []

        ################################################################################################
        # Setup the UI main window
        ################################################################################################
        qdarktheme.setup_theme()
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

        #Register signal for program exit!
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        print("\nCatching a Keyboard Interruption exception! Shutdown all processes.\n")
        for proc in self.allProcesses:
            print("Process stopped", proc)
            proc.stop()
            proc.join()
        # logger.info("Received Ctrl+C, stopping processes...")
        # Stop all processes:
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