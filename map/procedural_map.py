#from map.map import Map
from LAUNCH_SETUP import LAUNCH_SAFEWAY_SAND
#from map.defaultmap import default_map_2d
import noise
import numpy as np
from utils.vector import Vector

################################
# 1 generation de perlin noise #
################################
# def perlin_array(size = (50, 50),
# 			scale=21, octaves = 50,
# 			persistence = 0.1,
# 			lacunarity = 2,
# 			seed = None):

# 	if not seed:

# 		seed = np.random.randint(0, 100)
# 		print("seed was {}".format(seed))

# 	arr = np.zeros(size)
# 	for i in range(size[0]):
# 		for j in range(size[1]):
# 			arr[i][j] = noise.pnoise2(i / scale,
# 										j / scale,
# 										octaves=octaves,
# 										persistence=persistence,
# 										lacunarity=lacunarity,
# 										repeatx=1024,
# 										repeaty=1024,
# 										base=seed)
# 	max_arr = np.max(arr)
# 	min_arr = np.min(arr)
# 	norm_me = lambda x: (x-min_arr)/(max_arr - min_arr)
# 	norm_me = np.vectorize(norm_me)
# 	arr = norm_me(arr)
# 	#print(arr)
# 	return arr

#perlin_array(seed=61)

# def process_array(array, size = (50,50)):
# 	#baseTile = Tile("grass", 0,0,None)
# 	out = [[0 for y in range(size[1])] for x in range(size[0])]
# 	for x in range(size[0]):
# 		for y in range(size[1]):
# 			if array[x][y] < 0.18:
# 				#layer2=Stone(Vector(x,y))
# 				out[x][y] = Tile("grass", Vector(x, y))
# 			elif array[x][y] < 0.287:
# 				#layer2=Stone(Vector(x,y))
# 				out[x][y] = Tile("grass", Vector(x, y))
# 			elif array[x][y] < 0.315:
# 				#layer2=Stone(Vector(x,y))
# 				out[x][y] = Tile("grass", Vector(x, y))
# 			elif array[x][y] < 0.32:
# 				out[x][y] = Tile("grass", Vector(x, y),"stone")
# 			elif array[x][y] < 0.45:
# 				out[x][y] = Tile("grass", Vector(x, y))
# 			elif array[x][y] < 0.47:
# 				out[x][y] = Tile("grass", Vector(x, y),"tree")
# 			elif array[x][y] < 0.578:
# 				#layer2=Wood(Vector(x,y))
# 				out[x][y] = Tile("grass", Vector(x, y))
# 			elif array[x][y] < 0.58:
# 				#layer2=Wood(Vector(x,y))
# 				out[x][y] = Tile("grass", Vector(x, y),"gold")
# 			elif array[x][y] < 0.65:
# 				#layer2=Wood(Vector(x,y))
# 				out[x][y] = Tile("grass", Vector(x, y))
# 			elif array[x][y] < 0.75:
# 				#layer2=Gold(Vector(x,y))
# 				out[x][y] = Tile("sand", Vector(x, y))
# 			elif array[x][y] < 0.755:
# 				#layer2=Gold(Vector(x,y))
# 				out[x][y] = Tile("sand", Vector(x, y),"gold")
# 			else:
# 				out[x][y] = Tile("water", Vector(x, y))

# 	#genere la sprite
# 	for x in range(size[0]):
# 		for y in range(size[1]):
# 			out[x][y].init_sprite()

# 	return out

#########################################
# plusieurs generations de perlin noise #
#########################################
def perlin_array2(size = (50, 50),
			scale=21, octaves = 50,
			persistence = 0.1,
			lacunarity = 2,
			seed = None):

	if not seed:
		seed = np.random.randint(0, 100)
		print("seed was {}".format(seed))

	arr = np.zeros(size)
	for i in range(size[0]):
		for j in range(size[1]):
			arr[i][j] = noise.pnoise2(i / scale,
										j / scale,
										octaves=octaves,
										persistence=persistence,
										lacunarity=lacunarity,
										repeatx=1024,
										repeaty=1024,
										base=seed)
	max_arr = np.max(arr)
	min_arr = np.min(arr)
	norm_me = lambda x: (x-min_arr)/(max_arr - min_arr)
	norm_me = np.vectorize(norm_me)
	arr = norm_me(arr)
	return arr

