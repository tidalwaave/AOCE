# --- Imports ---
import arcade
from arcade.arcade_types import Color
from views.CustomButtons import QuitButton, NextViewButton
from views.MainView import MainView

# --- Constants ---
BACKGROUND = "./Ressources/img/Victory3.jpg"

# View de victoire : on l'affiche quand le joueur remporte la partie
class VictoryView(arcade.View) :
    def __init__(self,game):
        super().__init__()
        self.game =game

    def setup(self):
        pass

    def on_show(self):
        """ This is run once when we switch to this view """

		# ajoute l'image de background
        self.texture = arcade.load_texture(BACKGROUND)

		# a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.setupButtons()

    def setupButtons(self):
        # def button size
        buttonsize = self.window.width / 3 # arbitrary

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        retour_menu = NextViewButton(self.window,MainView(self.game),text="Menu Principal",width=buttonsize)
        self.v_box.add(retour_menu.with_space_around(bottom=buttonsize/6))

        exit_game = QuitButton(self.window,text="Quit",width = buttonsize)
        self.v_box.add(exit_game)

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x = "left",
                align_x = buttonsize/2,
				anchor_y = "center_y",
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
