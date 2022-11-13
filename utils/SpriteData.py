
class SpriteData:
	def __init__(self, file, scale=1, x_offset=0, y_offset=0):
		self.file = file
		self.scale = scale
		self.x_offset = x_offset
		self.y_offset = y_offset
	# def __getstate__(self):
	# 	return [self.file, self.scale, self.x_offset, self.y_offset]
	# def __setstate__(self, data):
	# 	self.file = data[0]
	# 	self.scale=data[1]
	# 	self.x_offset=data[2]
	# 	self.y_offset = data[3]