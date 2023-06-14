from Common import *
from PIL import Image

#Picture.py by pbsds
#Give credit to pbsds if used!
#
#The PIL Image Library must be installed for this to work!

class Picture():
	def __init__(self,Width = 1,Height = 1,BKColor = 0):
		self.Width = Width
		self.Height = Height
		self.PixelData = [BKColor for i in xrange(self.Width*self.Height)]
	def __str__(self):
		return "Width = " + str(self.Width) + ", Height = " + str(self.Height)
	#Editing:
	def GetPixel(self,X,Y):
		return self.PixelData[self.ValidX(X)+self.ValidY(Y)*self.Width]
	def SetPixel(self,X,Y,RGBA):
		self.PixelData[self.ValidX(X)+self.ValidY(Y)*self.Width] = RGBA
	def Resize(self,NewWidth,NewHeight):#Streches the image into the new dimentions(no resampling :( )
		if NewWidth <> self.Width or NewHeight <> self.Height:
			NewImage = [0 for i in xrange(NewWidth*NewHeight)]
			for x in range(NewWidth):
				for y in range(NewHeight):
					NewImage[x+y*NewWidth] = self.GetPixel(x*self.Width/NewWidth,y*self.Height/NewHeight)
			self.Width = NewWidth
			self.Height = NewHeight
			self.PixelData = NewImage
	def Scale(self,Scale = 1):#resizes the image into the new scale. 1 is the current size, 2 is double the size, 0.5 is half the size, etc...(supports floats)
		self.Resize(int(self.Width*Scale),int(self.Height*Scale))
	def Crop(self,x1,y1,x2,y2):#Cuts out a part of the image
		NewPixelData = [0 for i in range((x2-x1)*(y2-y1))]
		i = 0
		for y in range(y1,y2):
			for x in range(x1,x2):
				NewPixelData[i] = self.GetPixel(x,y)
				if self.ValidX(x) <> x or self.ValidY(y) <> y:
					NewPixelData[i] = 0
				i += 1
		self.Width = x2-x1
		self.Height = y2-y1
		self.PixelData = NewPixelData
	def ColorLight(self,RGB):#Just like black n' white, but with an another color
		Red2 = RGB >> 16 & 0xFF
		Green2 = RGB >> 8 & 0xFF
		Blue2 = RGB & 0xFF
		for i in range(0,len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			Red = (self.PixelData[i]>>24) & 0xFF
			Green = (self.PixelData[i]>>16) & 0xFF
			Blue = (self.PixelData[i]>>8) & 0xFF
			Gray = (Red+Green+Blue)/3
			
			Red = Red2*Gray/255
			Green = Green2*Gray/255
			Blue = Blue2*Gray/255
			
			self.PixelData[i] = (Red<<24) | (Green<<16) | (Blue<<8) | Alpha
	def Blend(self,RGB):#50% the original image, 50% the new color
		Red2 = RGB >> 16 & 0xFF
		Green2 = RGB >> 8 & 0xFF
		Blue2 = RGB & 0xFF
		for i in range(0,len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			Red = (self.PixelData[i]>>24) & 0xFF
			Green = (self.PixelData[i]>>16) & 0xFF
			Blue = (self.PixelData[i]>>8) & 0xFF
			
			Red = (Red+Red2)/2
			Green = (Green+Green2)/2
			Blue = (Blue+Blue2)/2
			
			self.PixelData[i] = (Red<<24) | (Green<<16) | (Blue<<8) | Alpha
	def Brightness(self,Amount):#Makes the image brighter or darker depending on the given amount
		for i in range(0,len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			Red = (self.PixelData[i]>>24) & 0xFF
			Red += Amount
			if Red < 0: Red = 0
			if Red > 255: Red = 255
			Green = (self.PixelData[i]>>16) & 0xFF
			Green += Amount
			if Green < 0: Green = 0
			if Green > 255: Green = 255
			Blue = (self.PixelData[i]>>8) & 0xFF
			Blue += Amount
			if Blue < 0: Blue = 0
			if Blue > 255: Blue = 255
			self.PixelData[i] = (Red<<24) | (Green<<16) | (Blue<<8) | Alpha
	def Contrast(self,Amount):#Adds contrast to the image
		for i in range(0,len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			Red = (self.PixelData[i]>>24) & 0xFF
			Green = (self.PixelData[i]>>16) & 0xFF
			Blue = (self.PixelData[i]>>8) & 0xFF
			if (Red+Green+Blue)/3 >= 128:
				Red += Amount
				if Red < 0: Red = 0
				if Red > 255: Red = 255
				Green += Amount
				if Green < 0: Green = 0
				if Green > 255: Green = 255
				Blue += Amount
				if Blue < 0: Blue = 0
				if Blue > 255: Blue = 255
			else:
				Red -= Amount
				if Red < 0: Red = 0
				if Red > 255: Red = 255
				Green -= Amount
				if Green < 0: Green = 0
				if Green > 255: Green = 255
				Blue -= Amount
				if Blue < 0: Blue = 0
				if Blue > 255: Blue = 255
			self.PixelData[i] = (Red<<24) | (Green<<16) | (Blue<<8) | Alpha
	def BlackAndWhite(self):#Turns the image black n' white
		for i in range(0,len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			Red = (self.PixelData[i]>>24) & 0xFF
			Green = (self.PixelData[i]>>16) & 0xFF
			Blue = (self.PixelData[i]>>8) & 0xFF
			Grey = (Red+Green+Blue)/3
			if Grey > 255: Grey = 255
			self.PixelData[i] = (Grey<<24) | (Grey<<16) | (Grey<<8) | Alpha
	def Invert(self):#Turns the image negative
		for i in range(len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			self.PixelData[i] = ((0xFFFFFF-(self.PixelData[i]>>8))<<8) | Alpha
	def RemoveAlpha(self,BKColor = 1):#Removes the transparency. BKColor: 0 = Black, 1 = White(defult)
		for i in range(len(self.PixelData)):
			Alpha = self.PixelData[i] & 0xFF
			Red = (self.PixelData[i]>>24) & 0xFF
			Green = (self.PixelData[i]>>16) & 0xFF
			Blue = (self.PixelData[i]>>8) & 0xFF
			if BKColor == 1:
				Red = 255-((255-Red)*Alpha/255)
				Green = 255-((255-Green)*Alpha/255)
				Blue = 255-((255-Blue)*Alpha/255)
			else:
				Red = Red*Alpha/255
				Green = Green*Alpha/255
				Blue = Blue*Alpha/255
			self.PixelData[i] = (Red<<24) | (Green<<16) | (Blue<<8) | 255
	def AlphaColor(self,RGB):#New color, same alpha
		RGB <<= 8
		for i in range(0,len(self.PixelData)):
			self.PixelData[i] = RGB | (self.PixelData[i] & 0xFF)
	def FlipHorizontaly(self):#Flips the image horizontaly
		temp2 = self.Width - 1
		for x in range(self.Width/2):
			for y in range(self.Height):
				temp = self.GetPixel(x,y)
				self.SetPixel(x,y,self.GetPixel(temp2-x,y))
				self.SetPixel(temp2-x,y,temp)
	def FlipVerticaly(self):#Flips the image verticaly
		temp2 = self.Height - 1
		for x in range(self.Width):
			for y in range(self.Height/2):
				temp = self.GetPixel(x,y)
				self.SetPixel(x,y,self.GetPixel(x,temp2-y))
				self.SetPixel(x,temp2-y,temp)
	#To and from images:
	def FromFile(self,InputPath):#This will change the width and height to the dimentions of the new image
		temp = Image.open(InputPath)
		Pixels = temp.getdata()
		self.Width, self.Height = temp.size
		self.PixelData = []
		
		if len(Pixels[0]) == 4:
			def Combine(Pixel):
				return Pixel[0] << 24 | Pixel[1] << 16 | Pixel[2] << 8 | Pixel[3]
		else:
			def Combine(Pixel):
				return Pixel[0] << 24 | Pixel[1] << 16 | Pixel[2] << 8 | 0xFF
		
		for i in Pixels:
			self.PixelData.append(Combine(i))
		return self
	def ToFile(self,OutputPath = "out.png"):
		temp = []
		temp2 = DecAsc
		for Pixel in self.PixelData:
			temp.append(temp2(Pixel,4))
		temp = "".join(temp)

		temp = Image.frombytes("RGBA", (self.Width, self.Height), temp)
		FileType = OutputPath[OutputPath.rfind(".")+1:]
		temp.save(OutputPath,FileType)
	#Private:
	def ValidX(self,x):
		if x < 0:
			x = 0
		if x >= self.Width:
			x = self.Width-1
		return x
	def ValidY(self,y):
		if y < 0:
			y = 0
		if y >= self.Height:
			y = self.Height-1
		return y
#==============