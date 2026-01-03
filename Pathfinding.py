import Math
import Utils

oppositeDir = {East:West, West:East, North:South, South:North}
directions = [North, East, West, South]
deltaDirections = {North:(0,1), East:(1,0), South:(0,-1), West:(-1,0)}
defaultWalls = {North:True, East:True, West:True, South:True}
X_AXIS = 'x'
Y_AXIS = 'y'

# Solves any maze, continually using Weird Substance on the chest until we can't anymore,
# we pre-cache the maze itself so we can solve it programmatically and give the drone
# directions, so re-use the same maze to save time pre-caching
def solveMaze(substanceCost):
	walls = {}
	iterations = 1
	# Initialise our walls dictionary
	walls[(get_pos_x(), get_pos_y())] = {}
	for dir in directions:
		walls[(get_pos_x(), get_pos_y())][dir] = can_move(dir)
		
	# Use a recursive DFS to traverse the entire maze and map all the walls
	for explore_dir in directions:
		if (explorePath(explore_dir, walls)):
			break
	
	# Re-use of the same maze is capped at 300 times, and can only continue if we
	# have enough weird substance
	while(iterations < 300 and num_items(Items.Weird_Substance) >= substanceCost):
		findTreasure(walls)
				
		# Track our iterations and use weird substance on the chest
		iterations = iterations + 1
		use_item(Items.Weird_Substance, substanceCost)
	
	# One more to finish, need to harvest this time to end the maze
	findTreasure(walls)
	harvest()
	
# Uses the provided walls dictionary to create and navigate a path through the current maze
def findTreasure(walls):
	# Once we have all the walls mapped we can use A* algorithm to create all the steps 
	# we need to reach the treasure for a given maze
	targetCoords = measure()
	startCoords = get_pos_x(), get_pos_y()
	stack = getAStarPathStack(startCoords, targetCoords, walls)
		
	# Once we have our stack, perform each of the given directions until we've solved it
	while len(stack) > 0:
		next_move = stack.pop()
		move(next_move)
		for dir in directions:
			walls[(get_pos_x(), get_pos_y())][dir] = can_move(dir)

# Calculates and returns a stack of directions using an A* pathfinding algorithm
def getAStarPathStack(startCoords, targetCoords, walls):
	# Priority Queue - list of (fScore, gScore, x, y)
	pQueue = [(0, 0, (startCoords[0], startCoords[1]))]

	gScore = {startCoords: 0}
	cameFrom = {}

	while len(pQueue) > 0:
		# We keep the list sorted so index 0 is always the best
		currentF, currentG, current = pQueue.pop(0)

		# If our current position is the treasure, iterate backwards through our path and append
		# to the stack so we can pass to movement code
		if current == targetCoords:
			path = []
			while current in cameFrom:
				prev, move = cameFrom[current]
				path.append(move)
				current = prev
			return path

		# Get the current state of walls for the current tile
		curWalls = Utils.safeGet(walls, current, defaultWalls)

		for direction in deltaDirections:
			# Check walls first to avoid calculations if blocked
			# Assuming True is default passable
			is_passable = Utils.safeGet(curWalls, direction, True)
			if not is_passable:
				continue

			# If we are able to traverse in the given direction, get the neighbour of the current tile
			neighbour = (current[0] + deltaDirections[direction][0], current[1] + deltaDirections[direction][1])
			
			# tentativeG is the cost to get to neighbour via current tile
			tentativeG = currentG + 1

			if neighbour not in gScore or tentativeG < Utils.safeGet(gScore, neighbour, 99999):
				# If this path is better than any previous one to neighbour, then overwrite gscore
				gScore[neighbour] = tentativeG
				
				# Calculate heuristic and fscore
				hScore = (abs(neighbour[0] - targetCoords[0]) + abs(neighbour[1] - targetCoords[1])) * 1.001
				fScore = tentativeG + hScore
				
				# Find the next highest and keep the list sorted by f score
				newEntry = (fScore, tentativeG, neighbour)
				inserted = False
				for i in range(len(pQueue)):
					if fScore < pQueue[i][0]:
						pQueue.insert(i, newEntry)
						inserted = True
						break
				if not inserted:
					pQueue.append(newEntry)
				
				cameFrom[neighbour] = (current, direction)

	# If we exit the while without identifying a path, then there's no path to the treasure
	return []

	# Recursive function to explore all paths for a given maze and log where the walls are
