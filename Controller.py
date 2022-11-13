# --- Imports ---
from copy import deepcopy
from pickle import TRUE
import arcade
import time
from LAUNCH_SETUP import LAUNCH_ENABLE_IA
import cheats_vars
from utils.isometric import *
from entity.Unit import *
from entity.Zone import *
# from game import GameView
from player import AI, Player
from views.IAVictoryView import IAVictoryView
from views.VictoryView import VictoryView
from views.DefeatView import DefeatView

# --- Constants ---
from CONSTANTS import DEFAULT_MAP_SIZE, Resource

#########################################################################
#							CONTROLLER CLASS							#
#########################################################################

class Controller():

# --- Setup ---

	def __init__(self, aoce_game):#: GameView):
		""" Initializer """
		self.game = aoce_game

		# Selection (will contain elements of type Entity)
		self.selection = dict()  # self.section ---> convert to a dict, the key is "player" or "ai_1" or "ai_2" or ...
		self.dead_entities = set()
		self.ai = set()
		self.players = set()
		self.working_sites = set()
		self.type_of_game = ""

	def __getstate__(self):
		return [self.selection, self.dead_entities, self.ai, self.players, self.working_sites, self.type_of_game]

	def __setstate__(self, data):
		self.selection, self.dead_entities, self.ai, self.players, self.working_sites, self.type_of_game = data

	def reset(self):
		self.selection.clear()
		self.dead_entities.clear()
		self.ai.clear()
		self.players.clear()
		self.working_sites.clear()
		self.type_of_game = ""

	def setup(self, players_dict: dict, type_of_game):
		self.reset()
		self.selection["player"] = set()
		self.type_of_game = type_of_game
		for key, value in players_dict.items():
			self.players.add(value)
			self.selection[key] = set()
			if "ai" in key:
				self.ai.add(value)

# --- Utility methods ---
	@staticmethod
	def filter_type(type):
		return lambda entity: isinstance(entity, type)
	@staticmethod
	def filter_faction(faction, reverse=False):
		if reverse:
			return lambda entity: entity.faction != faction
		else:
			return lambda entity: entity.faction == faction
	@staticmethod
	def filter_both(type, faction, reverse=False):
		if reverse:
			return lambda entity: isinstance(entity, type) and entity.faction != faction
		else:
			return lambda entity: isinstance(entity, type) and entity.faction == faction

	@staticmethod
	def find_entity_in_sprites(sprites_collection, filter) -> Entity:
		for s in sprites_collection:
			entity = s.entity
			if entity and filter(entity):
				return entity
		return None
	@staticmethod
	def find_entity(entity_collection, filter) -> Entity:
		for e in entity_collection:
			if e and filter(e):
				return e
		return None



# --- Adding/Discarding entities ---

	def add_entity_to_game(self, new_entity):
		player = self.game.players.get(new_entity.faction)
		if player is not None:
			player.add_entity(new_entity)
		self.game.game_model.add_entity(new_entity)
		self.game.game_view.add_sprite(new_entity.sprite)
		self.game.game_view.update_resources_gui()

		if isinstance(new_entity, WorkSite):
			self.working_sites.add(new_entity)

	def discard_entity_from_game(self, dead_entity):
		dead_entity.is_dead = True
		if (selection_set := self.selection.get(dead_entity.faction)):
			selection_set.discard(dead_entity)
		self.game.game_view.update_resources_gui()

		for player in self.game.players.values():
			player.discard_from_selection(dead_entity)

		owner = self.game.players.get(dead_entity.faction)
		if owner is not None:
			owner.discard_entity(dead_entity)
		self.game.game_view.discard_sprite(dead_entity.sprite)
		self.game.game_model.discard_entity(dead_entity)

		if isinstance(dead_entity, WorkSite):
			self.working_sites.discard(dead_entity)

	def discard_player_from_game(self, player: Player):
		for entity in player.my_units | player.my_zones | player.my_worksites:
			entity.faction = None
			self.discard_entity_from_game(entity)



