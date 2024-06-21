import cv2
import threading
import socket
import base64
import time
import numpy as np
import os
import io
import csv

from multiprocessing import Pipe
from src.templates.threadwithstop import ThreadWithStop
import struct
import pickle
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsColorizeEffect
from PyQt5.QtGui import QFontDatabase, QPixmap, QImage
from PyQt5.QtCore import QThread, QEvent, pyqtSignal

import folium
from ui_interface import *


class threadMap(QThread):
    MapUpdate = pyqtSignal(bytes)

    def __init__(self, ip_address, port):
        super().__init__()
        self.ThreadActive = True
        self.ip_address = ip_address
        self.port = port
        self.initial_location = [10.87043, 106.80196]
        self.map = folium.Map(location=self.initial_location, zoom_start=17)
        self.marker = folium.Marker(location=self.initial_location)
        self.marker.add_to(self.map)

    def run(self):
        self.ThreadActive = True
        # self.map = folium.Map(location=[10.87043, 106.80196], zoom_start=17)

        # Read GPS coordinates from CSV file
        with open('route_points.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            coordinates = []

            for row in csv_reader:
                try:
                    latitude, longitude = map(float, row)
                    coordinates.append((latitude, longitude))
                except ValueError:
                    print(f"Skipping invalid row: {row}")

        # Create a PolyLine object with the coordinates
        polyline = folium.PolyLine(locations=coordinates)

        for i in range(len(coordinates)):
            if not self.ThreadActive:
                break

            # Add a PolyLine for the GPS points up to the current index
            folium.PolyLine(locations=coordinates[:i+1], color='blue').add_to(self.map)

            # Save map data to data object
            data = io.BytesIO()
            self.map.save(data, close_file=False)

            # Emit the map_updated signal with the updated map data
            self.MapUpdate.emit(data.getvalue())

            # Wait for 1 second before updating the next coordinate
            time.sleep(1)
        self.terminate()

    def stop(self):
        self.ThreadActive = False
        self.terminate()