def explorePath(direction, walls):
	# Attempt to move in the given direction, returning early if we're not able to
	if not move(direction):
		return False
		
	# If the walls dictionary contains all tiles in the farm, it's complete so return our success case
	if (len(walls) == get_world_size()**2):
		return True
		
	# If we haven't already explored this tile, then we should survey the walls
	if ((get_pos_x(), get_pos_y()) not in walls):
		walls[(get_pos_x(), get_pos_y())] = {}
		for dir in directions:
			walls[(get_pos_x(), get_pos_y())][dir] = can_move(dir)
		
	# Once we've surveyed the walls, we can recursively call into this method to continue exploring
	# all possible directions
	for explore_dir in directions:
		if (oppositeDir[explore_dir] == direction):
			continue
		
		# If we recieve a success case, then we know the walls dict is full, so return out
		if (explorePath(explore_dir, walls)):
			return True
	# If we reach a dead end, we need to return the opposite way to explore the other paths
	move(oppositeDir[direction])
	

def playSnake():
	current_path = []
	saved_target = None
	tail_history = []
	current_length = 0
	# Heuristic - only use A* if we fill less than 10% of the board.
	max_length = (get_world_size()**2)*0.1

	while True:
		# measure() returns None if called a multiple times
		# Only update saved_target if we get a real reading.
		scan_result = measure()
		if scan_result != None:
			saved_target = scan_result
			# New target found implies old path is invalid or we just finished one
			current_path = [] 
			
		if len(current_path) == 0 and saved_target != None:
			if len(tail_history) < max_length:
				walls = constructWallsFromHistory(tail_history)
				current_path = getAStarPathStack((get_pos_x(), get_pos_y()), saved_target, walls)

		move_successful = False
		
		# Try to use the cached A* path
		if len(current_path) > 0:
			next_move = current_path.pop()
			
			# safety check: is this specific move blocked?
			if can_move(next_move): 
				move(next_move)
				move_successful = True
			else:
				# The path is blocked/invalid. Discard it.
				current_path = []
		
		# If the path failed, was empty, or we are too big for A*
		if not move_successful:
			current_path = [] # Clear bad paths
			move_successful = hamiltonianCycle()
			
		# If the move still isn't successful, we've died
		if not move_successful:
			break

		# Update tail history for the next A* calculation
		current_pos = (get_pos_x(), get_pos_y())
		tail_history.append(current_pos)
		
		# If we reached the target, increment length
		if current_pos == saved_target:
			current_length += 1
			saved_target = None # Reset target so we look for a new one
			
		# Keep history trimmed to actual size
		while len(tail_history) > current_length:
			tail_history.pop(0)

def constructWallsFromHistory(last_movements):
	walls = {}
	for move in last_movements:
		for dir in deltaDirections:
			neighbour = (move[0] + deltaDirections[dir][0], move[1] + deltaDirections[dir][1])
			if (neighbour not in walls):
				walls[neighbour] = {}
			walls[neighbour][oppositeDir[dir]] = False
	return walls

# Moves in a pattern that traverses every tile on the grid,
# ignoring column 0 and traverses in a snaking pattern up the y axis, until reaching
# the top left, where we traverse south to 0,0
# NOTE: Only works when get_world_size() is even!
# v < < <
# v > > ^
# v ^ < <
# > > > ^
def hamiltonianCycle():
	if(get_pos_y() == get_world_size() - 1) and (get_pos_x() == 1):
		return move(West)
	elif (get_pos_x() == 0):
		# Handle the return trip down column 0 one step at a time
		if get_pos_y() > 0:
			return move(South)
		else:
			return move(East) # Back at 0,0, restart
	elif(get_pos_y() % 2 == 0) and (get_pos_x() != get_world_size() - 1):
		return move(East)
	elif(get_pos_y() % 2 != 0) and (get_pos_x() > 1):
		return move(West)
	else:
		return move(North)
		
# Tried and tested bubble sort implementation
def bubbleSort(direction, axis):
	for rowColCount in range(get_world_size()):
		for i in range(get_world_size()-1):
			swapped = False
			for j in range(get_world_size()-i-1):
				if(measure() > measure(direction)):
					swap(direction)
					swapped = True
				move(direction)
			# Important - reset to start at each iteration
			if(axis == X_AXIS):
				goto(0, rowColCount)
			else:
				goto(rowColCount, 0)
			if not swapped:
				break
				
		if(axis == X_AXIS):
			move(North)
		else:
			move(East)
			
