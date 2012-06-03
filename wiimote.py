import cwiid, time, sys, pygame#, numpy
#from gaussion_elim import *
from perspective import Perspective

def blit_alpha(target, source, (x, y), alpha):
	temp = pygame.Surface((source.get_width(), source.get_height())).convert()
	temp.blit(target, (-x, -y))
	temp.blit(source, (0, 0))
	temp.set_alpha(alpha)
	target.blit(temp, (x, y))

class Wiimote:
	def __init__(self, LED = 1):#this will connect to the wiimote
		self.Buttons = {"a"		: [0x0008, 0],
						"b"		: [0x0004, 0],
						"up"	: [0x0800, 0],
						"down"	: [0x0400, 0],
						"left"	: [0x0100, 0],
						"right"	: [0x0200, 0],
						"+"		: [0x1000, 0],
						"-"		: [0x0010, 0],
						"home"	: [0x0080, 0],
						"1"		: [0x0002, 0],
						"2"		: [0x0001, 0]}
		
		#Connect to mote:
		self.wm = None
		for i in xrange(5):
			print "Connecting to wiimote...",
			try:
				self.wm = cwiid.Wiimote()
				print "Success!"
				break
			except RuntimeError:
				print "Failed..."
		if not self.wm:
			print "Could not connect to Wiimote, exiting..."
			sys.exit(0)
		self.wm.rpt_mode = cwiid.RPT_IR | cwiid.RPT_BTN#Report IR and buttons input
		self.wm.led = LED
		self.wm.rumble = 1
		time.sleep(0.2)
		self.wm.rumble = 0
		
		#IR calculation variables (glovepie):
		#self.r = (66, 776, 66, 776)
		#self.h = (534, 534, 66, 66)
		#self.m = None
		#self.bb = None
		
		#Perspective:
		self.callibrated = False
		self.perspective = Perspective()
		self.perspective.setdst((66.0, 66.0), (734.0, 66.0), (66.0, 534.0), (734.0, 534.0))
	def GetButtonInput(self):
		b = self.wm.state["buttons"]
		
		ret = []
		for i in self.Buttons:
			if self.Buttons[i][1] > 0:
				self.Buttons[i][1] -= 1
			if self.Buttons[i][0] & b:
				if self.Buttons[i][1] == 0:
					ret.append(i)
				self.Buttons[i][1] = 5
		return ret
	def CallibratePen(self, Window, Marker, Timer, Text):#Remember to make the "Finished" text blink!
		#Fade bg:
		bg = Window.convert()
		temp = pygame.Surface((800, 600))
		temp.fill((0,0,0))
		temp.set_alpha(100)
		bg.blit(temp, (0, 0))
		del temp
		
		#Create the box displaying the IR input:
		bg.lock()
		pygame.draw.rect(bg, pygame.Color(255, 255, 255, 255), (199,149,402,302))
		pygame.draw.rect(bg, pygame.Color(  0,   0,   0, 255), (200,150,400,300))
		bg.unlock()
		
		#Create the text which will be drawn:
		TitleT = Text.Create48("WiiMote callibration")
		HowT = Text.Create16("Press A or + on the WiiMote while pointing at the reticle with the pen")
		FinishedT = Text.Create32("Press 1 on the WiiMote to finish")
		FinishedAlpha = 0
		
		Edges = []
		while 1:
			#FPS:
			Timer.tick(60)
			
			#Input:
			Events = pygame.event.get()
			for i in Events:
				if i.type == pygame.QUIT:
					print "Exiting..."
					sys.exit(0)
				if i.type == pygame.KEYDOWN:
					if i.key == pygame.K_ESCAPE:
					  sys.exit(0)
			for i in self.GetButtonInput():
				if i in ("a", "+"):#Set point/edge:
					if len(Edges) < 4:
						temp = self.wm.state["ir_src"]
						if temp[0]:
							Edges.append((temp[0]["pos"][0], 768-temp[0]["pos"][1]))
							FinishedAlpha = 0
					continue
				if i == "-":#Remove point/edge:
					if Edges:
						Edges.pop(-1)
					continue
				if i == "1" and len(Edges) == 4:
					self.SetPenEdges(Edges)
					return
			
			#Draw bg:
			Window.blit(bg, (0,0))
			
			#Draw the edges/points set:
			for x, y in Edges:
				pygame.draw.circle(Window, (255, 0, 255), (200 + x*400/1024, 150 + y*300/768), 2, 0)
			
			#Draw lines between the edges/points:
			if len(Edges) >= 2:
				pygame.draw.line(Window, (255, 0, 0), (200 + Edges[0][0]*400/1024, 150 + Edges[0][1]*300/768), (200 + Edges[1][0]*400/1024, 150 + Edges[1][1]*300/768))
			if len(Edges) >= 3:
				pygame.draw.line(Window, (255, 0, 0), (200 + Edges[1][0]*400/1024, 150 + Edges[1][1]*300/768), (200 + Edges[2][0]*400/1024, 150 + Edges[2][1]*300/768))
			if len(Edges) >= 4:
				pygame.draw.line(Window, (255, 0, 0), (200 + Edges[2][0]*400/1024, 150 + Edges[2][1]*300/768), (200 + Edges[3][0]*400/1024, 150 + Edges[3][1]*300/768))
				pygame.draw.line(Window, (255, 0, 0), (200 + Edges[3][0]*400/1024, 150 + Edges[3][1]*300/768), (200 + Edges[0][0]*400/1024, 150 + Edges[0][1]*300/768))
				
			#Draw IR input:
			for i in self.wm.state["ir_src"]:
				if i:
					pygame.draw.circle(Window, (255, 255, 0), (200 + i["pos"][0]*400/1024, 150 + (768-i["pos"][1])*300/768), 2, 0)
			
			#Draw the reticle:
			if len(Edges) == 0:
				Window.blit(Marker, (42, 42))
			elif len(Edges) == 1:
				Window.blit(Marker, (710, 42))
			elif len(Edges) == 2:
				Window.blit(Marker, (710, 510))
			elif len(Edges) == 3:
				Window.blit(Marker, (42, 510))
			
			#Draw text:
			Window.blit(TitleT, (400- TitleT.get_width()/2, 8))
			Window.blit(HowT, (400- HowT.get_width()/2, 125))
			if len(Edges) == 4:
				FinishedAlpha += 4
				if FinishedAlpha > 510:
					FinishedAlpha -= 511
				if FinishedAlpha < 256:
					blit_alpha(Window, FinishedT, (400- FinishedT.get_width()/2, 460), FinishedAlpha)
				else:
					blit_alpha(Window, FinishedT, (400- FinishedT.get_width()/2, 460), 511-FinishedAlpha)
			
			#Update the window:
			pygame.display.flip()
	def SetPenEdges(self, ((x1, y1), (x2, y2), (x4, y4), (x3, y3))):
		#GlovePIE transelations:
		if 1 == 2: #numpy edition:
			self.m = numpy.array(  [[-1, -1, -1, -1,  0,  0,  0,  0],
									[x1, x2, x3, x4,  0,  0,  0,  0],
									[y1, y2, y3, y4,  0,  0,  0,  0],
									[ 0,  0,  0,  0, -1, -1, -1, -1],
									[ 0,  0,  0,  0, x1, x2, x3, x4],
									[ 0,  0,  0,  0, y1, y2, y3, y4],
									[x1*self.r[0], x2*self.r[1], x3*self.r[2], x4*self.r[3], x1*self.h[0], x2*self.h[1], x3*self.h[2], x4*self.h[3]],
									[y1*self.r[0], y2*self.r[1], y3*self.r[2], y4*self.r[3], y1*self.h[0], y2*self.h[1], y3*self.h[2], y4*self.h[3]]])
			
			#self.bb = numpy.array(list(self.r)+list(self.h))
			self.bb = numpy.array( [[self.r[0]],
									[self.r[1]],
									[self.r[2]],
									[self.r[3]],
									[self.h[0]],
									[self.h[1]],
									[self.h[2]],
									[self.h[3]]])
			
			#Gaussain elimination:
			self.m[1:8, 1] = -self.m[1:8, 1] + self.m[1:8, 1]
			self.bb[1] = -self.bb[1] + self.bb[0]
			self.m[0, 1] = 0
			
			self.m[1:8, 2] = -self.m[1:8, 2] + self.m[1:8, 1]
			self.bb[2] = -self.bb[2] + self.bb[0]
			self.m[0, 2] = 0
			
			self.m[1:8, 3] = -self.m[1:8, 3] + self.m[1:8, 1]
			self.bb[3] = -self.bb[3] + self.bb[0]
			self.m[0, 3] = 0
			
			self.m[2:8, 2] = -self.m[2:8, 2] / self.m[1, 2] * self.m[1, 1] + self.m[2:8, 1]
			self.bb[2] = -self.bb[2] / self.m[1, 2] * self.m[1, 1] + self.bb[1]
			self.m[1, 2] = 0
			
			self.m[2:8, 3] = -self.m[2:8, 3] / self.m[1, 3] * self.m[1, 1] + self.m[2:8, 1]
			self.bb[3] = -self.bb[3] / self.m[1, 3] * self.m[1, 1] + self.bb[1]
			self.m[1, 3] = 0
			
			self.m[3:8, 3] = -self.m[3:8, 3] / self.m[2, 3] * self.m[2, 2] + self.m[3:8, 2]
			self.bb[3] = -self.bb[4] / self.m[2, 3] * self.m[2, 2] + self.bb[2]
			self.m[2, 3] = 0
			
			self.m[4:8, 5] = -self.m[4:8, 5] + self.m[4:8, 4]
			self.bb[5] = -self.bb[5]+self.bb[4]
			self.m[3, 5] = 0
			
			self.m[4:8, 6] = -self.m[4:8, 6] + self.m[4:8, 4]
			self.bb[6] = -self.bb[6]+self.bb[4]
			self.m[3, 6] = 0
			
			self.m[4:8, 7] = -self.m[4:8, 7] + self.m[4:8, 4]
			self.bb[7] = -self.bb[7]+self.bb[4]
			self.m[3, 7] = 0
			
			self.m[5:8, 6] = -self.m[5:8, 6] / self.m[4, 6] * self.m[4, 5] + self.m[5:8, 5]
			self.bb[6] = -self.bb[6] / self.m[4, 6] * self.m[4, 5] + self.bb[5]
			self.m[4, 6] = 0
			
			self.m[5:8, 7] = -self.m[5:8, 7] / self.m[4, 7] * self.m[4, 5] + self.m[5:8, 5]
			self.bb[7] = -self.bb[7] / self.m[4, 7] * self.m[4, 5] + self.bb[5]
			self.m[4, 7] = 0
			
			self.m[6:8, 7] = -self.m[6:8, 7] / self.m[5, 7] * self.m[5, 6] + self.m[6:8, 6]
			self.bb[7] = -self.bb[7] / self.m[5, 7] * self.m[5, 6] + self.bb[6]
			self.m[5, 7] = 0
			
			self.m[7, 7] = self.m[7, 7] / self.m[6, 7] * self.m[6, 3] + self.m[7, 3]
			self.bb[7] = self.bb[7] / self.m[6, 7] * self.m[6, 3] + self.bb[3]
			self.m[6, 7] = 0
			
			#debug:
			print self.m
			print self.bb
			
			#The 8 calculations for the 8 parameters:
			self.b3 = self.bb[7]/self.m[7, 7]
			self.a3 = (self.bb[3]-(self.m[7, 3]*self.b3))/self.m[6, 3]
			self.b2 = (self.bb[6]-(self.m[7, 6]*self.b3 + self.m[6, 6]*self.a3))/self.m[5, 6]
			self.a2 = (self.bb[5]-(self.m[7, 5]*self.b3 + self.m[6, 5]*self.a3 + self.m[5, 5]*self.b2))/self.m[4, 5]
			self.c2 = (self.bb[4]-(self.m[7, 4]*self.b3 + self.m[6, 4]*self.a3 + self.m[5, 4]*self.b2 + self.m[4, 4]*self.a2))/self.m[3, 4]
			
			self.b1 = (self.bb[2]-(self.m[7, 2]*self.b3 + self.m[6, 2]*self.a3 + self.m[5, 2]*self.b2 + self.m[4, 2]*self.a2 + self.m[3, 2]*self.c2))/self.m[2, 2]
			self.a1 = (self.bb[1]-(self.m[7, 1]*self.b3 + self.m[6, 1]*self.a3 + self.m[5, 1]*self.b2 + self.m[4, 1]*self.a2 + self.m[3, 1]*self.c2 + self.m[2, 1]*self.b1))/self.m[1, 1]
			self.c1 = (self.bb[0]-(self.m[7, 0]*self.b3 + self.m[6, 0]*self.a3 + self.m[5, 0]*self.b2 + self.m[4, 0]*self.a2 + self.m[3, 0]*self.c2 + self.m[2, 0]*self.b1 + self.m[1, 0]*self.a1))/self.m[0, 0]
			
			#debug:
			print self.a1
			print self.a2
			print self.a3
			print self.b1
			print self.b2
			print self.b3
			print self.c1
			print self.c2
		if 1 == 2:#Vanilla python:
			x1 = float(x1)/1024
			x2 = float(x2)/1024
			x3 = float(x3)/1024
			x4 = float(x4)/1024
			y1 = float(768-y1)/768
			y2 = float(768-y2)/768
			y3 = float(768-y3)/768
			y4 = float(768-y4)/768
			self.m=[[-1, -1, -1, -1,  0,  0,  0,  0],
					[x1, x2, x3, x4,  0,  0,  0,  0],
					[y1, y2, y3, y4,  0,  0,  0,  0],
					[ 0,  0,  0,  0, -1, -1, -1, -1],
					[ 0,  0,  0,  0, x1, x2, x3, x4],
					[ 0,  0,  0,  0, y1, y2, y3, y4],
					[x1*self.r[0], x2*self.r[1], x3*self.r[2], x4*self.r[3], x1*self.h[0], x2*self.h[1], x3*self.h[2], x4*self.h[3]],
					[y1*self.r[0], y2*self.r[1], y3*self.r[2], y4*self.r[3], y1*self.h[0], y2*self.h[1], y3*self.h[2], y4*self.h[3]]]
			self.bb = list(self.r)+list(self.h)
			
			#Convert ot float:
			for x in xrange(8):
				self.bb[x] = float(self.bb[x])
				for y in xrange(8):
					self.m[x][y] = float(self.m[x][y])
			
			#Gaussian elemination:
			self.m[1][1] = -self.m[1][1] + self.m[1][0]
			self.m[2][1] = -self.m[2][1] + self.m[2][0]
			self.m[3][1] = -self.m[3][1] + self.m[3][0]
			self.m[4][1] = -self.m[4][1] + self.m[4][0]
			self.m[5][1] = -self.m[5][1] + self.m[5][0]
			self.m[6][1] = -self.m[6][1] + self.m[6][0]
			self.m[7][1] = -self.m[7][1] + self.m[7][0]
			self.bb[1] = -self.bb[1] + self.bb[0]
			self.m[0][1] = 0.0
			
			self.m[1][2] = -self.m[1][2] + self.m[1][0]
			self.m[2][2] = -self.m[2][2] + self.m[2][0]
			self.m[3][2] = -self.m[3][2] + self.m[3][0]
			self.m[4][2] = -self.m[4][2] + self.m[4][0]
			self.m[5][2] = -self.m[5][2] + self.m[5][0]
			self.m[6][2] = -self.m[6][2] + self.m[6][0]
			self.m[7][2] = -self.m[7][2] + self.m[7][0]
			self.bb[2] = -self.bb[2] + self.bb[0]
			self.m[0][2] = 0.0
			
			self.m[1][3] = -self.m[1][3] + self.m[1][0]
			self.m[2][3] = -self.m[2][3] + self.m[2][0]
			self.m[3][3] = -self.m[3][3] + self.m[3][0]
			self.m[4][3] = -self.m[4][3] + self.m[4][0]
			self.m[5][3] = -self.m[5][3] + self.m[5][0]
			self.m[6][3] = -self.m[6][3] + self.m[6][0]
			self.m[7][3] = -self.m[7][3] + self.m[7][0]
			self.bb[3] = -self.bb[3] + self.bb[0]
			self.m[0][3] = 0.0
			
			self.m[2][2] = -self.m[2][2] / self.m[1][2] * self.m[1][1] + self.m[2][1]
			self.m[3][2] = -self.m[3][2] / self.m[1][2] * self.m[1][1] + self.m[3][1]
			self.m[4][2] = -self.m[4][2] / self.m[1][2] * self.m[1][1] + self.m[4][1]
			self.m[5][2] = -self.m[5][2] / self.m[1][2] * self.m[1][1] + self.m[5][1]
			self.m[6][2] = -self.m[6][2] / self.m[1][2] * self.m[1][1] + self.m[6][1]
			self.m[7][2] = -self.m[7][2] / self.m[1][2] * self.m[1][1] + self.m[7][1]
			self.bb[2] = -self.bb[2] / self.m[1][2] * self.m[1][1] + self.bb[1]
			self.m[1][2] = 0.0
			
			self.m[2][3] = -self.m[2][3] / self.m[1][3] * self.m[1][1] + self.m[2][1]
			self.m[3][3] = -self.m[3][3] / self.m[1][3] * self.m[1][1] + self.m[3][1]
			self.m[4][3] = -self.m[4][3] / self.m[1][3] * self.m[1][1] + self.m[4][1]
			self.m[5][3] = -self.m[5][3] / self.m[1][3] * self.m[1][1] + self.m[5][1]
			self.m[6][3] = -self.m[6][3] / self.m[1][3] * self.m[1][1] + self.m[6][1]
			self.m[7][3] = -self.m[7][3] / self.m[1][3] * self.m[1][1] + self.m[7][1]
			self.bb[3] = -self.bb[3] / self.m[1][3] * self.m[1][1] + self.bb[1]
			self.m[1][3] = 0.0
			
			self.m[3][3] = -self.m[3][3] / self.m[2][3] * self.m[2][2] + self.m[3][2]
			self.m[4][3] = -self.m[4][3] / self.m[2][3] * self.m[2][2] + self.m[4][2]
			self.m[5][3] = -self.m[5][3] / self.m[2][3] * self.m[2][2] + self.m[5][2]
			self.m[6][3] = -self.m[6][3] / self.m[2][3] * self.m[2][2] + self.m[6][2]
			self.m[7][3] = -self.m[7][3] / self.m[2][3] * self.m[2][2] + self.m[7][2]
			self.bb[3] = -self.bb[3] / self.m[2][3] * self.m[2][2] + self.bb[2]
			self.m[2][3] = 0.0
			
			self.m[4][5] = -self.m[4][5] + self.m[4][4]
			self.m[5][5] = -self.m[5][5] + self.m[5][4]
			self.m[6][5] = -self.m[6][5] + self.m[6][4]
			self.m[7][5] = -self.m[7][5] + self.m[7][4]
			self.bb[5] = -self.bb[5] + self.bb[4]
			self.m[3][5] = 0.0
			
			self.m[4][6] = -self.m[4][6] + self.m[4][4]
			self.m[5][6] = -self.m[5][6] + self.m[5][4]
			self.m[6][6] = -self.m[6][6] + self.m[6][4]
			self.m[7][6] = -self.m[7][6] + self.m[7][4]
			self.bb[6] = -self.bb[6] + self.bb[4]
			self.m[3][6] = 0.0
			
			self.m[4][7] = -self.m[4][7] + self.m[4][4]
			self.m[5][7] = -self.m[5][7] + self.m[5][4]
			self.m[6][7] = -self.m[6][7] + self.m[6][4]
			self.m[7][7] = -self.m[7][7] + self.m[7][4]
			self.bb[7] = -self.bb[7] + self.bb[4]
			self.m[3][7] = 0.0
			
			self.m[5][6] = -self.m[5][6] / self.m[4][6] * self.m[4][5] + self.m[5][5]
			self.m[6][6] = -self.m[6][6] / self.m[4][6] * self.m[4][5] + self.m[6][5]
			self.m[7][6] = -self.m[7][6] / self.m[4][6] * self.m[4][5] + self.m[7][5]
			self.bb[6] = -self.bb[6] / self.m[4][6] * self.m[4][5] + self.bb[5]
			self.m[4][6] = 0.0
			
			self.m[5][7] = -self.m[5][7] / self.m[4][7] * self.m[4][5] + self.m[5][5]
			self.m[6][7] = -self.m[6][7] / self.m[4][7] * self.m[4][5] + self.m[6][5]
			self.m[7][7] = -self.m[7][7] / self.m[4][7] * self.m[4][5] + self.m[7][5]
			self.bb[7] = -self.bb[7] / self.m[4][7] * self.m[4][5] + self.bb[5]
			self.m[4][7] = 0.0
			
			self.m[6][7] = -self.m[6][7] / self.m[5][7] * self.m[5][6] + self.m[6][6]
			self.m[7][7] = -self.m[7][7] / self.m[5][7] * self.m[5][6] + self.m[7][6]
			self.bb[7] = -self.bb[7] / self.m[5][7] * self.m[5][6] + self.bb[6]
			self.m[5][7] = 0.0
			
			self.m[7][7] = -self.m[7][7] / self.m[6][7] * self.m[6][3] + self.m[7][3]
			self.bb[7] = -self.bb[7] / self.m[6][7] * self.m[6][3] + self.bb[3]
			self.m[6][7] = 0.0
			
			#The 8 calculations for the 8 parameters
			self.b3 = self.bb[7]/self.m[7][7]
			self.a3 = (self.bb[3] - (self.m[7][3] * self.b3)) / self.m[6][3]
			self.b2 = (self.bb[6] - (self.m[7][6] * self.b3 + self.m[6][6] * self.a3)) / self.m[5][6]
			self.a2 = (self.bb[5] - (self.m[7][5] * self.b3 + self.m[6][5] * self.a3 + self.m[5][5] * self.b2)) / self.m[4][5]
			self.c2 = (self.bb[4] - (self.m[7][4] * self.b3 + self.m[6][4] * self.a3 + self.m[5][4] * self.b2 + self.m[4][4] * self.a2)) / self.m[3][4]

			self.b1 = (self.bb[2] - (self.m[7][2] * self.b3 + self.m[6][2] * self.a3 + self.m[5][2] * self.b2 + self.m[4][2] * self.a2 + self.m[3][2] * self.c2)) / self.m[2][2]
			self.a1 = (self.bb[1] - (self.m[7][1] * self.b3 + self.m[6][1] * self.a3 + self.m[5][1] * self.b2 + self.m[4][1] * self.a2 + self.m[3][1] * self.c2 + self.m[2][1] * self.b1)) / self.m[1][1]
			self.c1 = (self.bb[0] - (self.m[7][0] * self.b3 + self.m[6][0] * self.a3 + self.m[5][0] * self.b2 + self.m[4][0] * self.a2 + self.m[3][0] * self.c2 + self.m[2][0] * self.b1 + self.m[1][0] * self.a1)) / self.m[0][0]
		
		#Borrowed edition:
		self.perspective.setsrc((x1, y1), (x2, y2), (x3, y3), (x4, y4))
		self.callibrated = True
	def CalculatePenPosition(self):#Will crash when edges arent set!
		#old:
		if 1 == 2:
			if self.m == None: return []
			
			ret = []
			for i in self.wm.state["ir_src"]:
				if not i: continue
				#wx, wy = i["pos"][0], 768-i["pos"][1]
				wx, wy = float(i["pos"][0])/1024, float(i["pos"][1])/768
				x = (self.a1*wx + self.b1*wy + self.c1) / (self.a3*wx + self.b3*wy + 1)
				y = (self.a2*wx + self.b2*wy + self.c2) / (self.a3*wx + self.b3*wy + 1)
				ret.append((int(x), 600-int(y)))
			
			return ret
		
		#new:
		if not self.callibrated: return [None, None, None, None]
		
		ret = []
		for i in self.wm.state["ir_src"]:
			if not i:
				ret.append(None)
			else:
				ret.append(map(int, self.perspective.warp(i["pos"][0], 768-i["pos"][1])))
		
		return ret
