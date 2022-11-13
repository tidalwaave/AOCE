# --- Imports ---
from utils.vector import Vector

# --- Constants ---
from CONSTANTS import TILE_WIDTH, TILE_HEIGHT, TILE_WIDTH_HALF, TILE_HEIGHT_HALF

def cart_to_iso(x, y):
	iso_x = (x - y)
	iso_y = (x + y) / 2
	return iso_x, iso_y

def iso_to_cart(iso_x, iso_y):
	x = iso_x / 2 + iso_y
	y = iso_y - iso_x / 2
	return x, y

def map_xy_to_iso(x, y, tile_width_half, tile_height_half):
	iso_x = (x - y) * tile_width_half
	iso_y = (x + y) * tile_height_half

def grid_xy_to_iso(x, y):
	iso_x = (x - y) * TILE_WIDTH_HALF
	iso_y = (x + y) * TILE_HEIGHT_HALF
	return iso_x, iso_y

def iso_to_grid_xy(x, y):
	grid_x = (x / TILE_WIDTH_HALF + y / TILE_HEIGHT_HALF) / 2
	grid_y = (y / TILE_HEIGHT_HALF - (x / TILE_WIDTH_HALF)) / 2
	return round(grid_x), round(grid_y)

def grid_pos_to_iso(pos):
	iso_x = (pos.x - pos.y) * TILE_WIDTH_HALF
	iso_y = (pos.x + pos.y) * TILE_HEIGHT_HALF
	return Vector(iso_x, iso_y)

def iso_to_map_pos(pos, tile_width_half, tile_height_half):
	map_x = (pos.x / tile_width_half + pos.y / tile_height_half) / 2
	map_y = (pos.y / tile_height_half - (pos.x / tile_width_half)) / 2
	return Vector(map_x, map_y)

def iso_to_grid_pos(pos):
	grid_x = (pos.x / TILE_WIDTH_HALF + pos.y / TILE_HEIGHT_HALF) / 2
	grid_y = (pos.y / TILE_HEIGHT_HALF - (pos.x / TILE_WIDTH_HALF)) / 2
	return Vector(grid_x, grid_y).round()
