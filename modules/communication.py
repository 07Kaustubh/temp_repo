from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from modules.serialRead import SerialRead
from modules.tcp import TCP

class SerialThread(QThread,SerialRead):
    dataReceived = pyqtSignal(str)
    def run(self):
        super(SerialRead, self)
    def set_port(self,port):
        self.start_serial(port,self.__serialCallback)
    def __serialCallback(self, data):
        try:
            self.dataReceived.emit(data)
        except Exception as e:
            print("Error in conversion ",e)
class TCPthread(QThread,TCP):
    dataReceived = pyqtSignal(str)
    def run(self):
        super(TCP, self)
    def set_port(self,port):
        self.start_client(port,self.__tcpCallback)
    def __tcpCallback(self, data):
        try:
            self.dataReceived.emit(data)
        except Exception as e:
            print("Error in conversion ",e)




