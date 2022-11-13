# Imports
import arcade
from arcade.gui.widgets import UITextArea, UITexturePane
from views.CustomButtons import SelctDifButton, NextViewButton, NumInput, LaunchGameButton, PlayerButton

#Constants
BACKGROUND_PREGAME = "./Ressources/img/FondAgePaint5.jpg"
COLOR_STATIC_RESSOURCES_ICONE = arcade.color.DARK_GRAY

class PreGameView(arcade.View) :

	def __init__(self, main_view, nbAdv=0) :
		super().__init__()
		self.main_view = main_view
		self.nbAdv = nbAdv

	def setup(self) :
		# add an UIManager to handle the UI.
		self.manager = arcade.gui.UIManager()

		if self.nbAdv == 4 :
			self.nbAdv = 0

	def on_show(self):
		""" This is run once when we switch to this view """

		# ajoute l'image de background
		self.texture = arcade.load_texture(BACKGROUND_PREGAME)

		self.manager.enable()

		self.setupButtons()
		self.ressourcesInput()
		self.launch_game()
		self.retourButton()

	# Boutton retour
	def retourButton(self):
		buttonsize = self.window.width / 10 # arbitrary

		# Create a vertical BoxGroup to align buttons
		self.retour_box = arcade.gui.UIBoxLayout()

		retour_button = NextViewButton(self.window, self.main_view, text="Retour", width=buttonsize)
		self.retour_box.add(retour_button)

		# Create a widget to hold the v_box widget, that will center the buttons
		self.manager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x = "left",
				align_x = buttonsize*(0.1), # arbitrary
				anchor_y = "top",
				align_y= -buttonsize*(0.1), # arbitrary
				child = self.retour_box
			)
		)


	def setupButtons(self):
		# def button size
		buttonsize = self.window.width / 6 # arbitrary

		# Create a vertical BoxGroup to align buttons
		self.ia_box = arcade.gui.UIBoxLayout()

		# Create the buttons of incrementation
		you_civil_button = PlayerButton(text="Vous", width=buttonsize * 2, height=buttonsize / 4)
		self.ia_box.add(you_civil_button.with_space_around(bottom=20))

		name = ["IA1", "IA2", "IA3", "IA4", "IA5", "IA6", "IA7"]

		for i in range(self.nbAdv) :
			adv_civil_button = SelctDifButton(text=name[i],size=buttonsize, name=name[i])
			self.ia_box.add(adv_civil_button.with_space_around(bottom=20))

		# Create a widget to hold the v_box widget, that will center the buttons
		self.manager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x = "left",
				align_x = buttonsize / 2, # arbitrary
				anchor_y = "top",
				align_y= -buttonsize * (3 / 5), # arbitrary
				child = self.ia_box
			)
		)

	#New class ad by GuiLeDav 22/11/2021, affiche la gestion du nombre de ressources
	def ressourcesInput(self) :
		# def button size
		buttonsize = self.window.width / 6 # arbitrarys

		#Couleur de fond pour les espaces ressources modifiables
		bg_text = arcade.load_texture("Ressources/img/bouton_vert_age.png")

		#Creation du text "Ressource :"
		map_text = UITextArea(
			x=self.window.width - buttonsize * (3 / 2), # arbitrary
			y=self.window.height - buttonsize * (0.75), # arbitrary
			width=buttonsize / 3,
			height=buttonsize / 10,
			text="Map seed :",
			text_color=(255, 255, 255, 255),
		)

		#Affichage de "Ressource :"
		self.manager.add(
			UITexturePane(
				map_text.with_space_around(right=20),
				tex=bg_text,
				padding=(10, 10, 10, 10)
			)
		)

		self.map_pane = arcade.gui.UITexturePane(
			NumInput(
				x=self.window.width - buttonsize/(1.4),
				y=self.window.height - buttonsize * (0.75),
				text="70", width=buttonsize/(2.5), height=buttonsize/10,
				text_color=(255, 255, 255, 255),
				limit=100
			),
			tex=bg_text,
			padding=(10, 10, 10, 10)
		)

		#Affichage des espaces ressources modifiables
		self.manager.add(self.map_pane)

		#Creation du text "Ressource :"
		ressource_text = UITextArea(
			x=self.window.width - buttonsize * (3 / 2), # arbitrary
			y=self.window.height - buttonsize, # arbitrary
			width=buttonsize / 2,
			height=buttonsize / 10,
			text="Ressources :",
			text_color=(255, 255, 255, 255),
		)

		name_ressources = ["Nourriture", "Bois", "Pierre", "Or"]
		ressources_default_value = {"Nourriture": 200, "Bois": 200, "Pierre": 200, "Or": 200}

		for i, name_ressource in enumerate(name_ressources) :
			text_area = UITextArea(
				x=self.window.width - buttonsize * (3 / 2),
				y=self.window.height - buttonsize * (1.25 + i * 0.25),
				width=buttonsize / 3,
				height=buttonsize / 11,
				text=f"{name_ressource} : ",
				text_color=(255, 255, 255, 255)
			)

			self.manager.add(
				UITexturePane(
					text_area.with_space_around(right=20),
					tex=bg_text,
					padding=(10, 10, 10, 10)
				)
			)

		#Creation des espaces ressources modifiables
		self.name_input_ressources = []

		for i, name_ressource in enumerate(name_ressources):
			texture_pane = arcade.gui.UITexturePane(
				NumInput(
					x=self.window.width - buttonsize/(1.4),
					y=self.window.height - buttonsize*(1.25+i*0.25),
					text=str(ressources_default_value[name_ressource]), width=buttonsize/(2.5), height=buttonsize/10,
					text_color=(255, 255, 255, 255)
				),
				tex=bg_text,
				padding=(10, 10, 10, 10)
			)

			#Affichage des espaces ressources modifiables
			self.manager.add(texture_pane)

			#Ajout du texture_pain créé à self.name_input_ressources
			self.name_input_ressources.append(texture_pane)

		#Affichage de "Ressource :"
		self.manager.add(
			UITexturePane(
				ressource_text.with_space_around(right=20),
				tex=bg_text,
				padding=(10, 10, 10, 10)
			)
		)

	#Button to start the game
	def launch_game(self):
		# def button size
		buttonsize = self.window.width / 6 # arbitrary

		# Create a vertical BoxGroup to align buttons
		self.launch_box = arcade.gui.UIBoxLayout()

		# Create the button
		num_enem_button = NextViewButton(
			self.window,
			PreGameView(self.main_view, self.nbAdv + 1),
			text="Nombre d'IA : " + str(self.nbAdv),
			width=buttonsize * (3 / 2)
		)
		self.launch_box.add(num_enem_button.with_space_around(bottom=20))

		launch_button = LaunchGameButton(
			self.window,
			self.main_view.game_view,
 			self,
			text="Lancer la partie",
			width=buttonsize * (3 / 2)
		)
		self.launch_box.add(launch_button.with_space_around(bottom=20))

		# Create a widget to hold the v_box widget, that will center the buttonsS
		self.manager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x = "right",
				align_x = -buttonsize*(0.2),
				anchor_y = "center_y",
				align_y = -buttonsize,
				child = self.launch_box
			)
		)

	def on_draw(self):
		""" Draw this view """
		arcade.start_render()
		self.texture.draw_sized(self.window.width / 2, self.window.height / 2, self.window.width, self.window.height)
		self.manager.draw()


	def on_hide_view(self) :
		self.manager.disable()
