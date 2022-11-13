import random
from LAUNCH_SETUP import LAUNCH_DISABLE_RANDOM_PLACEMENT, LAUNCH_FAST_ACTIONS, LAUNCH_LIGHTSPEED_MOVES
import cheats_vars
from entity.Entity import Entity
from utils.SpriteData import SpriteData
from CONSTANTS import Resource as Res
from utils.vector import Vector
from utils.isometric import *
# Pathfinding / movement imports
# TODO : pip3 install pathfinding


#   _    _           _   _
#  | |  | |         (_) | |
#  | |  | |  _ __    _  | |_
#  | |  | | | '_ \  | | | __|
#  | |__| | | | | | | | | |_
#   \____/  |_| |_| |_|  \__|

SPEED_UNITS = 3 # Correction of the speed because it was too slow --- Be careful: The FPS affects units speed!
class Unit(Entity):
	#une Unit est une Entity qui est mobile
	#Liste des Unit: https://ageofempires.fandom.com/wiki/Units_(Age_of_Empires_II)
	def __init__(self, iso_position, speed=5, **kwargs):
		super().__init__(iso_position, **kwargs)

		# Movement
		self.previous_goal = ""

		self.goal = ""
		self.aim = Vector(0, 0)  # coordinate aimed by the user when he clicked
		self.aimed_entity = None
		self.previous_aimed_entity = None
		self.is_moving = False
		self.is_interacting = False
		self.path = []
		self.change = Vector(0, 0)  # The change of coordinate calculated from the speed. This may be moved in the Controller in the future.
		self.speed = SPEED_UNITS * 5 if LAUNCH_LIGHTSPEED_MOVES else SPEED_UNITS * speed  # Speed of the unit

	def set_move_action(self):
		self.aim = Vector(0, 0)
		self.action_timer = 0
		self.is_interacting = False
		self.is_moving = True

	def set_aimed_entity(self, entity):
		if self.aimed_entity and self.previous_aimed_entity != self.aimed_entity:
			self.previous_aimed_entity = self.aimed_entity
		self.aimed_entity = entity

	def set_goal(self, goal):
		self.action_timer = 0
		if self.goal:
			self.previous_goal = self.goal
		self.goal = goal

	def go_back_to_harvest(self):
		if self.previous_goal == "harvest" and self.previous_aimed_entity:
			self.goal = "harvest"
			self.aimed_entity = self.previous_aimed_entity
			return True
		else:
			return False

	def end_goal(self):
		if self.goal:
			self.previous_goal = self.goal
		self.goal = ""
		self.is_moving = False
		self.is_interacting = False

	def set_path(self, path):
		self.path = path
		self.is_moving = True

	# Function for movement, may change in the future when pathfinding will be needed.
	def next_aim(self):
		self.aim = grid_pos_to_iso(Vector(*self.path.pop(0)))

		if not LAUNCH_DISABLE_RANDOM_PLACEMENT and len(self.path) == 0:
			self.aim += Vector(random.randint(-8, 8), random.randint(-8, 8))

		# The following calculation is necessary to have uniform speeds :
		self.change = SPEED_UNITS * 5 * ((self.aim - self.iso_position).normalized()) if cheats_vars.cheat_lightspeed else self.speed * ((self.aim - self.iso_position).normalized())
		# We want the same speed no matter what the distance between the villager and where he needs to go is.





#  __      ___ _ _
#  \ \    / (_) | |
#   \ \  / / _| | | __ _  __ _  ___ _ __
#    \ \/ / | | | |/ _` |/ _` |/ _ \ '__|
#     \  /  | | | | (_| | (_| |  __/ |
#      \/   |_|_|_|\__,_|\__, |\___|_|
#                         __/ |
#                        |___/


