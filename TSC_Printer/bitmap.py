import ctypes
from PIL import Image
import numpy as np

tsclibrary = ctypes.WinDLL(".\TSC_Printer\libs\TSCLIB.dll");
class Printer:
# Config
	PWIDTH	= 60	# tag width, measured in mm
	PHEIGHT = 50		# tag height
	PGAP 	= 3.5# gap between tags
	DPI		= 200		# DPI of printer
	SPEED	= 2		# printing speed
	DENSITY = 10	# ink density
	SENSOR	= 0	# type of sensor 0>gap 1>black mark
	OFFSET  = 0		# GAP offset
	DOT 	= DPI//100*4# Dots per mm
	# DOT=7
	CONTRAST= 180		# A number between 0~255
	left = l = 0
	# right = r = 240

	def printPic(self,imName,x,y,mode):
		print("PRINTING ", imName)
		im = Image.open(imName)
		# im.thumbnail((PWIDTH*DOT//2,PHEIGHT*DOT))
		im.thumbnail((Printer.PWIDTH*Printer.DOT,Printer.PHEIGHT*Printer.DOT),Image.BICUBIC)
		width,height = im.size

		if width<248:	# report err for now, edit later
			print("FAILURE: IMAGE IS TOO SMALL\n")
			return -1

		im = im.convert("L") 
		data = im.getdata()
		data = np.matrix(data)
		data = data.tolist()[0]

		im1 = [1 for i in range(width*height)]
		for i in range(width*height):
			if data[i] < Printer.CONTRAST:
				im1[i] = 0
		bitmap = [0   for i in range(width*height//8)]	# sending 0 may cause some err
		offset = [255 for i in range(width*height//8)]	# so use offset to make it work
		for i in range(width*height//8):
			bitmap[i] = eval("0b"+str(im1[i*8:(i+1)*8]).replace(" ","").replace(",",'').replace("[",'').replace("]",''))
			if bitmap[i] == 0:
				bitmap[i] = 1
				offset[i] = 254
		# self.seeBitmap(bitmap)
		ini = "BITMAP "+str(0)+","+str(0)+","+str(width//8)+","+str(height)+","+str(mode)+","
		print(ini)
		ini = ini.encode()
		bm = bytes(bitmap)
		ofs = bytes(offset)
		end = "\0".encode()
		tsclibrary.sendcommand(ini + bm + end);
		tsclibrary.sendcommand(ini + ofs + end);
		return 

	def seeBitmap(self,bitmap):
		ss = ""
		for i in bitmap:
			if i == 1:
				ss += "00 "
			else:
				tt = str(hex(i))[2:].upper()
				if len(tt)==1:
					tt = "0"+tt
				ss+=tt+" "
		print(ss)
	def printOnTop(self,imName,position):
		self.printPic(imName,position,0,1)

	def print(self,url,data):
		# tsclibrary.openportW("USB");
		# # tsclibrary.setup(str(self.PWIDTH),str(self.PHEIGHT),str(self.SPEED),str(self.DENSITY),str(self.SENSOR),str(self.PGAP),str(self.OFFSET))
		# tsclibrary.sendcommandW("DENSITY "+str(Printer.DENSITY));
		# tsclibrary.sendcommandW("SIZE " + str(Printer.PWIDTH) +" mm, " + str(Printer.PHEIGHT) +" mm");
		# tsclibrary.sendcommandW("GAP "+str(Printer.PGAP)+" mm, 0");
		# # tsclibrary.sendcommandW("DIRECTION 1");
		# # tsclibrary.sendcommandW("GAPDETECT ["+str(PHEIGHT*DOT)+","+str(PGAP*DOT)+"]");
		# # tsclibrary.sendcommandW("HOME");
		# tsclibrary.clearbuffer();
		# tsclibrary.sendcommandW("CLS");
		# self.printOnTop(url,Printer.left)
		# # printOnTop(".//image//im05.png",right)
		# tsclibrary.printlabelW("1","1");
		# tsclibrary.closeport();

		tsclibrary.openportW("USB");
		tsclibrary.sendcommandW(f"SIZE {60} mm, {27} mm");
		tsclibrary.sendcommandW("GAP 2 mm, 0 mm");
		tsclibrary.sendcommandW("DIRECTION 1");
		tsclibrary.sendcommandW("CLS");
		# tsclibrary.sendcommandW("TEXT 10,30,\"3\",0,1,1,\"123456\"");
		tsclibrary.sendcommandW(f"BARCODE 110,130, \"128\",50,2,0,1,1,\"{data}\"")
		# tsclibrary.barcodeW("10","150","Code 128","80","1","0","2","4","00545616281203C0C699200724000023");
		# tsclibrary.printerfontW("10", "70", "4", "0", "1", "1", "TEST PRINTOUT");
		# tsclibrary.windowsfontW("10","100","24","0", "0", "0", "Arial","Window Font Test");
		# tsclibrary.downloadpcxW("UL.PCX","UL.PCX");
		# tsclibrary.sendcommandW("PUTPCX 10,300,\"UL.PCX\"");
		self.printOnTop(url,Printer.left)
		tsclibrary.printlabelW("1","1");
		tsclibrary.closeport();
if __name__=="__main__":
	p = Printer()
	p.print("D:\\NripenderProject\\DesktopApp\\final_image.bmp","00545616281203C0C699200824000005")