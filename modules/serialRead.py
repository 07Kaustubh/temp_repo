import serial
import threading
import serial.tools.list_ports
class SerialRead:
    def __init__(self) -> None:
       self.__callback=None
       self.__started=False
       self.__port=""
    def start_serial(self,port,callback):
        self.__callback=callback
        self.__port=port
        if self.__port!="":
            self.__ser = serial.Serial(self.__port, 115200)
            self.__started=True
            threading.Thread(target=self.__readResponse).start()
    def available_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        print("Available ports:",ports)
        return ports
    def stop__serial(self):
        if self.__started:
            self.__started=False
            self.__ser.close()
    def sendRequest(self,comand):
        print("Command send to Port",comand)
       #self.__ser.write(comand.encode("utf-8")+b'\n')
        if isinstance(comand, str):
            self.__ser.write(comand.encode("utf-8") + b'\n')
        elif isinstance(comand, bytes):
            self.__ser.write(comand + b'\n')
        else:
            raise TypeError("Unsupported type for comand. Expected str or bytes.")
    def __readResponse(self):
       while self.__started:
            data = self.__ser.read_until(b'\r\n')
            # print("Data Received From Serial:",data)
            # Decode the data and print it
            #self.__callback(data.decode('utf-8', errors='ignore'))
            self.__callback(data.decode('latin-1', errors='ignore'))