class Villager(Unit):#un Villageois est une Unit particuliere
	creation_cost = {Res.FOOD : 50, Res.WOOD : 0, Res.GOLD : 0, Res.STONE : 0}
	creation_time = 25
	sprite_data = SpriteData("Ressources/img/units/villager_stand.png", y_offset=46//2, x_offset=-3)
	speed = 0.8
	max_health = 25
	damage = 3
	rate_fire = 2
	line_sight = 4

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		sprite_data=Villager.sprite_data,
		faction=faction,
		speed=Villager.speed,
		health=health,
		max_health=Villager.max_health,
		damage=Villager.damage,
		rate_fire=Villager.rate_fire,
		line_sight=Villager.line_sight)

		self.resources = {Res.FOOD : 0, Res.WOOD : 0, Res.GOLD : 0, Res.STONE : 0} # utilisation de l'enumeration Resource
		self.max_resource = 3 if LAUNCH_FAST_ACTIONS else 10

	def nb_resources(self):
		nb = 0
		for resource in self.resources:
			nb += self.resources[resource]
		return nb

	def set_max_resource(self, max_resource):
		self.max_resource = max_resource

	def is_full(self):#ne peut plus prendre de nouvelles resources
		return self.nb_resources() == self.max_resource



#   __  __ _ _ _ _
#  |  \/  (_) (_) |
#  | \  / |_| |_| |_ __ _ _ __ _   _
#  | |\/| | | | | __/ _` | '__| | | |
#  | |  | | | | | || (_| | |  | |_| |
#  |_|  |_|_|_|_|\__\__,_|_|   \__, |
#                               __/ |
#                              |___/


class Military(Unit):#un Militaire est une Unit particuliere
	def __init__(self, iso_position, **kwargs):
		super().__init__(iso_position, **kwargs)

# Rq : Il n'est peut-être pas utile de creer les implementation de chaque type de militaire car cela n'apporte pas vraiment d'interet

#Infantry (Trained at Barracks)
# AOE 1 Military
# class Clubman(Military):
# 	creation_cost = {Res.FOOD : 50, Res.WOOD : 0, Res.GOLD : 0, Res.STONE : 0}
# 	creation_time = 26
# 	def __init__(self, iso_position, faction, health=-1):
# 		super().__init__(iso_position,
# 		sprite_data=SpriteData("Ressources/img/units/militia_stand.png", y_offset=50//2),
# 		faction=faction,
# 		speed=1, # la valeur de base était trop haut alors j'ai modifié
# 		health=health,
# 		max_health=40,
# 		damage=4,
# 		rate_fire=1.5,
# 		pierce_armor=0,
# 		line_sight=4)

# AOE 2 Military
class Militia(Military):
	creation_cost = {Res.FOOD : 60, Res.WOOD : 0, Res.GOLD : 20, Res.STONE : 0}
	creation_time = 21
	sprite_data = SpriteData("Ressources/img/units/militia_stand.png", y_offset=50//2)
	speed=0.9
	max_health = 40
	damage = 4
	rate_fire = 2
	pierce_armor = 1
	line_sight = 4

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		sprite_data=Militia.sprite_data,
		faction=faction,
		speed=Militia.speed,
		health=health,
		max_health=Militia.max_health,
		damage=Militia.damage,
		rate_fire=Militia.rate_fire,
		pierce_armor=Militia.pierce_armor,
		line_sight=Militia.line_sight)

