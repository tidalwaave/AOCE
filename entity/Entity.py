from entity.EntitySprite import EntitySprite
from CONSTANTS import Resource as Res

#   ______           _     _   _
#  |  ____|         | |   (_) | |
#  | |__     _ __   | |_   _  | |_   _   _
#  |  __|   | '_ \  | __| | | | __| | | | |
#  | |____  | | | | | |_  | | | |_  | |_| |
#  |______| |_| |_|  \__| |_|  \__|  \__, |
#                                     __/ |
#                                    |___/
#

SPRITE_SCALING_COIN = 0.2

class Entity:
	# https://ageofempires.fandom.com/wiki/Units_(Age_of_Empires)
	# https://ageofempires.fandom.com/wiki/Buildings_(Age_of_Empires)

  #static attributs which must be redefined in leaf classes
	creation_cost = {Res.FOOD : 0, Res.WOOD : 0, Res.GOLD : 0, Res.STONE : 0}
	creation_time = 0
	def __init__(self, iso_position, sprite_data, faction: str ="None", health=-1, max_health=-1, damage=0, rate_fire=1, range=0, melee_armor=0, pierce_armor=0, line_sight=4):
		# Position
		self.iso_position = iso_position

		# Sprite
		self.sprite_data = sprite_data
		self.sprite = EntitySprite(self, sprite_data, hit_box_algorithm="Simple")

		# Faction
		self.faction = faction

		# Backend
		self.action_timer = 0
		self.selected = False

		#
		## Life
		#
		#by default, initialize the life with max_health
		#health is when we load a game from a save file
		self.health = max_health if health == -1 else health
		self.max_health = max_health if health == -1 else health
		self.damage = damage
		self.is_dead = False

		# Battle
		self.rate_fire = rate_fire
		self.range = range
		self.melee_armor = melee_armor
		self.pierce_armor = pierce_armor
		self.line_sight = line_sight

	# def __getstate__(self):
	# 	return [self.iso_position, self.sprite_data, self.faction, self.health, self.max_health, self.damage, self.rate_fire, self.range, self.melee_armor, self.pierce_armor, self.line_sight]

	# def __setstate__(self, data):
	# 	# Position
	# 	self.iso_position = data[0]

	# 	# Sprite
	# 	self.sprite_data = data[1]
	# 	self.sprite = EntitySprite(self, self.sprite_data, hit_box_algorithm="Simple")

	# 	# Faction
	# 	self.faction = data[2]

	# 	# Backend
	# 	self.action_timer = 0
	# 	self.selected = False

	# 	#
	# 	## Life
	# 	#
	# 	self.health = data[3]
	# 	self.max_health = data[4]
	# 	self.damage = data[5]
	# 	self.is_dead = False

	# 	# Battle
	# 	self.rate_fire = data[6]
	# 	self.range = data[7]
	# 	self.melee_armor = data[8]
	# 	self.pierce_armor = data[9]
	# 	self.line_sight = data[10]

	@classmethod
	def get_name(cls):
		return cls.__name__.lower()

	# coordonnees
	def get_x(self):
		return self.iso_position.x
	def get_y(self):
		return self.iso_position.y
	def set_xy(self, x, y):
		self.iso_position.x = x
		self.iso_position.y = y

	def get_position(self):
		return self.iso_position
	def set_position(self, iso_position):
		self.iso_position = iso_position

	def get_sprite(self):
		return self.sprite

	# health
	def get_health(self):
		return self.health

	def set_health(self, health):
		self.health = health

	def gain_health(self, qty_health):
		self.health += qty_health
		if self.health > self.max_health:# on corrige le nb de pt de vie si celui-ci est superieur au maximum
			self.health = self.max_health

	def lose_health(self, qty_health):
		self.health -= qty_health
		if self.health <= 0:# on corrige le nb de pt de vie si celui-ci est negatif
			self.health = 0
			return False
		return True

	def is_alive(self):
		return self.health > 0

	# max_health
	def get_max_health(self):
		return self.max_health

	def set_max_health(self, max_health):
		self.max_health = max_health

	# damage
	def get_damage(self):
		return self.damage

	def set_damage(self, damage):
		self.damage = damage

	# rate_fire
	def get_rate_fire(self):
		return self.rate_fire

	def set_rate_fire(self, rate_fire):
		self.rate_fire = rate_fire

	# range
	def get_range(self):
		return self.range

	def set_range(self, range):
		self.range = range

	# melee_armor
	def get_melee_armor(self):
		return self.melee_armor

	def set_melee_armor(self, melee_armor):
		self.melee_armor = melee_armor

	# pierce_armor
	def get_pierce_armor(self):
		return self.pierce_armor

	def set_pierce_armor(self, pierce_armor):
		self.pierce_armor = pierce_armor

	# line_sight
	def get_line_sight(self):
		return self.line_sight

	def set_line_sight(self, line_sight):
		self.line_sight = line_sight