# --- Selection (Called once) ---

	def select(self, faction, sprites_at_point):
		self.clear_faction_selection(faction)
		unit_found = self.find_entity_in_sprites(sprites_at_point, self.filter_type(Unit))
		if unit_found :
			unit_found.selected = True
			self.selection[faction].add(unit_found)
			if isinstance(unit_found, Villager) :
				arcade.load_sound("./Ressources/music/newmail_aoe_scoutahem.wav").play()

	def select_zone(self, faction, sprites_at_point):
		self.clear_faction_selection(faction)
		zone_found = self.find_entity_in_sprites(sprites_at_point, self.filter_type(Zone))
		if zone_found:
			zone_found.selected = True
			self.selection[faction].add(zone_found)

	def clear_faction_selection(self, faction):
		for entity in self.selection[faction]:
			entity.selected = False
		self.selection[faction].clear()

	def unit_in_selection(self, faction):
		for entity in self.selection[faction]:
			if isinstance(entity, Unit):
				return True
		return False

	def zone_in_selection(self, faction):
		for entity in self.selection[faction]:
			if isinstance(entity, Zone):
				return True
		return False



# --- Human Orders (Called once) ----

	def human_order_towards_sprites(self, action, faction, sprites_at_point):

		if action == "army" : # keyboard shortcut to send the whole army
			entity_found = self.find_entity_in_sprites(sprites_at_point, self.filter_faction(faction, reverse=True))
			if entity_found:
				self.order_army_attack(self.game.players["player"].my_military, entity_found)
		else:
			for entity in self.selection[faction]:
				if action == "harvest/stock/attack/repair" : # click on batiment
					zone_found = self.find_entity_in_sprites(sprites_at_point, self.filter_type(Resources))
					if isinstance(entity, Villager) and zone_found: # harvest ressources
						self.order_harvest(entity, zone_found)
					else :
						zone_found = self.find_entity_in_sprites(sprites_at_point, self.filter_faction(faction))
						worksite_found = self.find_entity_in_sprites(sprites_at_point, self.filter_both(WorkSite,faction))
						stock_found = self.find_entity_in_sprites(sprites_at_point, self.filter_both((TownCenter, StoragePit, Granary), faction))
						if isinstance(entity, Villager) and stock_found and entity.nb_resources() != 0: #stock zone found and resources to stock
							self.order_stock_resources(entity, stock_found)

						elif isinstance(entity, Villager) and worksite_found:
							self.order_resume_build(entity, worksite_found)
						elif isinstance(entity, Villager) and zone_found: # zone of faction found, ask repairation
							self.order_repairation(entity, zone_found)
						else:
							other_zone_found = self.find_entity_in_sprites(sprites_at_point, self.filter_both((Buildable), faction, reverse=True))
							if other_zone_found: # no ally zone
								self.order_attack(entity, other_zone_found)
				if action == "attack" : # click on unit
					unit_found = self.find_entity_in_sprites(sprites_at_point, self.filter_faction(faction, reverse=True))
					if unit_found:
						self.order_attack(entity, unit_found)


	def human_order_towards_position(self, action, faction, iso_position, *args):
		grid_position = iso_to_grid_pos(iso_position)
		for entity in self.selection[faction]:
			if isinstance(entity, Unit) and entity.faction == faction :
				if action == "move":
					entity.set_goal("move")
					if self.is_on_map(grid_position):
						for entity in self.selection[faction]:
							self.move_entity(entity, grid_position, False)
					else:
						#print("out of bound!")
						return
				elif action == "build":
					self.order_build(entity, grid_position, *args)
	def human_order_with_zone(self, action: str, faction: str):
		if action == "populate":
			for entity in self.selection[faction]:
				if entity.faction == faction and isinstance(entity, TownCenter):
					self.order_zone_units(entity)
					return
		elif "train" in action:
			trained_entity = action.split(' ')[1]
			for entity in self.selection[faction]:
				if entity.faction == faction and isinstance(entity, Barracks):
					self.order_zone_units(entity, trained_entity)




