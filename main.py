import sys
import cv2
sys.path.append(".")
from multiprocessing import Queue, Event
import multiprocessing
import logging


# ===================================== PROCESS IMPORTS ==================================

from src.client.processClient import processClient
if __name__ == '__main__':
    multiprocessing.freeze_support()

    # ======================================== SETTING UP ====================================

    allProcesses = list()

    Clients = True

    # ===================================== SETUP PROCESSES ==================================

    if Clients:
        SERVER_IP = '192.168.1.2'
        PORT = 12345
        processClient1 = processClient(SERVER_IP, PORT)
        allProcesses.append(processClient1)
        PORT += 1
        processClient2 = processClient(SERVER_IP, PORT)
        allProcesses.append(processClient2)

    # ===================================== START PROCESSES ==================================
    for process in allProcesses:
        process.daemon = True
        process.start()

    # ===================================== STAYING ALIVE ====================================
    blocker = Event()
    try:
        blocker.wait()
    except KeyboardInterrupt:
        print("\nCatching a Keyboard Interruption exception! Shutdown all processes.\n")
        for proc in allProcesses:
            print("Process stopped", proc)
            proc.stop()
            proc.join()
        cv2.destroyAllWindows()