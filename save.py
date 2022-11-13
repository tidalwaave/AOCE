import pickle, json

import cheats_vars
def pickleSaving(game):
	save_file = "aocesave_" + cheats_vars.global_save_suffix +'.pkl'
	data = {'players': game.players, 'model': game.game_model, 'controller': game.game_controller}
	print(f"[Saving]: {data}")
	with open(save_file,'wb') as fileDescriptor:
		pickle.dump(data, fileDescriptor)
	print(f"[Saving]: Done!")

def pickleLoading():
	save_file = "aocesave_" + cheats_vars.global_save_suffix +'.pkl'
	print(f"[Loading]: Loading...")
	with open(save_file,'rb') as fileDescriptor:
		data = pickle.load(fileDescriptor)
		print(f"[Loaded]: Loaded")
	print(f"[Loading]: Done!")
	return data