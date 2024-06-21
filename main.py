import sys
import cv2
sys.path.append(".")
from multiprocessing import Queue, Event
import multiprocessing
import logging
import argparse
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsColorizeEffect
from PyQt5.QtGui import QFontDatabase, QPixmap, QImage
from PyQt5.QtCore import QThread, QEvent, pyqtSignal

import qdarktheme

import folium
from MainWindow import MainWindow


# ===================================== PROCESS IMPORTS ==================================

from src.client.processClient import processClient
from src.map.processMap import processMap

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    parser = argparse.ArgumentParser(description='Process Input IP')
    parser.add_argument('--xavierip', type=str, help='Xavier IP', default="192.168.2.193")
    parser.add_argument('--xavierport', type=int, help='Xavier Port', default=12345)
    parser.add_argument('--esp32ip', type=str, help='ESP32 IP', default="192.168.2.194")
    parser.add_argument('--esp32port', type=int, help='Xavier IP', default=3333)
    args = parser.parse_args()

    # ======================================== SETTING UP ====================================

    allProcesses = list()

    Clients = True
    Map = True

    # ===================================== SETUP PROCESSES ==================================

    if Clients:
        SERVER_IP = args.xavierip
        PORT = args.xavierport
        processClient1 = processClient(SERVER_IP, PORT, window.ImageUpdateSlot)
        allProcesses.append(processClient1)
        PORT += 1
        processClient2 = processClient(SERVER_IP, PORT, window.OutputImageUpdateSlot)
        allProcesses.append(processClient2)
    
    if Map:
        SERVER_IP = args.esp32ip
        PORT = args.esp32port
        processMap = processMap(SERVER_IP, PORT, window.WebviewUpdateSlot)
        allProcesses.append(processMap)

    # ===================================== START PROCESSES ==================================
    for process in allProcesses:
        process.daemon = True
        process.start()
    
    window.allProcesses = allProcesses

    # ===================================== STAYING ALIVE ====================================
    sys.exit(app.exec_())
    