#!/usr/bin/env python2

# ___________________________________
#/                                   \
#|            Wiiteboard             |
#|By: pbsds / Peder Bergebakken Sundt|
#\___________________________________/
#
#Started: Thursday 6. march 2012
#Finished: Sunday 3. June 2012
#

print "Importing modules..."
import sys, pygame, math, colorsys
import wiimote

#Initalize pygame:
print "Initalizing pygame..."
pygame.init()
pygame.display.set_caption("Wiiteboard - by pbsds")
Window = pygame.display.set_mode((800,600), pygame.FULLSCREEN)
Timer = pygame.time.Clock()
pygame.mouse.set_visible(False)

#Globals:
Wiimote = None
PrevPens = [None, None, None, None]#Used for smoother drawing
PensCooldown = [0, 0, 0, 0]#Used for clicking

#Helpers:
def ComputeLine((x, y), (x2, y2)):#Brensenhams line algorithm:
	steep = 0
	coords = []
	dx = abs(x2 - x)
	if (x2 - x) > 0:
		sx = 1
	else:
		sx = -1
	dy = abs(y2 - y)
	if (y2 - y) > 0:
		sy = 1
	else:
		sy = -1
	if dy > dx:
		steep = 1
		x,y = y,x
		dx,dy = dy,dx
		sx,sy = sy,sx
	d = (2 * dy) - dx
	for i in range(0,dx):
		if steep:
			coords.append((y,x))
		else:
			coords.append((x,y))
		while d >= 0:
			y = y + sy
			d = d - (2 * dx)
		x = x + sx
		d = d + (2 * dy)
	coords.append((x2,y2))
	return coords
def PointDistance((x, y), (x2, y2)):
	return math.sqrt((x2-x)*(x2-x) + (y2-y)*(y2-y))
def PointDirection((x, y), (x2, y2)):
	return math.atan2(y-y2, x2-x)/math.pi*180
def LengthDir(Dir, Len):#Dir is from 0-1
	return ( math.cos(float(Dir)*math.pi*2) * Len,
			-math.sin(float(Dir)*math.pi*2) * Len)
def DegreeDiff(dir1, dir2):
	return (((dir2-dir1) % 360)+540) % 360 - 180
			
#Load graphics into memory:
print "Loading graphics into memory..."
def LoadImage(FilePath, alpha = False):
	if alpha:
		return pygame.image.load(FilePath).convert_alpha()
	else:
		return pygame.image.load(FilePath).convert()
BG=(LoadImage("graphic/ConnectWiimote.png"),
	LoadImage("graphic/MainMenu.png"),
	LoadImage("graphic/DrawingGUI.png"))
Sprites =  (LoadImage("graphic/CallibrationMarker.png", True),
			LoadImage("graphic/ScrollbarL.png", True),
			LoadImage("graphic/ScrollbarR.png", True),
			LoadImage("graphic/ToolButtonBG.png", True),
			LoadImage("graphic/ToolButtonBG2.png", True),
			LoadImage("graphic/ToolButtonBG3.png", True),
			LoadImage("graphic/BrushDrawer.png", True),
			LoadImage("graphic/PaletteDrawer.png", True),
			LoadImage("graphic/SliderNub.png", True),
			LoadImage("graphic/SliderNub2.png", True))
ToolIcons =(LoadImage("graphic/Tools/Brush.png", True),
			LoadImage("graphic/Tools/Eraser.png", True),
			LoadImage("graphic/Tools/Palette.png", True),
			LoadImage("graphic/Tools/Undo.png", True),
			LoadImage("graphic/Tools/NoUndo.png", True),
			LoadImage("graphic/Tools/Redo.png", True),
			LoadImage("graphic/Tools/NoRedo.png", True),
			LoadImage("graphic/Tools/Exit.png", True),
			LoadImage("graphic/Tools/Add.png", True))