def reserve_towncenter(out, position, zone_size, spawn_id, text_pos, map_size=(100,100)):
	for a in range(position.x, position.x + zone_size):
		for b in range(position.y, position.y + zone_size):
			out[a][b]["tile"] = "grass"
			out[a][b]["obj"] = None

	out[position.x + 1][position.y + 1]["obj"] = f"spawn_{spawn_id}"

	for a in range(position.x - 1, position.x + zone_size + 2, zone_size + 1):
		for b in range(position.y - 1, position.y + zone_size + 2, zone_size + 1):
			out[a][b]["tile"] = "grass"
			out[a][b]["obj"] = "berry"

	tile_type = "sand" if LAUNCH_SAFEWAY_SAND else "grass"

	if text_pos == "bottom":
		for diag in range(0, 40):
			out[position.x + diag][position.y + diag]["tile"] = tile_type

			out[position.x + diag + 1][position.y + diag]["tile"] = tile_type
			out[position.x + diag + 2][position.y + diag]["tile"] = tile_type

			out[position.x + diag][position.y + diag + 1]["tile"] = tile_type
			out[position.x + diag][position.y + diag + 2]["tile"] = tile_type

	elif text_pos == "top":
		for diag in range(0, 40):
			out[position.x - diag][position.y - diag]["tile"] = tile_type

			out[position.x - diag - 1][position.y - diag]["tile"] = tile_type
			out[position.x - diag - 2][position.y - diag]["tile"] = tile_type

			out[position.x - diag][position.y - diag - 1]["tile"] = tile_type
			out[position.x - diag][position.y - diag - 2]["tile"] = tile_type

	elif text_pos == "left":
		for diag in range(0, 40):
			out[position.x + diag][position.y - diag]["tile"] = tile_type

			out[position.x + diag + 1][position.y - diag]["tile"] = tile_type
			out[position.x + diag + 2][position.y - diag]["tile"] = tile_type

			out[position.x + diag][position.y - diag - 1]["tile"] = tile_type
			out[position.x + diag][position.y - diag - 2]["tile"] = tile_type

	elif text_pos == "right":
		for diag in range(0, 40):
			out[position.x - diag][position.y + diag]["tile"] = tile_type

			out[position.x - diag - 1][position.y + diag]["tile"] = tile_type
			out[position.x - diag - 2][position.y + diag]["tile"] = tile_type

			out[position.x - diag][position.y + diag + 1]["tile"] = tile_type
			out[position.x - diag][position.y + diag + 2]["tile"] = tile_type

def process_array2(size = (50,50), seed=None, nbr_players=1):
	# baseTile = Tile("grass", 0,0,None)
	# default => grass everywhere
	out = [[{"tile": "grass", "obj": None} for y in range(size[1])] for x in range(size[0])]
	if seed is None:
		seed = np.random.randint(0, 100)
		print("seed was {}".format(seed))

	# layer 1 => ground
	array = perlin_array2(size=size, seed=seed)
	for x in range(size[0]):
		for y in range(size[1]):
			if array[x][y] < 0.67:
				#grass by default
				pass
			elif array[x][y] < 0.75:
				out[x][y]["tile"] = "sand"
			else:
				out[x][y]["tile"] = "water"

	# layer 2 => ressources
	#trees
	seed = (seed+5)%100
	array = perlin_array2(size=size, seed=seed, octaves=20, scale=8)
	for x in range(size[0]):
		for y in range(size[1]):
			if array[x][y] > 0.75 and out[x][y]["tile"] != "water":
				out[x][y]["obj"] = "tree"

	#gold
	seed = (seed+5)%100
	array = perlin_array2(size=size, seed=seed, octaves=20, scale=4)
	for x in range(size[0]):
		for y in range(size[1]):
			if array[x][y] > 0.87 and out[x][y]["tile"] != "water":
				out[x][y]["obj"]= "gold"

	#stone
	seed = (seed+5)%100
	array = perlin_array2(size=size, seed=seed, octaves=20, scale=4)
	for x in range(size[0]):
		for y in range(size[1]):
			if array[x][y] > 0.89 and out[x][y]["tile"] != "water":
				out[x][y]["obj"]= "stone"

	zoneSize=6

	if nbr_players > 0:
		reserve_towncenter(out, Vector(10, 10), zoneSize, 0, text_pos="bottom")
	if nbr_players > 1:
		reserve_towncenter(out, Vector(size[0] - 10, size[1] - 10), zoneSize, 1, text_pos="top")
	if nbr_players > 2:
		reserve_towncenter(out, Vector(10, size[1] - 10), zoneSize, 2, text_pos="left")
	if nbr_players > 3:
		reserve_towncenter(out, Vector(size[0] - 10, 10), zoneSize, 3, text_pos="right")

	return out


#a = process_array(perlin_array())
#print(a)


# tileArray = [[Tile("grass",x,y,None) for y in range(50)] for x in range(50)]
# print(tileArray)

# for x in range(50):
#     for y in range(50):
#         noise.pnoise2(x/scale, y/scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=1024, repeaty=1024, base=seed)

#         tileArray[x][y]=Tile()
