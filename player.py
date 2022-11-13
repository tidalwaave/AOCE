import random
import time
from LAUNCH_SETUP import LAUNCH_NINJALUI
from entity.Entity import Entity
from CONSTANTS import Resource as Res
from entity.Unit import Military, Unit, Villager
from entity.Zone import Barracks, BerryBush, Buildable, Gold, House, Stone, StoragePit, Granary, TownCenter, Wood, WorkSite, Zone
from utils.isometric import iso_to_grid_pos
from utils.vector import Vector
# from game import GameView

class Player:
	def __init__(self,
				game,#: GameView,
				player_type: str,
				resources: dict) -> None:
		"""
		Create a player.

		:param str player_type: The player can be an human, an IA, ...etc
		:param int qty[Resource]: The initial qty of the 4 types of Resource
		"""
		self.game = game
		self.player_type = player_type
		self.is_alive = True

		# resource (dictionnary initialized with qty[Resource]
		# BE CAREFUL: The dictionnary "resources" is the same for all players, this is why we create a new one with this comprehension.
		self.resources = {key: 10000 if LAUNCH_NINJALUI else value for key, value in resources.items()}

		# unit
		self.nb_unit = 0
		self.max_unit = 4
		self.town_center = None
		self.my_units = set()
		self.my_military = set()
		self.my_zones = set()
		self.my_worksites = set()
		self.food_storage = set()
		self.other_storage = set()
		self.upgrades = {}

	def reset(self):
		self.resources.clear()
		self.my_units.clear()
		self.my_military.clear()
		self.my_zones.clear()
		self.my_worksites.clear()
		self.food_storage.clear()
		self.other_storage.clear()
		self.upgrades.clear()


	def __getstate__(self):
		return [self.player_type,
		self.is_alive,
		self.resources,
		self.nb_unit,
		self.max_unit,
		self.town_center,
		self.my_units,
		self.my_military,
		self.my_zones,
		self.my_worksites,
		self.food_storage,
		self.other_storage,
		self.upgrades]


	def __setstate__(self, data):
		self.player_type, self.is_alive, self.resources, self.nb_unit, self.max_unit, self.town_center, self.my_units, self.my_military, self.my_zones, self.my_worksites, self.food_storage, self.other_storage, self.upgrades = data

	# my_entities
	def add_entity(self, new_entity):
		if isinstance(new_entity, Unit):
			self.my_units.add(new_entity)
			self.nb_unit += 1
			if isinstance(new_entity, Military):
				self.my_military.add(new_entity)

		elif isinstance(new_entity, Buildable):
			self.my_zones.add(new_entity)
			if isinstance(new_entity, House):
				self.max_unit += 4
			elif isinstance(new_entity, TownCenter):
				self.town_center = new_entity
				self.food_storage.add(new_entity)
				self.other_storage.add(new_entity)
			elif isinstance(new_entity, Granary):
				self.food_storage.add(new_entity)
			elif isinstance(new_entity, StoragePit):
				self.other_storage.add(new_entity)

		elif isinstance(new_entity, WorkSite):
			self.my_worksites.add(new_entity)


	def discard_from_selection(self, dead_entity):
		for unit in self.my_units:
			if unit.aimed_entity == dead_entity:
				unit.aimed_entity = None
				unit.end_goal()


	def discard_entity(self, dead_entity):
		if isinstance(dead_entity, Unit):
			self.my_units.discard(dead_entity)
			self.nb_unit -= 1
			if isinstance(dead_entity, Military):
				self.my_military.discard(dead_entity)

		elif isinstance(dead_entity, Buildable):
			self.my_zones.discard(dead_entity)
			if isinstance(dead_entity, House):
				self.max_unit -= 4
			elif isinstance(dead_entity, TownCenter):
				self.food_storage.discard(dead_entity)
				self.other_storage.discard(dead_entity)
			elif isinstance(dead_entity, Granary):
				self.food_storage.discard(dead_entity)
			elif isinstance(dead_entity, StoragePit):
				self.other_storage.discard(dead_entity)

		elif isinstance(dead_entity, WorkSite):
			self.my_worksites.discard(dead_entity)


	def get_nbr_type_of_units(self, unit_class):
		count = 0
		for u in self.my_units:
			if isinstance(u, unit_class):
				count += 1
		return count

	# unit
	def get_nb_unit(self) -> int:
		return self.nb_unit

	def set_nb_unit(self, nb_unit):
		self.nb_unit = nb_unit

	def get_max_unit(self) -> int:
		return self.max_unit

	def set_max_unit(self, nb_max_unit: int):
		self.max_unit = nb_max_unit

	# resource
	#all (par Maxence, le 23/12 à 22h36)
	def add_all(self, qtyRes : int):
		self.resources[Res.FOOD] += qtyRes
		self.resources[Res.WOOD] += qtyRes
		self.resources[Res.GOLD] += qtyRes
		self.resources[Res.STONE] += qtyRes

	def reset_all_res(self):
		self.resources[Res.FOOD] = 200
		self.resources[Res.WOOD] = 200
		self.resources[Res.GOLD] = 100
		self.resources[Res.STONE] = 200

	def set_all_res(self, qtyFood, qtyWood, qtyGold, qtyStone):
		self.resources[Res.FOOD] += qtyFood
		self.resources[Res.WOOD] += qtyWood
		self.resources[Res.GOLD] += qtyGold
		self.resources[Res.STONE] += qtyStone

	def can_create(self, type_entity: Entity, upgrade_type_name=None) -> bool:
		if upgrade_type_name is None:
			upgrade_type_name = type_entity.get_name()
		if type_entity.get_name() == "villager" and self.upgrades.get(upgrade_type_name, 0) == 1:
			print("hey")
			return all((self.resources[k] >= type_entity.creation_cost[k] if k != Res.FOOD else self.resources[k] >= type_entity.creation_cost[k] - 20) for k in Res)
		elif type_entity.get_name() in ("barracks", "storagepit", "granary") and self.upgrades.get(upgrade_type_name, 0) == 1:
			return all((self.resources[k] >= type_entity.creation_cost[k] if k != Res.WOOD else self.resources[k] >= type_entity.creation_cost[k] - 20) for k in Res)
		elif type_entity.get_name() == "house" and self.upgrades.get(upgrade_type_name, 0) == 1:
			return all((self.resources[k] >= type_entity.creation_cost[k] if k != Res.WOOD else self.resources[k] >= type_entity.creation_cost[k] - 10) for k in Res)
		else:
			return all(self.resources[k] >= type_entity.creation_cost[k] for k in Res)

	# Resource
	def get_resource(self, resource):
		return self.resources[resource]

	def set_resource(self, resource, total_resource):
		self.resources[resource] = total_resource

	def add_resource(self, resource, qty_resource):
		self.resources[resource] += qty_resource

	def sub_resource(self, resource, qty_resource):
		self.resources[resource] -= qty_resource

	# Upgrade
	def upgrade(self, class_name_to_update):
		if self.upgrades.get(class_name_to_update, None) is None:
			self.upgrades[class_name_to_update] = 0
		self.upgrades[class_name_to_update] += 1

