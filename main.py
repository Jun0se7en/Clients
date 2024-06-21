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

import folium
from MainWindow import MainWindow


# ===================================== PROCESS IMPORTS ==================================

from src.client.processClient import processClient
from src.map.processMap import processMap
from src.client.threads.threadClient import threadClient
from src.map.threads.threadMap import threadMap

if __name__ == '__main__':
    multiprocessing.freeze_support()
    parser = argparse.ArgumentParser(description='Process Input IP')
    parser.add_argument('--xavierip', type=str, help='Xavier IP', default="192.168.1.1")
    parser.add_argument('--xavierport', type=int, help='Xavier Port', default=12345)
    parser.add_argument('--esp32ip', type=str, help='ESP32 IP', default="192.168.1.2")
    parser.add_argument('--esp32port', type=int, help='Xavier IP', default=3333)
    args = parser.parse_args()
    app = QApplication(sys.argv)

    Camera = True
    Map = True

    window = MainWindow(Camera, Map, args.xavierip, args.xavierport, args.esp32ip, args.esp32port)
    window.show()

    # ===================================== STAYING ALIVE ====================================
    sys.exit(app.exec_())
    