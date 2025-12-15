water_threshold = 0.7

# Inserts a value into a MinHeap structure
# Shamelessly stolen from
# Ref: https://www.geeksforgeeks.org/dsa/introduction-to-min-heap-data-structure/
def minHeapInsert(heap, value):
	heap.append(value)
	
	index = len(heap) - 1
	while (index > 0) and (heap[(index - 1) // 2][0] > heap[index][0]):
		parentIndex = (index - 1) // 2
		heap[index], heap[parentIndex] = heap[parentIndex], heap[index]
		index = parentIndex
		
# Function to pop the smallest element from a MinHeap, ensuring the remaining
# elements are heapify'd back into order
# Shamelessly adapted from
# https://www.geeksforgeeks.org/dsa/introduction-to-min-heap-data-structure/
def minHeapPop(heap):
	if not heap:
		return None
		
	if len(heap) == 1:
		return heap.pop()
		
	minValue = heap[0]
	heap[0] = heap.pop()
	
	# Heapify the tree starting from the element at the
	# deleted index
	index = 0
	n = len(heap)
	while True:
		left_child = 2 * index + 1
		right_child = 2 * index + 2
		smallest = index

		if left_child < n and heap[left_child][0] < heap[smallest][0]:
			smallest = left_child
		if right_child < n and heap[right_child][0] < heap[smallest][0]:
			smallest = right_child

		if smallest != index:
			heap[index], heap[smallest] = heap[smallest], heap[index]
			index = smallest
		else:
			break
			
	return minValue

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
	