#Setup fonts:
class Text():
	def __init__(self):
		self.Font = (pygame.font.Font("graphic/font.ttc",16), pygame.font.Font("graphic/font.ttc",32), pygame.font.Font("graphic/font.ttc",48))
	def Create16(self, Input, Color=(255, 255, 255)):
		return self.Font[0].render(Input, True, Color)
	def Create32(self, Input, Color=(255, 255, 255)):
		return self.Font[1].render(Input, True, Color)
	def Create48(self, Input, Color=(255, 255, 255)):
		return self.Font[2].render(Input, True, Color)
Text = Text()
#GUI Objects:
class SliderObj:
	def __init__(self, SpriteIdle, SpritePressed, Pos, Range, Value = 0, Event = None):
		self.Pos = Pos
		self.Range = Range
		self.Value = Value
		self.Sprites = (SpriteIdle, SpritePressed)
		self.Size = SpriteIdle.get_size()
		self.Event = Event#Called whenever self.Value changes.
		
		self.Cooldown = -1
		self.Held = False
	def Step(self, Events, WmInput, Pens):
		global PensCooldown
		
		self.Cooldown -= 1
		Closest = [self.Range, -1]
		center = (self.Pos[0]+self.Value+(self.Size[0]/2), self.Pos[1]+(self.Size[1]/2))
		for i in xrange(4):
			if not Pens[i]: continue
			
			if not self.Held:
				if PensCooldown[i] <= 0:
					if self.Pos[0]+self.Value <= Pens[i][0] < self.Pos[0]+self.Value+self.Size[0] and self.Pos[1] <= Pens[i][1] < self.Pos[1]+self.Size[1]:
						print "Clicked on slider!"
						self.Held = True
						Closest[0] = 0.0
						Closest[1] = i
						self.Cooldown = 5
						break
			
			if self.Held:
				if PointDistance(center, Pens[i]) <= Closest[0]:
					Closest[0] = PointDistance(center, Pens[i])
					Closest[1] = i
					self.Cooldown = 5
		if self.Held and Closest[1] <> -1:
			self.Value = max((min((Pens[Closest[1]][0]-self.Pos[0]-self.Size[0]/2, self.Range)), 0))
			if self.Event: self.Event(self.Value)
		elif self.Held and self.Cooldown == 0:
			print "Let go of slider..."
			self.Held = False
	def Draw(self, Surface):
		if self.Held:
			Surface.blit(self.Sprites[1], (self.Pos[0]+self.Value, self.Pos[1]))
		else:
			Surface.blit(self.Sprites[0], (self.Pos[0]+self.Value, self.Pos[1]))
class VertSliderObj:
	def __init__(self, SpriteIdle, SpritePressed, Pos, Range, Value = 0, Event = None):
		self.Pos = Pos
		self.Range = Range
		self.Value = Value
		self.Sprites = (SpriteIdle, SpritePressed)
		self.Size = SpriteIdle.get_size()
		self.Event = Event#Called whenever self.Value changes.
		
		self.Cooldown = -1
		self.Held = False
	def Step(self, Events, WmInput, Pens):
		global PensCooldown
		
		self.Cooldown -= 1
		Closest = [self.Range, -1]
		center = (self.Pos[0]+(self.Size[0]/2), self.Pos[1]+self.Value+(self.Size[1]/2))
		for i in xrange(4):
			if not Pens[i]: continue
			
			if not self.Held:
				if PensCooldown[i] <= 0:
					if self.Pos[0] <= Pens[i][0] < self.Pos[0]+self.Size[0] and self.Pos[1]+self.Value <= Pens[i][1] < self.Pos[1]+self.Value+self.Size[1]:
						print "Clicked on slider!"
						self.Held = True
						Closest[0] = 0.0
						Closest[1] = i
						self.Cooldown = 5
						break
			
			if self.Held:
				if PointDistance(center, Pens[i]) <= Closest[0]:
					Closest[0] = PointDistance(center, Pens[i])
					Closest[1] = i
					self.Cooldown = 5
		if self.Held and Closest[1] <> -1:
			self.Value = max((min((Pens[Closest[1]][1]-self.Pos[1]-self.Size[1]/2, self.Range)), 0))
			if self.Event: self.Event(self.Value)
		elif self.Held and self.Cooldown == 0:
			print "Let go of slider..."
			self.Held = False
	def Draw(self, Surface):
		if self.Held:
			Surface.blit(self.Sprites[1], (self.Pos[0], self.Pos[1]+self.Value))
		else:
			Surface.blit(self.Sprites[0], (self.Pos[0], self.Pos[1]+self.Value))