class AI(Player):
	def __init__(self,
			game,
			player_type: str,
			difficulty,
			resources: dict) -> None:
		super().__init__(game, player_type, resources)
		self.delta_time = 0
		self.difficulty = difficulty
		self.mind = {}


	def __getstate__(self):
		return [self.player_type,
		self.is_alive,
		self.resources,
		self.nb_unit,
		self.max_unit,
		self.town_center,
		self.my_units,
		self.my_military,
		self.my_zones,
		self.my_worksites,
		self.food_storage,
		self.other_storage,
		self.upgrades,
		self.delta_time,
		self.difficulty,
		self.mind]

	def __setstate__(self, data):
		self.player_type, self.is_alive, self.resources, self.nb_unit, self.max_unit, self.town_center, self.my_units, self.my_military, self.my_zones, self.my_worksites, self.food_storage, self.other_storage, self.upgrades, self.delta_time, self.difficulty, self.mind = data


	def reset(self):
		self.delta_time = 0
		self.mind.clear()
		super().reset()

	def search_enemy_to_attack(self):
		if self.mind.get("aimed_player", None) is None:
			self.mind["aimed_player"] = random.choice(tuple(player for player_key, player in self.game.players.items() if player_key != self.player_type))
			print(self.mind)

		if random.randint(0, 1) == 0: # 0 : I attack a zone / 1 : I attack a unit
			for zone in self.mind["aimed_player"].my_zones:
				return zone
			# aimed_tile, harvest_zone = self.game.game_model.map.get_closest_tile_nearby_fast(iso_to_grid_pos(self.town_center.iso_position), attacked_zone)

		for unit in self.mind["aimed_player"].my_units:
			return unit

	def send_army_towards(self, entity):
		self.mind["aimed_entity"] = entity
		# for military in self.my_military:
		# 	# DEBUG_start = time.time()
		# 	self.game.game_controller.order_attack(military, entity)
		# 	# print(f"time: {time.time() - DEBUG_start}")
		self.game.game_controller.order_army_attack(self.my_military, entity)

	def send_army(self):
		entity_to_attack = self.search_enemy_to_attack()
		self.send_army_towards(entity_to_attack)

	def send_army_agressive(self):
		# print("A L'ATTAQUE")
		if self.mind.get("aimed_player", None) is None:
			aimed_player = None
			for player_key, player in self.game.players.items():
				if player_key != self.player_type:
					if len(self.my_military) >= 5 + len(player.my_military):
						aimed_player = player
						break

			if aimed_player is None and len(self.my_military) >= 5 and random.randint(0, 4) == 0:
				for player_key, player in self.game.players.items():
					if player_key != self.player_type:
						aimed_player = player
						break

			self.mind["aimed_player"] = aimed_player

		if self.mind.get("aimed_player", None) is not None:
			self.send_army_towards(self.mind["aimed_player"].town_center)


	def search_pos_to_build(self, start_position, tile_size):
		area_found = False
		current_iter = 0
		map_position = None

		while not area_found and current_iter < 1000:
			rand_x = random.choice((random.randint(-10, -3), random.randint(3, 10)))
			rand_y = random.choice((random.randint(-10, -3), random.randint(3, 10)))
			map_position = start_position + Vector(rand_x, rand_y)
			if self.game.game_model.map.is_area_on_map(map_position, tile_size):
				area_found = self.game.game_model.map.is_area_buildable(map_position, tile_size)
			current_iter += 1
		if current_iter == 1000:
			map_position = None

		return map_position

	def search_closest_harvest_zone(self, unit, resource):
		class_to_harvest = None
		if resource == "food":
			class_to_harvest = BerryBush
		elif resource == "wood":
			class_to_harvest = Wood
		elif resource == "gold":
			class_to_harvest = Gold
		elif resource == "stone":
			class_to_harvest = Stone

		harvest_zones = {zone for zone in self.game.game_model.zone_list if isinstance(zone, class_to_harvest)}
		aimed_tile, harvest_zone = self.game.game_model.map.get_closest_tile_nearby_collection_fast(iso_to_grid_pos(unit.iso_position), harvest_zones)
		return harvest_zone

	def my_zones_contains(self, class_to_search: Zone):
		for zone in self.my_zones:
			if isinstance(zone, class_to_search): # TODO: Bug here
				return True
		return False

	def worksite_to_build(self, class_to_search: Zone):
		for worksite in self.my_worksites:
			if worksite.zone_to_build == class_to_search:
				return worksite
		return None

	def correct_mind(self): # Just in case...
		if (aimed_entity := self.mind.get("aimed_entity", None)) is not None and (aimed_entity.is_dead or not aimed_entity.is_alive()):
			self.mind["is_attacked_by"] = None
			self.mind["aimed_entity"] = None
			self.mind["counter_entity"] = None
			if isinstance(aimed_entity, TownCenter) or ((aimed_player := self.mind.get("aimed_player", None)) is not None and aimed_player.is_alive):
				self.mind["aimed_player"] = None

	def on_update(self, delta_time):

		if not self.is_alive:
			return

		self.delta_time += delta_time

		if (self.difficulty in ("Difficile", "Agressive", "Pacifique") and self.delta_time < 1) or (self.difficulty == "Moyen" and self.delta_time < 2) or (self.difficulty == "Facile" and self.delta_time < 3):
			return
		else:
			self.delta_time = 0

		self.correct_mind()

		idle_unit = None
		ongoing_actions = set()
		for unit in self.my_units:
			# print(iso_to_grid_pos(unit.iso_position), unit.is_moving, unit.is_interacting)
			if not unit.is_moving and not unit.is_interacting:
				if isinstance(unit, Villager):
					idle_unit = unit
			else:
				aimed_entity = unit.aimed_entity
				if isinstance(aimed_entity, WorkSite):
					aimed_entity = aimed_entity.zone_to_build
				ongoing_actions.add((unit.goal, aimed_entity.get_name()))

		unit = idle_unit
		impossible_actions = set()
		if unit is not None:
			if isinstance(unit, Villager):
				action_found = False
				while not action_found:
					if (action := ("harvest", "berrybush")) not in (ongoing_actions | impossible_actions) and self.resources[Res.FOOD] < 100:
						harvest_zone = self.search_closest_harvest_zone(unit, "food")
						if harvest_zone is not None:
							self.game.game_controller.order_harvest(unit, harvest_zone)
							action_found = True
						else:
							impossible_actions.add(action)

					elif (action := ("build", "house")) not in (ongoing_actions | impossible_actions) and self.max_unit - self.nb_unit < 2 and self.resources[Res.WOOD] > 30:
						worksite = self.worksite_to_build(House)

						if worksite is not None:
							self.game.game_controller.order_resume_build(unit, worksite)
							action_found = True
						else:
							map_position = self.search_pos_to_build(self.town_center.grid_position, House.tile_size)
							if map_position is not None:
								self.game.game_controller.order_build(unit, map_position, "house")
								action_found = True
							else:
								impossible_actions.add(action)

					elif (action := ("harvest", "wood")) not in (ongoing_actions | impossible_actions) and self.resources[Res.WOOD] < 100:
						harvest_zone = self.search_closest_harvest_zone(unit, "wood")
						if harvest_zone is not None:
							self.game.game_controller.order_harvest(unit, harvest_zone)
							action_found = True
						else:
							impossible_actions.add(action)

					elif (action := ("harvest", "stone")) not in (ongoing_actions | impossible_actions) and self.resources[Res.STONE] < 100:
						harvest_zone = self.search_closest_harvest_zone(unit, "stone")
						if harvest_zone is not None:
							self.game.game_controller.order_harvest(unit, harvest_zone)
							action_found = True
						else:
							impossible_actions.add(action)

					elif (action := ("harvest", "gold")) not in (ongoing_actions | impossible_actions) and self.resources[Res.GOLD] < 100:
						harvest_zone = self.search_closest_harvest_zone(unit, "gold")
						if harvest_zone is not None:
							self.game.game_controller.order_harvest(unit, harvest_zone)
							action_found = True
						else:
							impossible_actions.add(action)

					elif self.difficulty != "Pacifique" and (action := ("build", "barracks")) not in (ongoing_actions | impossible_actions) and not self.my_zones_contains(Barracks):
						worksite = self.worksite_to_build(Barracks)

						if worksite is not None:
							self.game.game_controller.order_resume_build(unit, worksite)
							action_found = True
						else:
							map_position = self.search_pos_to_build(self.town_center.grid_position, Barracks.tile_size)
							if map_position is not None:
								self.game.game_controller.order_build(unit, map_position, "barracks")
								action_found = True
							else:
								impossible_actions.add(action)

					else:
						action_found = True # This is not necessarely True technically, but this is to prevent infinite loop if no action is possible.
						iteration_guard = 0
						harvest_zone = None
						while harvest_zone is None and iteration_guard < 20:
							resources_name = "food", "gold", "stone", "wood"
							c = random.choice(resources_name)
							harvest_zone = self.search_closest_harvest_zone(unit, c)
							iteration_guard += 1
						if harvest_zone is not None:
							self.game.game_controller.order_harvest(unit, harvest_zone)

		if len(self.my_military) > 0 and self.difficulty != "Pacifique":
			# print(self.mind.get("aimed_entity", None))
			if self.mind.get("is_attacked_by", None) is not None and self.mind.get("counter_entity", None) is None:
				# print("I'M ATTACKED!!!")
				entity_attacking = self.mind["is_attacked_by"]
				self.mind["counter_entity"] = entity_attacking
				self.send_army_towards(entity_attacking)
			elif self.mind.get("aimed_entity", None) is None:
				# print("I WASN'T AIMING AN ENTITY")
				if self.difficulty == "Facile":
					if len(self.my_military) >= 30:
						self.send_army()
				elif self.difficulty == "Moyen":
					if len(self.my_military) >= 15:
						self.send_army()
				elif self.difficulty == "Difficile":
					if len(self.my_military) >= 5:
						self.send_army()
				elif self.difficulty == "Agressive":
					self.send_army_agressive()
			else:
				idle_military = set(military for military in self.my_military if military.goal != "attack")
				for military in idle_military:
					self.game.game_controller.order_attack(military, self.mind["aimed_entity"])

		who_is_producing = random.randint(0, 1)
		for zone in self.my_zones:
			if isinstance(zone, (TownCenter, Barracks)):
				if zone.is_producing:
					ongoing_actions.add(("produce", zone.class_produced.get_name()))
				else:
					if self.nb_unit < 40 and who_is_producing == 0 and isinstance(zone, TownCenter) and self.resources[Res.FOOD] > 50 and self.get_nbr_type_of_units(Villager) < 10 + len(self.my_military):
						self.game.game_controller.order_zone_units(zone)
					elif len(self.my_military) < 20 and who_is_producing == 1 and isinstance(zone, Barracks) and self.resources[Res.FOOD] > 50:
						self.game.game_controller.order_zone_units(zone, "militia")
