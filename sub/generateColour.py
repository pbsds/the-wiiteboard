import Picture, colorsys, math

out = Picture.Picture(201, 201, 0xFFFFFFFF)

def PointDistance((x, y), (x2, y2)):
	return math.sqrt((x2-x)*(x2-x) + (y2-y)*(y2-y))
def LengthDir(Dir, Len):
	return ( math.sin(float(Dir)/180*math.pi) * Len,
			-math.cos(float(Dir)/180*math.pi) * Len)
def PointDirection((x, y), (x2, y2)):
	return math.atan2(y-y2, x2-x)/math.pi*180

def OpenGLToRGBA(l):
	l[0] *= 255
	l[1] *= 255
	l[2] *= 255
	l = map(int, l)
	return (l[0]<<24) | (l[1] << 16) | (l[2] << 8) | 0xFF

for x in xrange(201):
	for y in xrange(201):
		S = PointDistance((100, 100), (x, y))
		if S < 100.0:
			S /= 100.0
			H = PointDirection((100, 100), (x, y))
			if H < 0.0: H += 360.0
			if H >= 360.0: H -= 360.0
			H /= 360.0
			out.SetPixel(x, y, OpenGLToRGBA(list(colorsys.hsv_to_rgb(H, S, 1.0))))

out.ToFile("out.png")