class ButtonObj:
	def __init__(self, SpriteIdle, SpritePressed, (x, y), Event = None):
		self.Sprites = (SpriteIdle, SpritePressed)
		self.Clicked = 0
		self.Pos = (x, y)
		self.Size = SpriteIdle.get_size()
		self.Event = Event
	def Step(self, Events, WmInput, Pens):
		global PensCooldown
		
		ret = False
		
		if self.Clicked > 0:
			self.Clicked -= 1
		
		#Check if clicked:
		for i in xrange(4):
			#Check if the pen is visible and cooled down:
			if Pens[i] == None or PensCooldown[i] > 0: continue
			
			#Check if the pen is within the button:
			if self.Pos[0] <= Pens[i][0] < self.Pos[0]+self.Size[0] and self.Pos[1] <= Pens[i][1] < self.Pos[1]+self.Size[1]:
				
				#Call event, if any:
				if self.Event:
					self.Event()
				
				#Return to parent:
				ret = True
				
				#Change the sprite:
				self.Clicked = 5
		
		return ret
	def Draw(self, Surface):
		if self.Clicked:
			Surface.blit(self.Sprites[1], self.Pos)
		else:
			Surface.blit(self.Sprites[0], self.Pos)
class DrawingObj:
	def __init__(self):
		global Text
		self.Tool = 1#1 = Brush, 2 = Eraser
		self.Size = 2#1 - 4 brush size
		self.Color = [0,0,0, 0.0,0.0,0.0, 149,392]#[r,g,b, h,s,v, x,y]
		self.Scroll = 0#0 - 408(position of the scrollbar)
		self.Drawing = False#Used to know when to save a copy of self.Surface to the history
		self.Cursors = []#A list of points to draw a cursor
		
		self.Surface = pygame.Surface((734, 527)).convert()#Current drawing
		self.History = [self.Surface.copy()]#Contains the 30 previous versions of self.Surface plus the current one
		self.Future = []#Used for the REDO function
		
		self.HEX = Text.Create16("0x000000", (0, 0, 0))
		self.BrushDrawer = False#Wether the brush drawer shall be visible or not.
		self.ColorDrawer = False#Wether the pelette drawer shall be visible or not.
		self.Brushes = (ButtonObj(Sprites[3], Sprites[4], (138, 449)),
						ButtonObj(Sprites[5], Sprites[4], (206, 449)),
						ButtonObj(Sprites[3], Sprites[4], (274, 449)),
						ButtonObj(Sprites[3], Sprites[4], (342, 449)))
		self.Colours = (SliderObj(Sprites[8], Sprites[9], (334, 291), 200, Event = self.RGB_R),#r
						SliderObj(Sprites[8], Sprites[9], (334, 323), 200, Event = self.RGB_G),#g
						SliderObj(Sprites[8], Sprites[9], (334, 355), 200, Event = self.RGB_B),#b
						SliderObj(Sprites[8], Sprites[9], (334, 387), 200, Event = self.HSV_H),#h
						SliderObj(Sprites[8], Sprites[9], (334, 419), 200, Event = self.HSV_S),#s
						SliderObj(Sprites[8], Sprites[9], (334, 451), 200, Event = self.HSV_V),#v
						SliderObj(Sprites[8], Sprites[9], (334, 483), 200, 200))#alpha
		self.Scrollbars  = (VertSliderObj(Sprites[1], Sprites[1], (  0, -4), 408, Event = self.SetScroll),
							VertSliderObj(Sprites[2], Sprites[2], (767, -4), 408, Event = self.SetScroll))
		
		self.Surface.fill((255, 255, 255))
		self.History[0].fill((255, 255, 255))
	def Step(self, Events, WmInput, Pens):
		global PensCooldown, PrevPens, Sprites
		
		#Step scrollbars:
		self.Scrollbars[0].Step(Events, WmInput, Pens)
		self.Scrollbars[1].Step(Events, WmInput, Pens)
		
		#Step brushbuttons:
		if self.BrushDrawer:
			for i in xrange(4):
				if self.Brushes[i].Step(Events, WmInput, Pens):
					self.Size = i+1
					for j in xrange(4):
						if j == i: continue
						self.Brushes[j].Sprites = (Sprites[3], Sprites[4])
					self.Brushes[i].Sprites = (Sprites[5], Sprites[4])
		
		#Step Palette Drawer:
		if self.ColorDrawer:
			for i in xrange(7):
				self.Colours[i].Step(Events, WmInput, Pens)
		
		#Perform the drawing: ADD ERASER and scrollbars!!!
		drawing = False
		self.Cursors = []
		y = (self.Surface.get_height()-527)*self.Scroll/408
		for i in xrange(4):
			if self.ColorDrawer and Pens[i]:
				S = PointDistance((149, 392), Pens[i])
				if S < 100.0:
					S /= 100.0
					H = PointDirection((149, 392), Pens[i])
					if H < 0.0: H += 360.0
					if H >= 360.0: H -= 360.0
					H /= 360.0
					
					self.Color[3] = H
					self.Color[4] = S
					self.Color[5] = 1.0
					self.UpdateRGB()
					self.UpdatePos()
					self.UpdateSliders()
			
			if self.Drawing and (Pens[i] or PrevPens[i]):
				drawing = True
			elif Pens[i]:
				if 33 <= Pens[i][0] < 767 and Pens[i][1] < 527 and not (self.BrushDrawer and 136 <= Pens[i][0] < 412 and 447 <= Pens[i][1] < 519) and not (self.ColorDrawer and 41 <= Pens[i][0] < 559 and 288 <= Pens[i][1] < 519):
					drawing = True
			
			if Pens[i] and drawing:
				self.Cursors.append(Pens[i])
				if PrevPens[i]:
					for i in ComputeLine(PrevPens[i], Pens[i])[1:]:
						if not (self.BrushDrawer and 136 <= i[0] < 412 and 447 <= i[1] < 519) and not (self.ColorDrawer and 41 <= i[0] < 559 and 288 <= i[1] < 519):
							if self.Tool == 2:
								pygame.draw.circle(self.Surface, (255, 255, 255, 255), (i[0]-33, i[1]+y), self.Size*3, 0)
							else:
								pygame.draw.circle(self.Surface, (self.Color[0], self.Color[1], self.Color[2], 255), (i[0]-33, i[1]+y), self.Size*3, 0)
				else:
					if not (self.BrushDrawer and 136 <= Pens[i][0] < 412 and 447 <= Pens[i][1] < 519) and not (self.ColorDrawer and 41 <= Pens[i][0] < 559 and 288 <= Pens[i][1] < 519):
						if self.Tool == 2:
							pygame.draw.circle(self.Surface, (255, 255, 255, 255), (Pens[i][0]-33, Pens[i][1]+y), self.Size*3, 0)
						else:
							pygame.draw.circle(self.Surface, (self.Color[0], self.Color[1], self.Color[2], 255), (Pens[i][0]-33, Pens[i][1]+y), self.Size*3, 0)
		
		#Check if the current stroke is finished:
		if self.Drawing and not drawing:
			print "Added stroke to history."
			#Add the changed surface to the history:
			self.History.append(self.Surface.copy())
			if len(self.History) > 31:
				del self.History[0]
			while len(self.Future):
				del self.Future[0]
		
		self.Drawing = drawing
	def Draw(self, Surface):
		global Sprites
		Surface.blit(self.Surface, (33, 0), pygame.Rect(0, (self.Surface.get_height()-527)*self.Scroll/408, 734, 527))
		self.Scrollbars[0].Draw(Surface)
		self.Scrollbars[1].Draw(Surface)
		
		if self.BrushDrawer:
			Surface.blit(Sprites[6], (134, 445))
			for i in xrange(4):
				self.Brushes[i].Draw(Surface)
				if self.Tool == 2:
					pygame.draw.circle(Window, (255, 255, 255), (173 + 68*i, 483), i*3+3, 0)
					pygame.draw.circle(Window, (0, 0, 0), (173 + 68*i, 483), i*3+3, 1)
				else:
					pygame.draw.circle(Window, self.Color[:3], (173 + 68*i, 483), i*3+3, 0)
		
		if self.ColorDrawer:
			Surface.blit(Sprites[7], (39, 286))
			for i in self.Colours: i.Draw(Surface)
			pygame.draw.rect(Surface, (0,0,0), (self.Color[6]-1, self.Color[7]-1, 3, 3), 1)
			Surface.blit(self.HEX, (165 - self.HEX.get_width()/2, 497))
		
		if self.Tool == 2:
			for x, y in self.Cursors:
				if 33 <= x < 767 and y < 527 and not (self.BrushDrawer and 136 < x < 412 and 447 < y < 519) and not (self.ColorDrawer and 41 <= x < 559 and 288 <= y < 519):
					#pygame.draw.circle(Window, (255, 255, 255), (x, y), self.Size*3, 0)
					pygame.draw.circle(Window, (0, 0, 0), (x, y), self.Size*3, 1)
	def UpdateHSV(self):
		self.Color[3], self.Color[4], self.Color[5] = colorsys.rgb_to_hsv(float(self.Color[0])/255, float(self.Color[1])/255, float(self.Color[2])/255)
	def UpdateRGB(self):
		r, g, b = colorsys.hsv_to_rgb(self.Color[3], self.Color[4], self.Color[5])
		self.Color[0] = int(r*255)
		self.Color[1] = int(g*255)
		self.Color[2] = int(b*255)
	def UpdatePos(self):
		x, y = LengthDir(self.Color[3], self.Color[4]*99)
		self.Color[6] = int(x+149.5)
		self.Color[7] = int(y+392.5)
	def UpdateSliders(self):
		self.Colours[0].Value = self.Color[0]*200/255
		self.Colours[1].Value = self.Color[1]*200/255
		self.Colours[2].Value = self.Color[2]*200/255
		self.Colours[3].Value = int(self.Color[3]*200)
		self.Colours[4].Value = int(self.Color[4]*200)
		self.Colours[5].Value = int(self.Color[5]*200)
		
		del self.HEX
		self.HEX = Text.Create16("0x" + hex(self.Color[0])[2:] + hex(self.Color[1])[2:] + hex(self.Color[2])[2:], (0, 0, 0))
	#Toolbutton events:
	def SetBrush(self):
		global Sprites, DrawTools
		self.Tool = 1
		DrawTools[0].Sprites = (Sprites[5], Sprites[4])
		DrawTools[1].Sprites = (Sprites[3], Sprites[4])
		print "Tool set to BRUSH"
	def SetEraser(self):
		global Sprites, DrawTools
		self.Tool = 2
		DrawTools[0].Sprites = (Sprites[3], Sprites[4])
		DrawTools[1].Sprites = (Sprites[5], Sprites[4])
		print "Tool set to ERASER"
	def Undo(self):
		if len(self.History) > 1:
			self.Future.append(self.History.pop())
			del self.Surface
			self.Surface = self.History[-1].copy()
			print "Performed an UNDO successfully!"
		else:
			print "Performed an UNDO unsuccessfully... (Out of history)"
	def Redo(self):
		if len(self.Future):
			self.History.append(self.Future.pop())
			del self.Surface
			self.Surface = self.History[-1].copy()
			print "Performed an REDO successfully!"
		else:
			print "Performed an REDO unseccessfully... (Out of future history)"
	def BrushDrawerOpen(self):
		print "Brush drawer"
		self.BrushDrawer = not self.BrushDrawer
		for i in self.Brushes:
			i.Clicked = 0
		self.ColorDrawer = False
		for i in self.Colours:
			i.Held = False
	def ColorDrawerOpen(self):
		print "Color drawer"
		self.ColorDrawer = not self.ColorDrawer
		for i in self.Colours:
			i.Held = False
		self.BrushDrawer = False
		for i in self.Brushes:
			i.Clicked = 0
	def ExpandButton(self):
		print "Expand surface..."
		self.Surface = pygame.Surface((734, self.Surface.get_height()+408)).convert()
		self.Surface.fill((255, 255, 255))
		self.Surface.blit(self.History[-1], (0, 0))
		self.SetScroll(408)
		
		self.History.append(self.Surface.copy())
		if len(self.History) > 31:
			del self.History[0]
	def Exit(self):
		global Handler, DrawTools
		
		return
		#sys.exit()
		
		#Back to "main menu":
		if 1 == 2:
			self.Tool = 1#1 = Brush, 2 = Eraser
			self.Size = 2#1 - 4 brush size
			self.Color = [0,0,0, 0.0,0.0,0.0, 149,392]
			self.UpdateSliders()
			self.SetScroll(0)
			self.Drawing = False#Used to know when to save a copy of self.Surface to the history
			self.Cursors = []#A list of points to draw a cursor
			self.BrushDrawer = False#Wether the brush drawer shall be visible or not.
			self.ColorDrawer = False#Wether the pelette drawer shall be visible or not.
			
			while len(self.History):
				del self.History[0]
			while len(self.Future):
				del self.Future[0]
			self.Surface = pygame.Surface((734, 527)).convert()
			self.History.append(self.Surface.copy())
			self.Surface.fill((255, 255, 255))
			self.History[0].fill((255, 255, 255))
			
			Handler = 1
			
			for i in DrawTools:
				i.Clicked = min((i.Clicked, 1))
	#Slider events:
	def RGB_R(self, R):
		self.Color[0] = R*255/200
		self.UpdateHSV()
		self.UpdatePos()
		self.UpdateSliders()
	def RGB_G(self, G):
		self.Color[1] = G*255/200
		self.UpdateHSV()
		self.UpdatePos()
		self.UpdateSliders()
	def RGB_B(self, B):
		self.Color[2] = B*255/200
		self.UpdateHSV()
		self.UpdatePos()
		self.UpdateSliders()
	def HSV_H(self, H):
		self.Color[3] = float(H)/200
		self.UpdateRGB()
		self.UpdatePos()
		self.UpdateSliders()
	def HSV_S(self, S):
		self.Color[4] = float(S)/200
		self.UpdateRGB()
		self.UpdatePos()
		self.UpdateSliders()
	def HSV_V(self, V):
		self.Color[5] = float(V)/200
		self.UpdateRGB()
		self.UpdatePos()
		self.UpdateSliders()
	#Scrollbar event:
	def SetScroll(self, Value):
		self.Scroll = Value
		self.Scrollbars[0].Value = Value
		self.Scrollbars[1].Value = Value

