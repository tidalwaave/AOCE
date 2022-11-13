# Imports

import time

from arcade import clamp
from map.tile import Tile
from entity.Zone import Wood, Stone, Gold, BerryBush
from map.defaultmap import default_map_2d, default_map_objects_2d
from utils.isometric import iso_to_grid_pos
from utils.vector import Vector
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# --- Constants ---
CHARACTER_SCALING = 1

class Map():
	def __init__(self, tiles, objects, map_size):
		self.tiles = tiles
		self.objects = objects

		self.map_size = map_size
		self.tile_array = []
		self.objects_array = []
		self.spawn_array = []


	def reset(self):
		self.tile_array.clear()
		self.objects_array.clear()
		self.spawn_array.clear()


	def setup(self, tile_array):
		# self.tile_array = [[Tile("grass",x,y,None) for y in range(map_size)] for x in range(map_size)]

		self.reset()

		if tile_array is None:
			self.tile_array = [[Tile(default_map_2d[grid_x][grid_y], Vector(grid_x, grid_y)) for grid_y in range(self.map_size)] for grid_x in range(self.map_size)]
		else:
			self.tile_array = [[Tile(tile_array[x][y]["tile"], Vector(x,y), tile_array[x][y]["obj"]) for y in range(self.map_size)] for x in range(self.map_size)]

		self.objects_array = [[None for y in range(self.map_size)] for x in range(self.map_size)]
		for x in range(self.map_size):
			for y in range(self.map_size):
				object = default_map_objects_2d[x][y] if tile_array is None else self.tile_array[x][y].pointer_to_entity
				if tile_array is None:
					self.tile_array[x][y].pointer_to_entity = object

				if object == "tree":  # Can't use match for now, not compatible with arcade library...
					self.objects_array[x][y] = Wood(Vector(x, y))

				elif object == "stone":
					self.objects_array[x][y] = Stone(Vector(x, y))

				elif object == "gold":
					self.objects_array[x][y] = Gold(Vector(x, y))

				elif object == "berry":
					self.objects_array[x][y] = BerryBush(Vector(x, y))

				elif object is not None and "spawn" in object:
					self.spawn_array.append((Vector(x, y), object.split("_")[1]))

				if self.objects_array[x][y]: # and self.objects_array[x][y].is_locking:
					self.tile_array[x][y].is_free = 0

		self.update_tile_list()

	def update_tile_list(self):
		# self.view.ground_list.clear()  # Do not do this. clear doesn't exist for Arcade.SpriteList().
		for x in range(self.map_size-1,-1, -1):
			for y in range(self.map_size-1,-1, -1):
				self.tiles.append(self.tile_array[x][y])
				if self.objects_array[x][y]:
					self.objects.append(self.objects_array[x][y])

	def is_on_map(self, grid_position):
		return grid_position.x >= 0 and grid_position.x < self.map_size and grid_position.y >= 0 and grid_position.y < self.map_size

	def is_area_on_map(self, grid_position, tile_size):
		return all(self.is_on_map(grid_position + Vector(x, y)) for x in range(tile_size[0]) for y in range(tile_size[1]))

	def get_pathfinding_matrix(self):  # @kenzo6c: The pathfinding_matrix has to be created on the fly, otherwise it won't change if the map changes
		# @tidalwaave, 19/12, 23h50 : Time to replace the movements methods, fit 'em in tiles
		# Swapping x and y here, because of the library implementation
		return [[self.tile_array[x][y].is_free for x in range(self.map_size)] for y in range(self.map_size)]

	def get_restricted_pathfinding_matrix(self, start, end):
		start_node_pos = Vector()
		end_node_pos = Vector()
		if start.x < end.x:
			left = start.x
			right = end.x
			start_node_pos += Vector(0,0)
			end_node_pos += Vector(right - left, 0)
		else:
			left = end.x
			right = start.x
			start_node_pos += Vector(right - left, 0)
			end_node_pos += Vector(0, 0)

		if start.y < end.y:
			bottom = start.y
			top = end.y
			start_node_pos += Vector(0,0)
			end_node_pos += Vector(0, top - bottom)
		else:
			bottom = end.y
			top = start.y
			start_node_pos += Vector(0, top - bottom)
			end_node_pos += Vector(0, 0)


		bottom = start.y if start.y < end.y else end.y
		top = end.y if start.y < end.y else start.y

		return left, bottom, start_node_pos, end_node_pos, [[self.tile_array[x][y].is_free for x in range(left, right+1)] for y in range(bottom, top+1)]

	def get_path_fast(self, start:Vector, end:Vector):
		# Pathfinding algorithm
		path = []
		new_path = []
		path_len = -1
		if start != end:
			left_offset, bottom_offset, start_pos, end_pos, pathfinding_matrix = self.get_restricted_pathfinding_matrix(start, end)
			grid = Grid(matrix=pathfinding_matrix)
			# DEBUG_start = time.time()
			finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
			# print(f"time: {time.time() - DEBUG_start}")
			start_node = grid.node(*start_pos)
			end_node = grid.node(*end_pos)
			path, runs = finder.find_path(start_node, end_node, grid)

			new_path = [(pos[0] + left_offset, pos[1] + bottom_offset) for pos in path]

			# c_path, c_path_len = self.get_path(start, end)
			# print(path, new_path, c_path)

			if new_path:
				new_path.pop(0)
				path_len = len(new_path)
		else:
			path_len = 0

		# path_len == -1 : means end is inacessible
		# path_len == 0 : means start == end
		# path_len > 0 : means there is a path between start and end.
		return new_path, path_len

	def get_path(self, start, end):
		# Pathfinding algorithm
		path = []
		path_len = -1
		if start != end:
			pathfinding_matrix = self.get_pathfinding_matrix()
			grid = Grid(matrix=pathfinding_matrix)
			# DEBUG_start = time.time()
			finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
			# print(f"time: {time.time() - DEBUG_start}")
			start = grid.node(*start)
			end = grid.node(*end)
			path, runs = finder.find_path(start, end, grid)

			if path:
				path.pop(0)
				path_len = len(path)
		else:
			path_len = 0

		# path_len == -1 : means end is inacessible
		# path_len == 0 : means start == end
		# path_len > 0 : means there is a path between start and end.
		return path, path_len

	def is_area_buildable(self, map_position, tile_size):
		for i in range(tile_size[0]):
			for j in range(tile_size[1]):
				new_position = map_position + Vector(i, j)
				if self.is_on_map(new_position):
					tile = self.get_tile_at(new_position)
					if not tile.is_empty():
						return False
					if tile.build_guard:
						return False
		return True

	def get_tile_at(self, map_position):
		return self.tile_array[map_position.x][map_position.y]

	def get_tiles_nearby(self, map_position):
		return tuple(self.tile_array[clamp(map_position.x + i, 0, self.map_size - 1)][clamp(map_position.y + j, 0, self.map_size - 1)] for i in range(-1, 2) for j in range(-1, 2))

	def get_closest_tile_nearby_fast(self, start_position, aim_grid_pos):
		aimed_tile = None
		min_dist = self.map_size**2  # Value that shouldn't be reached when searching a path through the map.
		for tile in self.get_tiles_nearby(aim_grid_pos):
			if tile.is_free:
				dist = (tile.grid_position - start_position).norm()

				if dist > 0 and min_dist > dist:
					aimed_tile = tile
					min_dist = dist
				elif dist == 0:
					return tile
		return aimed_tile

	# def get_closest_tile_nearby(self, start_position, aim_grid_pos):
	# 	aimed_tile = None
	# 	min_path_len = self.map_size**2  # Value that shouldn't be reached when searching a path through the map.
	# 	for tile in self.get_tiles_nearby(aim_grid_pos):
	# 		path, path_len = self.get_path(start_position, tile.grid_position)

	# 		if path_len > 0 and min_path_len > path_len:
	# 			aimed_tile = tile
	# 			min_path_len = path_len
	# 		elif path_len == 0:
	# 			return tile
	# 	return aimed_tile

	def get_tiles_nearby_collection(self, collection):
		return tuple((tile, element) for element in collection for i in range(-1, 2) for j in range(-1, 2) if (tile := self.tile_array[clamp(element.grid_position.x + i, 0, self.map_size - 1)][clamp(element.grid_position.y + j, 0, self.map_size - 1)]).is_empty())

	def get_closest_tile_nearby_collection_fast(self, start_position, collection):
		aimed_tile = None
		aimed_element = None
		min_dist = self.map_size**2  # Value that shouldn't be reached when searching a path through the map.
		for tile_element in self.get_tiles_nearby_collection(collection):
			# Beaucoup trop long : fait freeze le jeu. -> Solution possible : faire un calcul direct sur la distance.
			tile, element = tile_element
			dist = (tile.grid_position - start_position).norm()

			if dist > 0 and min_dist > dist:
				aimed_tile = tile
				aimed_element = element
				min_dist = dist
			elif dist == 0:
				return tile, element
		return aimed_tile, aimed_element

	# def get_closest_tile_nearby_collection(self, start_position, collection):
	# 	aimed_tile = None
	# 	aimed_element = None
	# 	min_path_len = self.map_size**2  # Value that shouldn't be reached when searching a path through the map.
	# 	for tile_element in self.get_tiles_nearby_collection(collection):
	# 		# Beaucoup trop long : fait freeze le jeu. -> Solution possible : faire un calcul direct sur la distance.
	# 		tile, element = tile_element
	# 		path, path_len = self.get_path(start_position, tile.grid_position)

	# 		if path_len > 0 and min_path_len > path_len:
	# 			aimed_tile = tile
	# 			aimed_element = element
	# 			min_path_len = path_len
	# 		elif path_len == 0:
	# 			return tile, element
	# 	return aimed_tile, aimed_element

	def free_tile_at(self, map_position, tile_size):
		for x in range(map_position.x, map_position.x + tile_size[0]):
			for y in range(map_position.y, map_position.y + tile_size[1]):
				if self.objects_array[x][y] is not None:
					self.objects_array[x][y] = None
				if self.tile_array[x][y].pointer_to_entity is not None:
					self.tile_array[x][y].pointer_to_entity = None
				self.tile_array[x][y].is_free = 1

	def add_entity_to_pos(self, entity):
		self.tile_array[entity.grid_position.x][entity.grid_position.y].pointer_to_entity = entity

	def reserve_tile_at(self, map_position, tile_size):
		for x in range(map_position.x, map_position.x + tile_size[0]):
			for y in range(map_position.y, map_position.y + tile_size[1]):
				self.tile_array[x][y].is_free = 0

	def set_build_guard(self, map_position):
		self.tile_array[map_position.x][map_position.y].build_guard = True

	def remove_build_guard(self, map_position):
		self.tile_array[map_position.x][map_position.y].build_guard = False

####################################################################
#
##
### @tidalwaave : trying to add Zones to map
##
#
	def updateZoneLayer(self):
		pass
