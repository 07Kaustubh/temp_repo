import socket
import uuid
from modules.utils import *
from PyQt5.QtWidgets import QInputDialog, QMessageBox
import threading

imei=[]
args = None

class TCP:
    def __init__(self):
        self.client_socket = None
        self.selected_imei = None
        self.host = TCP_HOST
        self.__callback=None
        self.__started=False
    def stop_tcp(self):
        if self.__started:
            self.__started=False
            self.client_socket.close()
    def send_request(self, request):
        print("Request send to server:",request)
        if self.__started:
            self.client_socket.send(request)
    def start_client(self, server_port,callback):
        self.__callback=callback
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, server_port))
            print(f"Connected to server at {self.host}:{server_port}")
            threading.Thread(target=self.__start_receiving).start()
            
        except socket.error as e:
            print(f"Socket error: {e}")
            self.stop_tcp()
        except Exception as e:
            print(f"An error occurred: {e}")
    def __start_receiving(self):
        self.__started=True
        while self.__started:
           response = self.client_socket.recv(1024)
           response = response.decode('latin-1')
           if response:
               print(response)
               self.__callback(response)
    
    