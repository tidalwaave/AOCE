# --- Imports ---
import arcade
from arcade.arcade_types import Color
from views.CustomButtons import LoadButton, QuitButton, NextViewButton
from views.SettingsView import SettingsView
from views.PreGameView import PreGameView
from views.IAvsIAView import IAPreGameView

# --- Constants ---
BACKGROUND = "./Ressources/img/background.png"

# View d'accueil : première à etre affichée à l'écran
class MainView(arcade.View) :

	def __init__(self, game_view) :
		super().__init__()
		self.game_view = game_view

	def setup(self) :
		pass

	def on_show(self):
		""" This is run once when we switch to this view """

		# ajoute l'image de background
		self.texture = arcade.load_texture(BACKGROUND)

		# add an UIManager to handle the UI.
		self.manager = arcade.gui.UIManager()
		self.manager.enable()

		self.setupButtons()

	def setupButtons(self):
		# def button size
		buttonsize = self.window.width / 6 # arbitrary

		# Create a vertical BoxGroup to align buttons
		self.v_box = arcade.gui.UIBoxLayout()

		# Create the buttons

		start_button = NextViewButton(self.window, PreGameView(self), text="Start Game VS IA", width=buttonsize)
		self.v_box.add(start_button.with_space_around(bottom=20))

		ia_match_button = NextViewButton(self.window,IAPreGameView(self), text="IA VS IA Game",width=buttonsize)
		self.v_box.add(ia_match_button.with_space_around(bottom=20))

		# TODO : charger une sauvegarde
		load_button = LoadButton(self.window, self, text="Charger une sauvegarde", width=buttonsize)
		self.v_box.add(load_button.with_space_around(bottom=20))

		settings_button = NextViewButton(self.window, SettingsView(self), text="Settings", width=buttonsize)
		self.v_box.add(settings_button.with_space_around(bottom=20))

		self.game_view.reset_game()
		quit_button = QuitButton(self.window, text="Quit", width=buttonsize)
		self.v_box.add(quit_button)

		# Create a widget to hold the v_box widget, that will center the buttons
		self.manager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x = "left",
				align_x = buttonsize,
				anchor_y = "center_y",
				align_y= -buttonsize / 6,
				child = self.v_box
			)
		)

	def on_draw(self):
		""" Draw this view """

		arcade.start_render()
		self.texture.draw_sized(self.window.width / 2, self.window.height / 2, self.window.width, self.window.height)
		self.manager.draw()

	def on_hide_view(self) :
		self.manager.disable()
