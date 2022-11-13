# Definition des constantes utiles dans tout le projet

# Doc pour les enumerations: https://docs.python.org/fr/3/library/enum.html
from enum import Enum, auto
from LAUNCH_SETUP import LAUNCH_DEFAULT_MAP
class Resource(Enum):
	# On utilise les 4 ressources du jeu a de nombreux endroits dans le code
	# Voici donc une enumeration pour harmoniser le tout
	FOOD = auto()
	WOOD = auto()
	GOLD = auto()
	STONE = auto()

# Default number of tiles on each side of the map
DEFAULT_MAP_SIZE = 50 if LAUNCH_DEFAULT_MAP else 100

# Some basics sizes about tiles
TILE_WIDTH = 64 # arbitrary ?
TILE_HEIGHT = TILE_WIDTH // 2
TILE_WIDTH_HALF = TILE_WIDTH // 2
TILE_HEIGHT_HALF = TILE_HEIGHT // 2
