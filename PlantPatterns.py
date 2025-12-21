import Pathfinding
import Utils
import MegafarmHelpers
	
def megaFarmPumpkin():
	MegafarmHelpers.spawnDronesWithTasks(MegafarmHelpers.plantRowPumpkin, North, False)
	
	MegafarmHelpers.spawnDronesWithTasks(MegafarmHelpers.reCheckPumpkin, East, False)
	
	MegafarmHelpers.waitForAllDrones()
	
	harvest()

def megaFarmCacti():
	MegafarmHelpers.spawnDronesWithTasks(MegafarmHelpers.plantRowCacti, North)
		
	if (get_pos_x() == 0) and (get_pos_y() == 0):
		# Sort each row, largest to the East
		MegafarmHelpers.spawnDronesWithTasks(Pathfinding.cocktailSortEast, North, False)
		MegafarmHelpers.waitForAllDrones()
			
		# Sort each column, largest to the North
		MegafarmHelpers.spawnDronesWithTasks(Pathfinding.cocktailSortNorth, East, False)
		MegafarmHelpers.waitForAllDrones()
			
		# Once we are out of both bubble sort loops, we know the entire farm is sorted
		Pathfinding.returnToStart()
		Utils.harvestIfAppropriate()
		
def runMaze(mazeSize = get_world_size()):
	substanceCost = mazeSize * 2**(num_unlocked(Unlocks.Mazes) - 1)
	if num_items(Items.Weird_Substance) >= substanceCost:
		plant(Entities.Bush)
		use_item(Items.Weird_Substance, substanceCost)
		Pathfinding.solveMaze(substanceCost)
	
def plantCompanions():
	companionDict = {}
	iterationComplete = False
	while(not iterationComplete):
		# Harvest, plant companion (if we have one, default crop if not) and water
		Utils.harvestIfAppropriate()
		Utils.plantAny(Utils.safeGet(companionDict, (get_pos_x(), get_pos_y()), getDefaultCrop()))
		Utils.waterIfAppropriate()
		
		# Get the companion for the just-planted crop, if it's on the current or later column, store
		# it for planting, otherwise ignore it
		companion = get_companion()
		if(companion != None) and (get_pos_x() <= companion[1][0]):
			companionDict[companion[1]] = companion[0]
		Pathfinding.moveToNext()
		# If we're back at the origin, break out the iteration so we can reset
		if(get_pos_x() == 0) and (get_pos_y() == 0):
			iterationComplete = True
			
def getDefaultCrop():
	if((get_pos_x() + get_pos_y()) % 2 == 0):
		return Entities.Tree
	elif(get_pos_x() % 2 == 0):
		return Entities.Carrot
	else:
		return Entities.Grass

def dinosaur():
	change_hat(Hats.Dinosaur_Hat)
	success = True
	# Very naive approach, currently will just move in a pattern to stay completely
	# safe regardless of tail size, quite slow but reliable
	# TODO optimise for small tail sizes?
	while success == True:
		success = Pathfinding.playSnake()
		if (success == False):
			change_hat(Hats.Wizard_Hat)
			clear()
	
def plantPumpkin():
	passNo = 0
	checkAgain = []
	checkSize = 0
	# Do 2 pass overs of the farm, 1 to initially plant everything
	# and another to check for dead pumpkins
	while(passNo < 2):
		if(get_entity_type() == Entities.Dead_Pumpkin):
			# If we come across a dead pumpkin, add its coordinates to the list
			# and increment our counter
			checkAgain.append([get_pos_x(), get_pos_y()])
			checkSize = checkSize + 1
		Utils.tillIfAppropriate()
		plant(Entities.Pumpkin)
		Utils.waterIfAppropriate()
		Pathfinding.moveToNext()
		if(get_pos_x() == 0) and (get_pos_y() == 0):
			passNo = passNo + 1
		
	while(checkSize > 0):
		removed = []
		# Loop through our dead pumpkin coordinates
		for tile in checkAgain:
			Pathfinding.goto(tile[0], tile[1])
			# If it's fully grown and not dead, we can remove it from the list, otherwise replant it
			if(get_entity_type() != Entities.Dead_Pumpkin) and (Utils.isFullyGrown() == True):
				# Don't remove in place, as python will left-shift any remaining elements
				removed.append([get_pos_x(), get_pos_y()])
				checkSize = checkSize - 1
			else:
				plant(Entities.Pumpkin)
				use_item(Items.Fertilizer)
		for toRemove in removed:
			checkAgain.remove(toRemove)
				
	# Once we break out of the re-check loop, we know all pumpkins are healthy and fully grown
	Pathfinding.returnToStart()
	Utils.harvestIfAppropriate()
		
def plantCactus():
	# Do an initial pass and plant everything
	Utils.tillIfAppropriate()
	plant(Entities.Cactus)
	Utils.waterIfAppropriate()
	Pathfinding.moveToNextHorizontal()
	#Pathfinding.returnToStart()
	if (get_pos_x() == 0) and (get_pos_y() == 0):
		# Sort each row, largest to the East
		#Pathfinding.bubbleSort(East, Pathfinding.X_AXIS)
		Pathfinding.cocktailSort(East, Pathfinding.X_AXIS)
		# Sort each column, largest to the North
		#Pathfinding.bubbleSort(North, Pathfinding.Y_AXIS)
		Pathfinding.cocktailSort(North, Pathfinding.Y_AXIS)
			
		# Once we are out of both bubble sort loops, we know the entire farm is sorted
		Pathfinding.returnToStart()
		Utils.harvestIfAppropriate()
		
def plantSunflower():
	# Do an initial pass and plant everything
	Utils.tillIfAppropriate()
	plant(Entities.Sunflower)
	Utils.waterIfAppropriate()
	Pathfinding.moveToNext()
	if (get_pos_x() == 0) and (get_pos_y() == 0):
		flowers = {7:[], 8:[], 9:[], 10:[], 11:[], 12:[], 13:[], 14:[], 15:[]}
		measured = False
		# Iterate through each flower and add it's coordinates to its respective size in the dictionary
		while not measured:
			if(Utils.isFullyGrown()):
				flowers[measure()].append([get_pos_x(), get_pos_y()])
				Pathfinding.moveToNext()
			if (get_pos_x() == 0) and (get_pos_y() == 0):
				measured = True
				
		# Once we have all the coordinates, iterate backwards through the flower size dict
		# and harvest each coordinate in the list
		for i in range(9):
			for coords in flowers[15-i]:
				Pathfinding.goto(coords[0], coords[1])
				Utils.harvestIfAppropriate()
				
		Pathfinding.returnToStart()
	
def plantAll():
	Utils.harvestIfAppropriate()
	Utils.plantAny(getDefaultCrop())
	Utils.waterIfAppropriate()
	Pathfinding.moveToNext()
		
