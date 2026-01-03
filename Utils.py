water_threshold = 0.7

def safeGet(dict, key, default):
	if key in dict:
		return dict[key]
	else:
		return default
		
def tillIfAppropriate():
	if(get_ground_type() != Grounds.Soil):
		till()
		
def harvestIfAppropriate():
	if(can_harvest()):
		harvest()

def waterIfAppropriate(fertilize = False):
	if(get_water() <= water_threshold):
		use_item(Items.Water)
	if fertilize:
		use_item(Items.Fertilizer)
		
def isFullyGrown():
	if(can_harvest()):
		return True
	else:
		return False
		
def plantAny(plantType):
	if(plantType == Entities.Grass):
		if(get_ground_type() != Grounds.Grassland):
			till()
	elif(plantType == Entities.Bush):
		plant(Entities.Bush)
	elif(plantType == Entities.Tree):
		plant(Entities.Tree)
	elif(plantType == Entities.Carrot):
		tillIfAppropriate()
		plant(Entities.Carrot)
	