# --- Orders (Called once) ----
	def move_entity(self, entity, end_grid_position, fast=True):
		path, path_len = self.game.game_model.map.get_path(start=iso_to_grid_pos(entity.iso_position), end=end_grid_position)
		# get_path_fast is a lot faster, but the pathfinding is a little more "stupid" and you need a little more to guide the units around obstacles
		# get_path_fast was unstable and added a lot of bugs so it's not used anymore.
		if path_len > 0:
			entity.set_move_action()
			entity.set_path(path)
			entity.next_aim()
		else:
			return

	def move_grouped_entities(self, entity_list, end_grid_position, fast=True):
		position_dict = {}
		for entity in entity_list:
			start_position = iso_to_grid_pos(entity.iso_position)
			if position_dict.get(tuple(start_position), None) is None:
				path, path_len = self.game.game_model.map.get_path(start=start_position, end=end_grid_position)
				# get_path_fast is a lot faster, but the pathfinding is a little more "stupid" and you need a little more to guide the units around obstacles
				# get_path_fast was unstable and added a lot of bugs so it's not used anymore.
				if path_len > 0:
					position_dict[tuple(start_position)] = path
					entity.set_move_action()
					entity.set_path(path)
					entity.next_aim()
				else:
					position_dict[tuple(start_position)] = ()
			else:
				path = position_dict[tuple(start_position)]

				if len(path) > 0:
					entity.set_move_action()
					entity.set_path(deepcopy(path))
					entity.next_aim()

	# Called once when you order an action on a zone
	def order_harvest(self, entity, zone_to_harvest):
		entity_grid_pos = iso_to_grid_pos(entity.iso_position)

		# Step 1: Search the closest tile near the zone_found to harvest it.

		aimed_tile = self.game.game_model.map.get_closest_tile_nearby_fast(entity_grid_pos, iso_to_grid_pos(zone_to_harvest.iso_position))

		# Step 2: Start moving toward the aimed entity

		if aimed_tile is not None:
			entity.set_goal("harvest")
			entity.set_aimed_entity(zone_to_harvest)
			if aimed_tile.grid_position == entity_grid_pos: # Dans ce cas c'est que nous sommes déjà arrivé
				entity.is_interacting = True
			else:
				self.move_entity(entity, aimed_tile.grid_position, False)

	def order_search_stock_resources(self, entity, resource_nbr):
		entity_grid_pos = iso_to_grid_pos(entity.iso_position)
		if resource_nbr == Res.FOOD:
			stock_zones = self.game.players[entity.faction].food_storage
		else:
			stock_zones = self.game.players[entity.faction].other_storage

		aimed_tile, stock_zone = self.game.game_model.map.get_closest_tile_nearby_collection_fast(entity_grid_pos, stock_zones)
		# Step 2: Start moving toward the aimed entity
		if aimed_tile is not None:
			entity.set_aimed_entity(stock_zone)
			if aimed_tile.grid_position != entity_grid_pos:
				self.move_entity(entity, aimed_tile.grid_position)


	def order_stock_resources(self, entity, stock_zone):
		entity.set_goal("stock")
		entity_grid_pos = iso_to_grid_pos(entity.iso_position)

		# Step 1: Search the closest tile near the zone_found to harvest it.
		aimed_tile = self.game.game_model.map.get_closest_tile_nearby_fast(entity_grid_pos, stock_zone.grid_position)

		# Step 2: Start moving toward the aimed entity
		if aimed_tile is not None:
			entity.set_aimed_entity(stock_zone)
			if aimed_tile.grid_position != entity_grid_pos:
				self.move_entity(entity, aimed_tile.grid_position)

	# Called once
	def order_build(self, entity, map_position, building_name):
		# Step 1: Create a worksite with the building_name
		zone_to_build_class = WorkSite.get_zone_class(building_name)
		if self.game.players[entity.faction].can_create(zone_to_build_class) :
			#Pour le gui, on baisse le flag si on peut finalement construire
			if entity.faction == "player":
				self.game.game_view.errorMessage = ""
			# Step 2: Search for an entity that can build: a Villager.
			if isinstance(entity, Villager):
				# Step 3: Start searching if it is possible to move toward the aimed map_position
				if not self.game.game_model.map.is_area_on_map(map_position, zone_to_build_class.tile_size):
					#print("out of bound!")
					return

				if not self.game.game_model.map.is_area_buildable(map_position, zone_to_build_class.tile_size):
					#print("area not available!")
					return

				if zone_to_build_class in (TownCenter, Barracks) and (not self.game.game_model.map.is_area_on_map(map_position - Vector(1, 1), (1, 1)) or not self.game.game_model.map.is_area_buildable(map_position - Vector(1, 1), (1, 1))):
					#print("no space to produce units!")
					return


				# Step 4: if possible (no return), move one tile below the first tile of the building and create the worksite
				worksite = WorkSite(map_position, entity.faction, building_name, entity)
				entity.set_goal("build")
				self.add_entity_to_game(worksite)
				entity.set_aimed_entity(worksite)
				aim = map_position - Vector(1,1)

				if iso_to_grid_pos(entity.iso_position) == aim:
					entity.is_interacting = True
				else:
					self.move_entity(entity, map_position - Vector(1, 1))
			else:
				pass
				#print("Not a Villager!")
		else:
			#print("not enough resources to order a build!")
			#Pour le GUI, on leve un flag pour le message d erreur
			if entity.faction == "player":
				self.game.game_view.errorMessage = "Vous manquez de ressources pour construire"

	# Called once
	def order_resume_build(self, entity, worksite):
		entity_grid_pos = iso_to_grid_pos(entity.iso_position)

		# Step 1: Search the closest tile near the worksite to resume the building.
		aimed_tile = self.game.game_model.map.get_closest_tile_nearby_fast(entity_grid_pos, iso_to_grid_pos(worksite.iso_position))

		# Step 2: Start moving toward the aimed entity
		if aimed_tile is not None:
			entity.set_goal("build")
			entity.set_aimed_entity(worksite)
			if aimed_tile.grid_position == entity_grid_pos: # Dans ce cas c'est que nous sommes déjà arrivé
				entity.is_interacting = True
			else:
				self.move_entity(entity, aimed_tile.grid_position, False)

	def order_zone_units(self, producing_zone, entity_produced = ""):

		if producing_zone.is_producing :
			return

		current_player = self.game.players[producing_zone.faction]
		if current_player.nb_unit < current_player.max_unit :
			if isinstance(producing_zone, Barracks) :
				producing_zone.set_class_produced(entity_produced)

			if current_player.can_create(producing_zone.class_produced, producing_zone.get_name()) :
				producing_zone.is_producing = True
				for key, value in producing_zone.class_produced.creation_cost.items():
					if isinstance(producing_zone, TownCenter) and key == Res.FOOD and current_player.upgrades.get(producing_zone.get_name(), 0) == 1:
						current_player.sub_resource(key, value - 20)
					else:
						current_player.sub_resource(key, value)

				if producing_zone.faction == "player" : # Shouldn't be used with AI
					self.game.game_view.update_resources_gui()
			else :
				if producing_zone.faction == "player":
					self.game.game_view.errorMessage = "Vous manquez de ressources pour produire des unités"
		else :
			if producing_zone.faction == "player":
				self.game.game_view.errorMessage = "Vous manquez de places pour cette population"

	def order_attack(self, entity: Unit, aimed_entity: Entity):
		# print(f"{entity} ---> VS {aimed_unit}")
		entity.set_goal("attack")
		entity.set_aimed_entity(aimed_entity)

		if isinstance(aimed_entity, Unit):
			self.move_entity(entity, iso_to_grid_pos(aimed_entity.iso_position), False)
		else:
			entity_grid_pos = iso_to_grid_pos(entity.iso_position)
			# Step 1: Search the closest tile near the zone_found to harvest it.
			aimed_tile = self.game.game_model.map.get_closest_tile_nearby_fast(entity_grid_pos, iso_to_grid_pos(aimed_entity.iso_position))
			#print(f"aimed_tile : {aimed_tile}")
			# Step 2: Start moving toward the aimed entity
			if aimed_tile is not None:
				#print(f"src and dest : {entity_grid_pos} -> {aimed_tile.grid_position}")
				if aimed_tile.grid_position == entity_grid_pos: # Dans ce cas c'est que nous sommes déjà arrivé
					entity.is_interacting = True
				else:
					self.move_entity(entity, aimed_tile.grid_position)

	def order_army_attack(self, entity_list, aimed_entity):
		last_entity = None
		for entity in entity_list:
			last_entity = entity
			entity.set_goal("attack")
			entity.set_aimed_entity(aimed_entity)

		if isinstance(aimed_entity, Unit):
			self.move_grouped_entities(entity_list, iso_to_grid_pos(aimed_entity.iso_position), False)
		else:
			first_entity_grid_pos = iso_to_grid_pos(last_entity.iso_position)
			# Step 1: Search the closest tile near the zone_found to harvest it.
			aimed_tile = self.game.game_model.map.get_closest_tile_nearby_fast(first_entity_grid_pos, iso_to_grid_pos(aimed_entity.iso_position))
			# print(f"aimed_tile : {aimed_tile}")
			# Step 2: Start moving toward the aimed entity
			if aimed_tile is not None:
				# print(f"src and dest : {first_entity_grid_pos} -> {aimed_tile.grid_position}")
				self.move_grouped_entities(entity_list, aimed_tile.grid_position)

	def order_repairation(self, entity, aimed_entity) :
		entity.set_goal("repair")
		entity.set_aimed_entity(aimed_entity)

		entity_grid_pos = iso_to_grid_pos(entity.iso_position)
		# Step 1: Search the closest tile near the zone_found to harvest it.
		aimed_tile = self.game.game_model.map.get_closest_tile_nearby_fast(entity_grid_pos, iso_to_grid_pos(aimed_entity.iso_position))
		#print(f"aimed_tile : {aimed_tile}")
		# Step 2: Start moving toward the aimed entity
		if aimed_tile :
			#print(f"src and dest : {entity_grid_pos} -> {aimed_tile.grid_position}")
			if aimed_tile.grid_position == entity_grid_pos: # Dans ce cas c'est que nous sommes déjà arrivé
				entity.is_interacting = True
			else:
				self.move_entity(entity, aimed_tile.grid_position)

	def order_upgradebuilding(self, upgradeIt:Buildable):
		if isinstance(upgradeIt, (Barracks, House, Granary, StoragePit, TownCenter)): # Dock not implemented
			current_player = self.game.players[upgradeIt.faction]
			current_level = current_player.upgrades.get(upgradeIt.get_name(), 0)  # If the key doesn't exists, it means we have never upgraded, so level 0 by default
			if (upgradeIt.upgrade_cost[current_level] != None):
				if all(current_player.resources[k] >= upgradeIt.upgrade_cost[current_level][k] for k in Res) :
						for k in Res :
							current_player.sub_resource(k, upgradeIt.upgrade_cost[current_level][k])
						if upgradeIt.faction == "player" : # Shouldn't be used with AI
							self.game.game_view.update_resources_gui()
						current_player.upgrade(upgradeIt.get_name())
				else :
					if upgradeIt.faction == "player":
						self.game.game_view.errorMessage = "Vous manquez de ressources pour améliorer"
			else :
				if upgradeIt.faction == "player":
					self.game.game_view.errorMessage = "Vous avez déjà amélioré ce batiment"

	def end_game(self):
		for player in self.game.players:
			if player == "player":
				VictoryView(self.game).setup()
				self.game.window.show_view(VictoryView(self.game))
			elif self.type_of_game == "JvsIA":  # which means a human was playing
				DefeatView(self.game,player).setup()
				self.game.window.show_view(DefeatView(self.game, player))
			else:
				IAVictoryView(self.game,player).setup()
				self.game.window.show_view(IAVictoryView(self.game,player))


