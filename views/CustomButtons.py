# Imports
from ctypes import string_at
from arcade.arcade_types import Color
import arcade.gui
from save import pickleLoading, pickleSaving
from entity.Unit import *

# Constants
from CONSTANTS import Resource as Res
textureTicked = "Ressources/img/tick.png"
textureEmpty = "Ressources/img/empty.png"
button_texture = "Ressources/img/button_background.png"

#############################################################
#					Custom buttons							#
#############################################################

# Button to exit the game
class QuitButton(arcade.gui.UITextureButton) :
	def __init__(self, window, text, width) :
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width)
		self.window = window

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		self.window.exit()


class SaveButton(arcade.gui.UITextureButton) :
	def __init__(self, game, text, width) :
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width)
		self.game = game

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		pickleSaving(self.game)

class LoadButton(arcade.gui.UITextureButton):
	def __init__(self, window, main_view, text, width):
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width)
		self.window = window
		self.main_view = main_view
		self.nextView = main_view.game_view

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		data = pickleLoading()
		#print("Data LOADED!!!")
		self.nextView.load_save(data)
		self.window.show_view(self.nextView)

# Button to return to the main menu
class NextViewButton(arcade.gui.UITextureButton) :
	def __init__(self, window, nextView, text, width) :
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width)
		self.window = window
		self.nextView = nextView

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		self.nextView.setup()
		self.window.show_view(self.nextView)

# Button to tactile mode
class TactilButton(arcade.gui.UITextureButton) :
	def __init__(self, view, text, width, height) :
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width, height=height)
		self.view = view
		self.bool = True

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		if self.bool :
			self.view.right_click_mode = True
			self.text = "Mode Clique Gauche"
			self.bool = False
		else :
			self.reset()

	def reset(self) :
		self.view.right_click_mode = False
		self.text = "Mode Clique Droit"
		self.bool = True

# Button to return to the main menu
class LaunchGameButton(arcade.gui.UITextureButton) :
	def __init__(self, window, nextView, pregameview, text, width) :
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width)
		self.window = window
		self.nextView = nextView
		self.pregameview = pregameview

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		ia = {}
		for padding in self.pregameview.ia_box.children :
			name, diff = padding.child.text.split(padding.child.sep)
			ia[name] = diff

		ressources = {}
		tab = [Res.FOOD, Res.WOOD, Res.STONE, Res.GOLD]
		indice = 0
		for texture_pane in self.pregameview.name_input_ressources :
			ressources[tab[indice]] = int(texture_pane.child.text)
			indice += 1
		self.nextView.setup(ressources, ia, int(self.pregameview.map_pane.child.text))
		self.window.show_view(self.nextView)

# Button to display things or not
class ListButton(arcade.gui.UITextureButton) :
	def __init__(self, vbox, children, text, width) :
		super().__init__(texture=arcade.load_texture(button_texture), text=text, width=width)
		self.vbox = vbox
		self.list = children
		self.isDisplayed = False

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		self.isDisplayed = not self.isDisplayed
		self.vbox.clear()
		self.vbox.add(self)

		if self.isDisplayed :
			for child in self.list :
				self.vbox.add(child)


# CheckboxButton
class CheckboxButton(arcade.gui.UITextureButton) :
	def __init__(self, window, text, size, ticked=True, music=False, fullscreen=False, vsync=False, tactil=False) :
		super().__init__(texture=arcade.load_texture(textureTicked if ticked else textureEmpty), text=text, width=size, height=size)
		self.window = window
		self.ticked = ticked
		self.music = music
		self.fullscreen = fullscreen
		self.vsync = vsync
		self.tactil = tactil

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		self.texture = arcade.load_texture(textureEmpty if self.ticked else textureTicked)

		self.ticked = not self.ticked

		if self.music :
			self.window.triggerMusic()
		elif self.fullscreen :
			self.window.triggerFullscreen()
		elif self.vsync :
			self.window.triggerVsync()
		elif self.tactil :
			self.window.triggerTactil()

# Selection de sa difficulté
class SelctDifButton(arcade.gui.UITextureButton):
	def __init__(self, text, size, name):
		super().__init__(texture=arcade.load_texture(button_texture), text=text + " : Moyen", width=size * 2, height=size / 4)
		self.count = 2
		self.name = name
		self.list = ["Pacifique", "Facile", "Moyen", "Difficile", "Agressive"]
		self.sep = " : "

	def on_click(self, event: arcade.gui.UIOnClickEvent):
		if self.count == len(self.list) - 1 :
			self.count = 0
		else :
			self.count = self.count + 1
		self.text = self.name + self.sep + self.list[self.count]

class PlayerButton(arcade.gui.UITextureButton):
	def __init__(self, text, width, height):
		super().__init__(texture=arcade.load_texture(button_texture), text=text + " : Joueur Humain", width=width, height=height)
		self.sep = " : "

class NumInput(arcade.gui.UIInputText) :
	def __init__(self, x, y, text, width, height, text_color, limit=None) :
		super().__init__(x=x, y=y, text=text, width=width, height=height, text_color=text_color)
		self.limit = limit

	def on_event(self, event) :
		bool = True
		if self._active and isinstance(event, arcade.gui.events.UITextEvent) :
			if (not (event.text.isnumeric() or event.text == "") or (self.limit != None and int(self.text + event.text) >= self.limit)) :
				bool = False

		if bool :
			super().on_event(event)

		if self.text == "" :
			self.caret.on_text("0")

class ConstructButton(arcade.gui.UITextureButton) :
	def __init__(self, aoce_game, image, width, height, text=""):
		super().__init__(texture=arcade.load_texture(image), width=width, height=height, text=text)
		self.game = aoce_game

	def on_click(self, event: arcade.gui.UIOnClickEvent):
		#On initialise à zero au cas ou le player changerai d avis sur ce qu il veut construire
		self.game.game_view.reset_construct_flags()
		self.game.game_view.count_time = 0

		if self.text in ("StoragePit", "House", "Granary", "Barracks"):  # Avant : ("StoragePit", "House", "Granary", "Barracks", "TownCenter")
			self.game.game_view.build_request = self.text.lower()

class ActionButton(arcade.gui.UITextureButton) :
	def __init__(self, text, width, height, batiment, aoce_game, image) :
		super().__init__(texture=arcade.load_texture(image), text=text, width=width, height=height)
		self.batiment = batiment
		self.aoce_game = aoce_game

	def on_click(self, event: arcade.gui.UIOnClickEvent) :
		if self.text == "Villageois" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, Villager.get_name())
		elif self.text == "Milice" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, Militia.get_name())
		elif self.text == "Lancier" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, Spearman.get_name())
		elif self.text == "Archer" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, Archer.get_name())
		elif self.text == "Escarmoucheur" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, Skirmisher.get_name())
		elif self.text == "Eclaireur" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, ScoutCavalry.get_name())
		elif self.text == "Chevalier" :
			self.aoce_game.game_controller.order_zone_units(self.batiment, Knight.get_name())
		elif self.text == "Amélioration" :
			self.aoce_game.game_controller.order_upgradebuilding(self.batiment)
