# Imports
import arcade
from arcade.gui.widgets import UITextArea, UITexturePane
from views.CustomButtons import NextViewButton, CheckboxButton

# Constants
SETTINGS_BACKGROUND = "./Ressources/img/LastImageSettings.jpg"

# View des paramètres accessible via ecran d'accueil
class SettingsView(arcade.View) :
	""" Settings view """

	def __init__(self, main_view) :
		super().__init__()
		self.main_view = main_view

	def on_show(self):
		""" This is run once when we switch to this view """

		# ajoute l'image de background
		self.texture = arcade.load_texture(SETTINGS_BACKGROUND)

		# a UIManager to handle the UI.
		self.manager = arcade.gui.UIManager()
		self.manager.enable()

		self.setupButtons()

	def setup(self) :
		pass

	def setupButtons(self) :
		# def sizes
		buttonsize = self.window.width / 6 # arbitrary
		checkboxsize = buttonsize / 2 # arbitrary

		# Create a vertical BoxGroup to align buttons
		self.v_box = arcade.gui.UIBoxLayout()

		# create the title text
		bg_text = arcade.load_texture("Ressources/img/parchemin3.png")
		settings = UITextArea(text="Paramètres", text_color=(0, 0, 0, 255), font_size=50)
		settings.fit_content()
		self.v_box.add(settings)

		# Create checkboxes
		self.h_box_music = arcade.gui.UIBoxLayout(vertical=False, align='left')
		music_button = CheckboxButton(self.window, text="", size=checkboxsize, ticked=self.window.isPlayingMusic(), music=True)
		self.h_box_music.add(music_button.with_space_around(right=20))
		music_text = UITextArea(text="Musique", text_color=(0, 0, 0, 255), font_size=20)
		music_text.fit_content()
		self.h_box_music.add(music_text)
		self.v_box.add(self.h_box_music.with_space_around(top=20))

		self.h_box_fullscreen = arcade.gui.UIBoxLayout(vertical=False, align='left')
		fullscreen_button = CheckboxButton(self.window, text="", size=checkboxsize, ticked=not self.window.fullscreen, fullscreen=True)
		self.h_box_fullscreen.add(fullscreen_button.with_space_around(right=20))
		fullscreen_text = UITextArea(text="Fenêtré", text_color=(0, 0, 0, 255), font_size=20)
		fullscreen_text.fit_content()
		self.h_box_fullscreen.add(fullscreen_text)
		self.v_box.add(self.h_box_fullscreen.with_space_around(top=20))

		self.h_box_vsync = arcade.gui.UIBoxLayout(vertical=False, align='left')
		vsync_button = CheckboxButton(self.window, text="", size=checkboxsize, ticked=self.window.vsync, vsync=True)
		self.h_box_vsync.add(vsync_button.with_space_around(right=20))
		vsync_text = UITextArea(text="V-Sync", text_color=(0, 0, 0, 255), font_size=20)
		vsync_text.fit_content()
		self.h_box_vsync.add(vsync_text)
		self.v_box.add(self.h_box_vsync.with_space_around(top=20))

		self.h_box_tactil = arcade.gui.UIBoxLayout(vertical=False, align='left')
		tactil_button = CheckboxButton(self.window, text="", size=checkboxsize, ticked=self.window.tactilmod, tactil=True)
		self.h_box_tactil.add(tactil_button.with_space_around(right=20))
		tactil_text = UITextArea(text="Tactile", text_color=(0, 0, 0, 255), font_size=20)
		tactil_text.fit_content()
		self.h_box_tactil.add(tactil_text)
		self.v_box.add(self.h_box_tactil.with_space_around(top=20))

		# Create the return menu
		retour_button = NextViewButton(self.window, self.main_view, text="Retour", width=buttonsize)
		self.v_box.add(retour_button.with_space_around(top=20))

		# Create a widget to hold the v_box widget, that will center the buttons
		self.manager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x = "center_x",
				anchor_y = "center_y",
				child = UITexturePane(
					self.v_box,
					tex=bg_text,
					padding=(150, 150, 150, 150)
				)
			)
		)

	def on_draw(self):
		""" Draw this view """
		arcade.start_render()

		self.texture.draw_sized(self.window.width / 2, self.window.height / 2, self.window.width, self.window.height)

		self.manager.draw()


	def on_hide_view(self) :
		self.manager.disable()
