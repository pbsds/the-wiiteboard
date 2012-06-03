import sys, pygame
import wiimote

wm = wiimote.Wiimote()

print "Initalizing pygame..."
pygame.init()
pygame.display.set_caption("WiiMote test - pbsds")
Window = pygame.display.set_mode((1024,768))
Timer = pygame.time.Clock()

while 1:
	#FPS:
	Timer.tick(60)
	
	#Draw:
	Window.fill((0,0,0))
	
	for i in wm.wm.state["ir_src"]:
		if i:
			pygame.draw.circle(Window, (255, 255, 0), i["pos"], 4*int(i["size"]), 0)
	#print "Buttons:", hex(wm.wm.state["buttons"])[2:]
	
	#Update window:
	pygame.display.flip()
	
	#Check buttons:
	for i in pygame.event.get():
		#Keyboard buttons:
		if i.type == pygame.QUIT:
			sys.exit(0)