#Drawing variables:
DrawingObj = DrawingObj()
DrawTools =(ButtonObj(Sprites[5], Sprites[4], (  2, 530), DrawingObj.SetBrush),
			ButtonObj(Sprites[3], Sprites[4], ( 70, 530), DrawingObj.SetEraser),
			ButtonObj(Sprites[3], Sprites[4], (138, 530), DrawingObj.ColorDrawerOpen),
			ButtonObj(Sprites[3], Sprites[4], (206, 530), DrawingObj.BrushDrawerOpen),
			ButtonObj(Sprites[3], Sprites[4], (308, 530), DrawingObj.Undo),
			ButtonObj(Sprites[3], Sprites[4], (376, 530), DrawingObj.Redo),
			ButtonObj(Sprites[3], Sprites[4], (444, 530), DrawingObj.Exit),
			ButtonObj(Sprites[3], Sprites[4], (730, 530), DrawingObj.ExpandButton))
PenVisible = False

#Mainloop and sub-Handlers:
Handler = 0
def MainLoop():#Keeps the FPS, reads Events and calls the needed handlers:
	global Handler, Timer, Sprites, PensCooldown, PrevPens
	first = True
	while 1:
		#FPS:
		Timer.tick(60)
		
		#Input:
		Events = pygame.event.get()
		if Handler:
			WmInput = Wiimote.GetButtonInput()
			Pens = Wiimote.CalculatePenPosition()
		else:
			WmInput, Pens = [], (None, None, None, None)
		
		#Check if exiting...
		for i in Events:
			if i.type == pygame.QUIT:
				print "Exiting..."
				sys.exit(0)
			if i.type == pygame.KEYDOWN:
				if i.key == pygame.K_ESCAPE:
				  sys.exit(0)
		
		#Run the correct handler:
		(ConnectHandler, MenuHandler, DrawHandler)[Handler](Events, WmInput, Pens)
		if first:
			first = False
			continue
		
		#Keep track of IR history:
		for i in xrange(4):
			PensCooldown[i] -= 1
			if Pens[i] <> None:
				PensCooldown[i] = 5
				PrevPens[i] = Pens[i]
			if PensCooldown[i] == 0:
				PrevPens[i] = None
		
		#Callibrate if neccesary or inquired:
		if "1" in WmInput or (not Wiimote.callibrated and Handler):
			Wiimote.CallibratePen(Window, Sprites[0], Timer, Text)
			PensCooldown = [0, 0, 0, 0]
			PrevPens = [None, None, None, None]
