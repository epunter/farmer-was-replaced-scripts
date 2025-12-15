import PlantPatterns

MODE_ALL = 0
MODE_PUMPKIN = 1
MODE_SUNFLOWER = 2
MODE_CACTUS = 3
MODE_DINOSAUR = 4
MODE_COMPANION = 5
MODE_MAZE = 6

def plantPattern(mode):
	if(mode == MODE_ALL):
		PlantPatterns.plantAll()
	elif(mode == MODE_PUMPKIN):
		PlantPatterns.plantPumpkin()
	elif(mode == MODE_SUNFLOWER):
		PlantPatterns.plantSunflower()
	elif(mode == MODE_CACTUS):
		PlantPatterns.plantCactus()
	elif(mode == MODE_DINOSAUR):
		PlantPatterns.dinosaur()
	elif(mode == MODE_COMPANION):
		PlantPatterns.plantCompanions()
	elif(mode == MODE_MAZE):
		PlantPatterns.runMaze()
		
if __name__ == "__main__":
	change_hat(Hats.Wizard_Hat)
	clear()
	while(True):
		plantPattern(MODE_MAZE)

		


		