# --- On_update (Called every frame) ---

	def on_update(self, delta_time):
		""" Movement and game logic """

		# --- Check End Conditions ---
		dead_players = set()
		for player in self.players:
			if player.town_center.is_dead:
				self.discard_player_from_game(player)
				player.is_alive = False
				dead_players.add(player)

		for dead_player in dead_players:
			self.players.remove(dead_player)
			del self.game.players[dead_player.player_type]

		if len(self.game.players) == 1 and self.type_of_game != "J": #If there is only one player in the game it will call end_game which will call Victory Screen.
			self.end_game()

		# --- Update AI ---
		if LAUNCH_ENABLE_IA:
			for ai in self.ai:
				ai.on_update(delta_time)

		# --- Updating Sets ---
		moving_entities = set()
		interacting_entities = set()
		for e in self.game.game_model.unit_list:
			if e.aimed_entity is not None and e.aimed_entity.is_dead:
				e.aimed_entity = None
				e.is_moving = None
				e.is_interacting = False
			if e.is_moving:
				moving_entities.add(e)
			if e.is_interacting:
				interacting_entities.add(e)

		producing_entities = set()
		for e in self.game.game_model.zone_list:
			if (isinstance(e, TownCenter) or isinstance(e, Barracks)) and e.is_producing:
				producing_entities.add(e)

		# --- Action - Moving entities ---
		for entity in moving_entities:
			# Check if the next position is on the map
			if not self.is_on_map(iso_to_grid_pos(entity.iso_position+entity.change)):
				entity.is_moving = False
			elif entity.iso_position.isalmost(entity.aim, SPEED_UNITS * 5 if cheats_vars.cheat_lightspeed else entity.speed):
				if entity.path:
					entity.next_aim()
				else: # ça veut dire qu'il est arrivé
					entity.is_moving = False
					if entity.goal in ("harvest", "stock", "build", "repair"):
						entity.is_interacting = True
					elif entity.goal == "attack":
						if isinstance(entity.aimed_entity, Unit):
							if iso_to_grid_pos(entity.iso_position) == iso_to_grid_pos(entity.aimed_entity.iso_position):
								# L'entité est arrivée
								entity.is_interacting = True
							elif (not entity.aimed_entity.is_moving) or entity.faction == "player" or entity.aimed_entity.faction == "player" :
								# L'entité n'est pas arrivée et l'autre ne bouge pas OU l'une des deux entités appartient à un joueur
								self.order_attack(entity, entity.aimed_entity)
							else:
								# L'entité n'est pas arrivée et l'autre bouge et les 2 appartiennent à des IA
								# "Temporary" fix to prevent circular/infinite loop of military chasing military...
								entity.end_goal()
						else:
							entity.is_interacting = True

			else:  # If it is not close to where it aims and not out of bounds, move.
				entity.iso_position += entity.change
				entity.sprite.update()

		# --- Action - Interacting entities ---
		for entity in interacting_entities:
			if entity.goal == "attack":
				if isinstance(entity.aimed_entity, Unit):
					if iso_to_grid_pos(entity.iso_position) != iso_to_grid_pos(entity.aimed_entity.iso_position):
						entity.is_interacting = False
						self.order_attack(entity, entity.aimed_entity)
					else:
						self.attack_entity(entity, delta_time)
				else:
					self.attack_entity(entity, delta_time)
			elif entity.goal == "harvest" and isinstance(entity.aimed_entity, Resources):
				self.harvest_zone(entity, delta_time)
			elif entity.goal == "build" and isinstance(entity.aimed_entity, WorkSite):
				self.build_zone(entity, delta_time)
			elif entity.goal == "stock" and  isinstance(entity.aimed_entity, (TownCenter, StoragePit, Granary)):
				self.stock_resources(entity, entity.aimed_entity.get_name())
			elif entity.goal == "repair" and isinstance(entity.aimed_entity, Buildable) :
				self.repair_zone(entity, delta_time)

		for entity in producing_entities:
			if isinstance(entity, (TownCenter, Barracks)):
				self.produce_units(entity, delta_time)

		# --- Deleting dead entities ---
		for dead_entity in self.dead_entities:
			#print("DEAD ENTITY DETECTED")
			self.discard_entity_from_game(dead_entity)
		self.dead_entities.clear()

	def is_on_map(self, grid_position):
		return self.game.game_model.map.is_on_map(grid_position)