def ConnectHandler(Events, WmInput, Pens):#Handler #0
	global BG, Window, Wiimote, Handler
	
	#Draws BG:
	Window.blit(BG[0], (0,0))
	
	#Refreshes the window:
	pygame.display.flip()
	
	#Search for wiimote(will sleep here until connected...):
	Wiimote = wiimote.Wiimote()
	
	Handler = 2#1
def MenuHandler(Events, WmInput, Pens):#Handler #1
	global BG, Sprites, Window, Timer, Text
	
	
	
	
	
	#Draw BG:
	Window.blit(BG[1], (0,0))
	
	#draw pointer:
	#for i in pens:
	#	pygame.draw.circle(Window, (255, 0, 255), i, 10, 0)
	
	#Refresh the Window:
	pygame.display.flip()
def DrawHandler(Events, WmInput, Pens):#Handler #2
	global BG, Sprites, ToolIcons, Window, Timer, Text
	global DrawTools, DrawingObj, PenVisible
	
	#Step Buttons:
	for i in DrawTools: i.Step(Events, WmInput, Pens)
	DrawingObj.Step(Events, WmInput, Pens)
	if "2" in WmInput:
		PenVisible = not PenVisible
	
	#Draw:
	Window.blit(BG[2], (0, 0))#BG
	for i in DrawTools:
		i.Draw(Window)#Buttons
	Window.blit(ToolIcons[0], (  4, 532))
	Window.blit(ToolIcons[1], ( 72, 532))
	Window.blit(ToolIcons[2], (140, 532))
	if len(DrawingObj.History) > 1:
		Window.blit(ToolIcons[3], (310, 532))
	else:
		Window.blit(ToolIcons[4], (310, 532))
	if len(DrawingObj.Future):
		Window.blit(ToolIcons[5], (378, 532))
	else:
		Window.blit(ToolIcons[6], (378, 532))
	Window.blit(ToolIcons[7], (446, 532))
	Window.blit(ToolIcons[8], (732, 532))
	if DrawingObj.Tool == 2:
		pygame.draw.circle(Window, (255, 255, 255), (241, 564), DrawingObj.Size*3, 0)
		pygame.draw.circle(Window, (0, 0, 0), (241, 564), DrawingObj.Size*3, 1)
	else:
		pygame.draw.circle(Window, DrawingObj.Color[:3], (241, 564), DrawingObj.Size*3, 0)
	DrawingObj.Draw(Window)
	
	#DEBUGGING:
	if PenVisible:
		for i in Pens:
			if i:
				pygame.draw.circle(Window, (255, 0, 255), i, 7, 0)# pointer(TEMP)
	
	#Refresh the Window:
	pygame.display.flip()

if __name__ == "__main__":
	MainLoop()
	
