import cv2
import threading
import socket
import base64
import time
import numpy as np
import os
import io
import csv
import json
import random

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

    def __init__(self, ip_address, port, update_speed_func, update_steer_func):
        super().__init__()
        self.ThreadActive = True
        # self.initial_location = [10.87043, 106.80196]
        # self.map = folium.Map(location=self.initial_location, zoom_start=17)
        # self.marker = folium.Marker(location=self.initial_location)
        # self.marker.add_to(self.map)
        self.PORT = port
        self.SERVER_ADDRESS = ip_address
        self.gps_coordinates = []
        self.update_speed_func = update_speed_func
        self.update_steer_func = update_steer_func
        self.connect_flag = False
        self.gps_latitude = 0.0
        self.gps_longitude = 0.0
        self.initial_flag = False

    def run(self):
        self.ThreadActive = True
        # # Read GPS coordinates from CSV file
        # with open('route_points.csv', 'r') as file:
        #     csv_reader = csv.reader(file)
        #     next(csv_reader)  # Skip the header row
        #     coordinates = []

        #     for row in csv_reader:
        #         try:
        #             latitude, longitude = map(float, row)
        #             coordinates.append((latitude, longitude))
        #         except ValueError:
        #             print(f"Skipping invalid row: {row}")

        # # Create a PolyLine object with the coordinates
        # polyline = folium.PolyLine(locations=coordinates)

        # for i in range(len(coordinates)):
        #     if not self.ThreadActive:
        #         break

        #     # Add a PolyLine for the GPS points up to the current index
        #     folium.PolyLine(locations=coordinates[:i+1], color='blue').add_to(self.map)

        #     # Save map data to data object
        #     data = io.BytesIO()
        #     self.map.save(data, close_file=False)

        #     # Emit the map_updated signal with the updated map data
        #     self.MapUpdate.emit(data.getvalue())

        #     # Wait for 1 second before updating the next coordinate
        #     time.sleep(1)
        # self.terminate()

        ################ ESP SOCKET ############################
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Information Socket created')
        while not self.connect_flag:
            try:
                self.socket.connect((self.SERVER_ADDRESS, self.PORT))  # connect to the server
                self.connect_flag = True
            except:
                print('Connecting Failed!!! Retrying....')
                pass

        resp_data = b""
        payload_size = struct.calcsize("Q")

        while self.ThreadActive:
            # while len(resp_data) < payload_size:
            #     packet = self.socket.recv(4*1024)
            #     if not packet: break
            #     resp_data+=packet
            # packed_msg_size = resp_data[:payload_size]
            # resp_data = resp_data[payload_size:]
            # msg_size = struct.unpack("Q",packed_msg_size)[0]
            
            # while len(resp_data) < msg_size:
            #     resp_data += self.socket.recv(4*1024)
            # response_data = resp_data[:msg_size]
            # resp_data = resp_data[msg_size:]
            # response = pickle.loads(response_data)
            # # response = json.load(response)
            # # print(f'Received response: {response}')
            # # print(f'Received response: {response}')
            # self.gps_latitude = response["0"]
            # self.gps_longitude = response["1"]
            # # print('GPS lat: ', self.gps_latitude, "GPS long: ", self.gps_longitude)
            # self.speed = response["2"]*3.6
            # self.steer = response["3"]
            # # self.speed = random.randint(0,8)*3.6
            # # self.steer = random.randint(-25, 25)
            # # print('Speed: ', self.speed, 'Steer: ', self.steer)
            # self.update_speed_func(self.speed)
            # self.update_steer_func(self.steer)
            # # if not self.initial_flag:
            # #     if self.gps_latitude != 0.0 and self.gps_longitude != 0.0:
            # #         self.marker = folium.Marker(location=[self.gps_latitude, self.gps_longitude])
            # #         self.marker.add_to(self.map)
            # #         self.gps_coordinates.append((self.gps_latitude, self.gps_longitude))
            # #         folium.PolyLine(locations=self.gps_coordinates, color='blue').add_to(self.map)
            # #         # Save map data to data object
            # #         data = io.BytesIO()
            # #         self.map.save(data, close_file=False)

            # #         # Emit the map_updated signal with the updated map data
            # #         self.MapUpdate.emit(data.getvalue())

            # #         # # Wait for 1 second before updating the next coordinate
            # #         # time.sleep(1)
            # #         print('Map Initialize Successfully!!!')
            # #         self.initial_flag = True
            # # else:
            # #     self.gps_coordinates.append((self.gps_latitude, self.gps_longitude))
            # #     folium.PolyLine(locations=self.gps_coordinates, color='blue').add_to(self.map)
            # #     # Save map data to data object
            # #     data = io.BytesIO()
            # #     self.map.save(data, close_file=False)

            # #     # Emit the map_updated signal with the updated map data
            # #     self.MapUpdate.emit(data.getvalue())

            # #     # # Wait for 1 second before updating the next coordinate
            # #     time.sleep(1)
            time.sleep(0.2)
        self.socket.close()
        self.terminate()

    def stop(self):
        self.ThreadActive = False
        self.socket.close()
        self.terminate()