# --- Updating interaction (Called every frame) ---

	def repair_zone(self, entity, delta_time) :
		entity.action_timer += delta_time
		if cheats_vars.cheat_steroids or cheats_vars.cheat_vitamins or entity.action_timer > 0.5 : # commence à réparer ou continue
			entity.action_timer = 0
			# print(f"{entity.aimed_entity.health} < {entity.aimed_entity.max_health}")
			if entity.aimed_entity.health < entity.aimed_entity.max_health :
				entity.aimed_entity.health += 1 # repare 1 point de vie

				if entity.faction == "player" :
					self.game.game_view.update_resources_gui()
			else : # fin de la réparation
				entity.end_goal()

	# Called every frame
	def build_zone(self, entity, delta_time):
		entity.aimed_entity.action_timer += delta_time
		if cheats_vars.cheat_steroids or (cheats_vars.cheat_vitamins and entity.aimed_entity.action_timer > 3) or entity.aimed_entity.action_timer > entity.aimed_entity.zone_to_build.build_time:  # build_time
			entity.action_timer = 0
			current_player = self.game.players[entity.faction]

			worksite = entity.aimed_entity
			self.discard_entity_from_game(entity.aimed_entity)
			entity.aimed_entity = None

			# print(current_player.upgrades, current_player.upgrades.get(worksite.zone_to_build.get_name(), 0))
			if current_player.can_create(worksite.zone_to_build):
				for res, cost in worksite.zone_to_build.creation_cost.items():
					if worksite.zone_to_build in (Barracks, StoragePit, Granary) and res == Res.WOOD and current_player.upgrades.get(worksite.zone_to_build.get_name(), 0) == 1:
						current_player.sub_resource(res, cost - 20)
					elif worksite.zone_to_build == House and res == Res.WOOD and current_player.upgrades.get(worksite.zone_to_build.get_name(), 0) == 1:
						current_player.sub_resource(res, cost - 10)
					else:
						current_player.sub_resource(res, cost)

				if entity.faction == "player":
					self.game.game_view.update_resources_gui()

				self.add_entity_to_game(worksite.create_zone())
			elif entity.faction == "player" :
				self.game.game_view.errorMessage = "Vous manquez de ressources pour construire"

			entity.end_goal()

	# Called every frame when an action is done on a zone (harvesting).
	# Récupère les resources présentes à chaque seconde, jusqu'à ce que ce soit full. Dans ce cas, il doit retourner au Town Center
	def harvest_zone(self, entity, delta_time):
		entity.action_timer += delta_time
		if cheats_vars.cheat_steroids or (cheats_vars.cheat_vitamins and entity.action_timer > 0.3) or entity.action_timer > 1:
			entity.action_timer = 0
			aimed_entity = entity.aimed_entity
			if not entity.is_full():
				harvested = aimed_entity.harvest(entity.damage)
				if harvested > 0:
					entity.resources[aimed_entity.get_resource_nbr()] += harvested
					# print(f"[harvesting] -> {type(entity).__name__} harvested {harvested} {type(aimed_entity).__name__}!")
					# print(f"[harvesting] -> {type(entity).__name__} has {entity.resources} - max_resources : {entity.max_resource}")
				elif harvested == -1: # The zone is totaly harvested.
					entity.end_goal()
					self.dead_entities.add(aimed_entity)
				if entity.faction == "player" :
					self.game.game_view.update_villager_resources_gui()
			else: # the entity is full and needs to go back to the town center.
				entity.set_goal("stock")
				self.order_search_stock_resources(entity, aimed_entity.get_resource_nbr())

	# Stock les resources qui ont été récolté définitivement et s'arrête
	def stock_resources(self, entity, storage_type):
		items_to_store = ()
		if storage_type == "towncenter":
			items_to_store = (Res.FOOD, Res.GOLD, Res.STONE, Res.WOOD)
		elif storage_type == "granary":
			items_to_store = (Res.FOOD,)
		elif storage_type == "storagepit":
			items_to_store = (Res.GOLD, Res.STONE, Res.WOOD)

		for resource in items_to_store:
			self.game.players[entity.faction].add_resource(resource, entity.resources[resource])
			entity.resources[resource] = 0

		if entity.faction == "player" :
			self.game.game_view.update_villager_resources_gui()
			self.game.game_view.update_resources_gui()

		can_harvest = entity.go_back_to_harvest()
		if can_harvest:
			self.order_harvest(entity, entity.previous_aimed_entity)

	# Produit une unité et s'arrête
	def produce_units(self, producing_zone, delta_time):
		producing_zone.action_timer += delta_time
		if cheats_vars.cheat_steroids or (cheats_vars.cheat_vitamins and producing_zone.action_timer > 3) or producing_zone.action_timer > producing_zone.unit_cooldown:
			producing_zone.action_timer = 0
			producing_zone.is_producing = False
			current_player = self.game.players[producing_zone.faction]
			if current_player.nb_unit < current_player.max_unit :
				grid_position = iso_to_grid_pos(producing_zone.iso_position) - Vector(1, 1)
				Class_produced = producing_zone.class_produced
				random_factor = 0 if LAUNCH_DISABLE_RANDOM_PLACEMENT else Vector(random.randint(-8, 8), random.randint(-8, 8))
				self.add_entity_to_game(Class_produced(grid_pos_to_iso(grid_position) + random_factor, producing_zone.faction))
			elif producing_zone.faction == "player":
				self.game.game_view.errorMessage = "Vous manquez de places pour cette population"

	def attack_entity(self, unit: Unit, delta_time):
		unit.action_timer += delta_time
		if unit.action_timer > 1/unit.rate_fire:
			player_controlling = self.game.players[unit.faction]
			opponent_controlling = self.game.players[unit.aimed_entity.faction]
			unit.action_timer = 0
			#print(f"[{unit.faction}: fighting] my health = {unit.health} - enemy health = {unit.aimed_entity.health}")
			alive = unit.aimed_entity.lose_health(unit.damage)

			if unit.faction == "player" or unit.aimed_entity.faction == "player" : # Shouldn't be used with AI
				self.game.game_view.update_villager_resources_gui()

			if isinstance(unit.aimed_entity, Unit) and unit.aimed_entity.aimed_entity != unit:
				self.order_attack(unit.aimed_entity, unit)
				unit.aimed_entity.is_interacting = True

			if isinstance(opponent_controlling, AI) and isinstance(unit.aimed_entity, Zone):
				opponent_controlling.mind["is_attacked_by"] = unit

			if not alive:
				# if isinstance(player_controlling, AI):
				# 	player_controlling.mind["is_attacked_by"] = None
				# 	player_controlling.mind["aimed_entity"] = None
				# 	player_controlling.mind["counter_entity"] = None
				# 	if isinstance(unit.aimed_entity, TownCenter) or not opponent_controlling.is_alive:
				# 		player_controlling.mind["aimed_player"] = None
				# Used to reset the mind of the IA, now it is in the AI on_update function but I left it here just in case
				unit.end_goal()
				self.dead_entities.add(unit.aimed_entity)