# Zero param wrapper for cocktail sort to enable megafarm
def cocktailSortEast():
	cocktailSort(East, X_AXIS, False)
	
# Zero param wrapper for cocktail sort to enable megafarm
def cocktailSortNorth():
	cocktailSort(North, Y_AXIS, False)
			
# Modified Bubble Sort algorithm, sorts in both directions rather than returning to
# the start of each row every iteration, same time complexity but faster actual timing
def cocktailSort(direction, axis, traverse = True):
	count = 1
	if (traverse):
		count = get_world_size()
	for rowColCount in range(count):
		swapped = True
		start = 0
		end = get_world_size() - 1
		while(swapped):
			swapped = False
			
			# Sort forwards
			for i in range(start, end):
				if(measure() > measure(direction)):
					swap(direction)
					swapped = True
				move(direction)
			
			if(not swapped):
				break
			
			# We can guarantee most recent we swapped is correct now, so ignore it
			end = end - 1
			move(oppositeDir[direction])
			
			# Sort backwards
			for i in range(end-1, start-1, -1):
				if (measure() < measure(oppositeDir[direction])):
					swap(oppositeDir[direction])
					swapped = True
				move(oppositeDir[direction])
			
			# We can guarantee most recent we swapped is correct now, so ignore it
			start = start + 1
			move(direction)
			
		if(traverse):
			# Move to next starting pos
			if(axis == X_AXIS):
				goto(0, rowColCount)
				move(North)
			else:
				goto(rowColCount, 0)
				move(East)
	
# Sends the drone to the given (x,y) coordinate by traversing along the x axis, then
# the y axis, will optionally go off the end of the farm when faster if useInverse is true
def goto(x, y, useInverse = True):
	successfulX = moveAxis(East, get_pos_x, x, useInverse)
	successfulY = moveAxis(North, get_pos_y, y, useInverse)
	return successfulX and successfulY
			
# Moves along a given axis until the desiredPos is reached
def moveAxis(posDir, posCheck, desiredPos, useInverse):
	# Calculate if it's faster to go off the end of the farm by:
	# Calculate how many steps to reach the tile - Math.abs(posCheck() - desiredPos)
	# If it's larger than half the size of the farm, it's faster to go off the end
	inverse = (Math.abs(posCheck() - desiredPos) > get_world_size() / 2) and useInverse
	originPos = posCheck()
	while(posCheck() != desiredPos):
		nextDir = posDir
		# Horrible conditional, but it makes sense and works
		# 1. If the would be travelling in the posDir direction, but it would be faster to go off the end
		# 2. If we would be travelling in the opposite of posDir, and it would NOT be faster to go off the end
		if((originPos - desiredPos <= 0) and (inverse == True)) or ((originPos - desiredPos >= 0) and (inverse == False)):
			nextDir = oppositeDir[nextDir]

		if (move(nextDir) == False):
			return False
	return True
	
# Moves around the map like a snake
# > v >
# ^ v ^ 
# ^ > ^
# This minimises the delay of going off the end of the map and waiting to reach the other side
def moveToNext():
	# If the column we're in is even, move North until we're at row world_size
	if(get_pos_x() % 2 == 0) and (get_pos_y() != get_world_size() - 1):
		move(North)
	# If the column we're in is odd, move South until we're at 0
	elif(get_pos_x() % 2 != 0) and (get_pos_y() != 0):
		move(South)
	else:
		move(East)
		
# Moves around the map like a snake
# > > >
# ^ < < 
# > > ^
# This minimises the delay of going off the end of the map and waiting to reach the other side
def moveToNextHorizontal():
	# If the column we're in is even, move East until we're at column world_size
	if(get_pos_y() % 2 == 0) and (get_pos_x() != get_world_size() - 1):
		move(East)
	# If the column we're in is odd, move West until we're at 0
	elif(get_pos_y() % 2 != 0) and (get_pos_x() != 0):
		move(West)
	else:
		move(North)
		
# Returns to (0,0), not particularly useful, but I used this before I found out clear() returns you
def returnToStart():
	# This method used to be more complex before the goto method existed, keeping for backwards compatibility
	goto(0, 0)