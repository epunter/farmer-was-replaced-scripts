import Utils

def plantRowPumpkin():
	plantRow(Entities.Pumpkin)
		
def plantRowCacti():
	plantRow(Entities.Cactus)

def reCheckPumpkin():
	allGrown = False
	while not allGrown:
		allGrown = True
		for i in range(get_world_size()):
			if(get_entity_type() == Entities.Dead_Pumpkin) or (not Utils.isFullyGrown()):
				plant(Entities.Pumpkin)
				use_item(Items.Fertilizer)
				allGrown = False
			move(North)

def plantRow(entity):
	for _ in range(get_world_size()):
		# Do an initial pass and plant everything
		Utils.tillIfAppropriate()
		plant(entity)
		Utils.waterIfAppropriate()
		move(East)

def spawnDronesWithTasks(task, direction, waitForLast = True):
	for i in range(get_world_size()):
		if i == get_world_size() - 1:
			last_drone = spawn_drone(task)
		else:
			spawn_drone(task)
		move(direction)
		
	if waitForLast:
		wait_for(last_drone)

def waitForAllDrones():
	while(num_drones() > 1):
		quick_print("")