class Spearman(Military):
	creation_cost = {Res.FOOD : 35, Res.WOOD : 25, Res.GOLD : 0, Res.STONE : 0}
	creation_time = 22
	sprite_data=SpriteData("Ressources/img/units/spearman_stand.png", y_offset=67//2)
	speed=1
	max_health=45
	damage=3
	rate_fire=3
	line_sight=4

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		sprite_data=SpriteData("Ressources/img/units/spearman_stand.png", y_offset=67//2),
		faction=faction,
		speed=Spearman.speed,
		health=health,
		max_health=Spearman.max_health,
		damage=Spearman.damage,
		rate_fire=Spearman.rate_fire,
		line_sight=Spearman.line_sight)

#Archery (Trained at Archery Range)
#For the moment, all archery units deal instant damage (there is no projectile) and they aim parfectly well.
class Archer(Military):
	creation_cost = {Res.FOOD : 0, Res.WOOD : 25, Res.GOLD : 45, Res.STONE : 0}
	creation_time = 35
	sprite_data=SpriteData("Ressources/img/units/archer_stand.png", y_offset=51//2)
	speed=0.96
	max_health=30
	damage=4
	rate_fire=2
	range=4
	line_sight=6

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		sprite_data=Archer.sprite_data,
		faction=faction,
		speed=Archer.speed,
		health=health,
		max_health=Archer.max_health,
		damage=Archer.damage,
		rate_fire=Archer.rate_fire,
		range=Archer.range,
		line_sight=Archer.line_sight)

class Skirmisher(Military):
	creation_cost = {Res.FOOD : 25, Res.WOOD : 35, Res.GOLD : 0, Res.STONE : 0}
	creation_time = 22
	sprite_data=SpriteData("Ressources/img/units/skirmisher_stand.png", y_offset=71//2)
	speed=0.96
	max_health=30
	damage=2
	rate_fire=3
	range=4
	pierce_armor=3
	line_sight=6

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		faction=faction,
		sprite_data=Skirmisher.sprite_data,
		speed=Skirmisher.speed,
		health=health,
		max_health=Skirmisher.max_health,
		damage=Skirmisher.damage,
		rate_fire=Skirmisher.rate_fire,
		range=Skirmisher.range,
		pierce_armor=Skirmisher.pierce_armor,
		line_sight=Skirmisher.line_sight)

#Cavalry (Trained at Stable)
class ScoutCavalry(Military):
	creation_cost = {Res.FOOD : 80, Res.WOOD : 0, Res.GOLD : 0, Res.STONE : 0}
	creation_time = 30
	sprite_data = SpriteData("Ressources/img/units/scoutcavalry_stand.png", y_offset=90//2)
	speed=1.2
	max_health=45
	damage=3
	rate_fire=2
	pierce_armor=2
	line_sight=4

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		faction=faction,
		sprite_data=ScoutCavalry.sprite_data,
		speed=ScoutCavalry.speed,
		health=health,
		max_health=ScoutCavalry.max_health,
		damage=ScoutCavalry.damage,
		rate_fire=ScoutCavalry.rate_fire,
		pierce_armor=ScoutCavalry.pierce_armor,
		line_sight=ScoutCavalry.line_sight)

class Knight(Military):
	creation_cost = {Res.FOOD : 60, Res.WOOD : 0, Res.GOLD : 75, Res.STONE : 0}
	creation_time = 30
	sprite_data=SpriteData("Ressources/img/units/knight_stand.png", y_offset=90//2)
	speed=1.35
	max_health=100
	damage=10
	rate_fire=1.8
	melee_armor=2
	pierce_armor=2
	line_sight=4

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		faction=faction,
		sprite_data=Knight.sprite_data,
		speed=Knight.speed,
		health=health,
		max_health=Knight.max_health,
		damage=Knight.damage,
		rate_fire=Knight.rate_fire,
		melee_armor=Knight.melee_armor,
		pierce_armor=Knight.pierce_armor,
		line_sight=Knight.line_sight)

#BigDaddy (CheatCode)
class BigDaddy(Military):
	creation_cost = {Res.FOOD : 0, Res.WOOD : 0, Res.GOLD : 0, Res.STONE : 0}
	creation_time = 0
	sprite_data=SpriteData("Ressources/img/units/bigdaddy.png", y_offset=90//2 - TILE_HEIGHT, scale=0.3)
	speed=4
	max_health=500
	damage=200
	rate_fire=10
	pierce_armor=10
	line_sight=17

	def __init__(self, iso_position, faction, health=-1):
		super().__init__(iso_position,
		faction=faction,
		sprite_data=BigDaddy.sprite_data,
		speed=BigDaddy.speed,
		health=health,
		max_health=BigDaddy.max_health,
		damage=BigDaddy.damage,
		rate_fire=BigDaddy.rate_fire,
		pierce_armor=BigDaddy.pierce_armor,
		line_sight=BigDaddy.line_sight)
