from arcade import Sprite
from utils.isometric import grid_pos_to_iso

class TileSprite(Sprite):
	def __init__(self, tile, sprite_data):
		super().__init__(filename=sprite_data.file, scale=sprite_data.scale)

		self.tile = tile

		iso_position = grid_pos_to_iso(tile.grid_position)  # Cette ligne ne recréer pas une map (testé et vérifié).
		self.center_x = iso_position.x + sprite_data.x_offset
		self.center_y = iso_position.y + sprite_data.y_offset