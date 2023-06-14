import binascii,struct
try:
	import psyco
	psyco.full()
except ImportError:
	pass

#By pbsds
#No credit needed if you use this, but I'd be glad if you do. :)

def SwapEndian32bit(i):#Swaps Endian on a decimal value(32bit)
	return ((i & 0xFF)<<24) | (((i >> 8) & 0xFF) << 16) | (((i >> 16) & 0xFF) << 8) | ((i >> 24) & 0xFF)
def SwapEndian24bit(i):#Swaps Endian on a decimal value(24bit)
	return ((i & 0xFF) << 16) | (i & 0xFF00) | (i>>16 & 0xFF)
def SwapEndian16bit(i):#Swaps Endian on a decimal value(16bit)
	return (i >> 8 & 0xFF) | ((i & 0xFF)<<8)
def AddPadding(i,pad = 64):#Makes the value dividable by the choosen padding(The returned value will never be lower than the input) 
	if i % pad <> 0:
		i += pad - (i % pad)
	return i
def AscDec(ascii):#Converts a ascii string into a decimal(Big Endian)
	ret = 0
	for i in map(ord,ascii):
		ret = (ret<<8) | i
	return ret
def DecAsc(dec,pad = -1):#Converts a decimal into an ascii string with the needed padding(Big Endian)
	ret = ""
	while dec <> 0:
		ret = chr(dec&0xFF) + ret
		dec >>= 8
	if pad <> -1:
		if len(ret) > pad:
			ret = ret[:pad]
		if len(ret) < pad:
			ret = "\0"*(pad-len(ret)) + ret
	return ret
def AscFloat(Data):#Used for unpacking a ascii string into a float(Big Endian)
	return struct.unpack(">f", Data[:4])[0]
def FloatAsc(Float):#Used for packing a float into a ascii string(Big Endian)
	return struct.pack(">f", Float)
def HexAsc(hex):#converts a hex string into a ascii string
	ret = ""
	temp = ""
	if hex[:2] == "0x":
		hex = hex[2:]
	for letter in hex:
		temp += letter
		if len(temp) == 2:
			ret += binascii.a2b_hex(temp)
			temp = ""
	return ret
def AscHex(ascii):#Converts a ascii string to hex
	return hex(AscDec(ascii),len(ascii)*2)
def hex(dec,pad = -1):#A better and improved version. It's without the "L" at the end for long numbers and has support for padding(second parameter)
	ret = "%X" % dec
	if pad <> -1:
		if len(ret) > pad:
			ret = ret[:pad]
		if len(ret) < pad:
			for i in range(pad-len(ret)):
				ret = "0" + ret
	return "0x" + ret
def Abs(i):#makes the value positive if it's negative
	if i < 0: i = 0 - i
	return i
def Clamp(i, min, max):#Makes i be within the range of choise
	if i < min: i = min
	if i > max: i = max
	return i
def Min(i1,i2):#chooses the smallest value
	ret = i1
	if i2 < i1: ret = i2
	return ret
def Max(i1,i2):#chooses the biggest value
	ret = i1
	if i2 > i1: ret = i2
	return ret
def Average(I1,I2,A1,A2):
	I1 = float(I1)
	I2 = float(I2)
	return (I1*A1 + I2*A2) / (A1*A2)