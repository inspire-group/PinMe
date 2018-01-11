import urllib3
import googlemaps
import lxml.etree as ET
import xml.dom
from LATLNG import get_altitude
from LATLNG import get_distance
from LATLNG import get_direction
from LATLNG import get_angle
SPEED = 10
MAP_NAME = 'Princeton'
# print root.attrib

######################################################################
# PART 1 : Tree cleaning
######################################################################
def get_way_name(way_root):
	if way_root.tag != 'way':
		return 0
	for way_child in way_root:
		if (len(way_child.attrib) == 2):					
			if way_child.attrib['k']== 'name':
				return way_child.attrib['v']
	return 0

def check_way_for_drive(way_root):
	if get_way_name(way_root) == 0:
		return 0
	for way_child in way_root:
		if (len(way_child.attrib)) == 2:
			if (way_child.attrib['k'] == 'highway') & (way_child.attrib['v'] == 'service'):
				return 0
			if (way_child.attrib['k'] == 'motor_vehicle') & (way_child.attrib['v']=='yes'):
				return 1
			if (way_child.attrib['k'] == 'highway') &\
			 ((way_child.attrib['v'] == 'primary') |\
			 (way_child.attrib['v'] == 'secondary')|\
			 (way_child.attrib['v'] == 'residential')):
				return 1
	return 0

def correct_way_name(way_root):
	if way_root.tag != 'way':
		return 0
	for way_child in way_root:
		if (len(way_child.attrib) == 2):					
			if way_child.attrib['k']== 'name':
				name = str(way_child.attrib['v'])
				if name[ (len(name) - 2) : ] == 'Rd':
					name = name[ 0 : (len(name) -2 )] + 'Road'
				way_child.attrib['v'] = name
				return way_child.attrib['v']
	return 0


def tree_clean():
	tree = ET.parse(MAP_NAME + '.osm')
	root = tree.getroot()
#-----------------------------------------------------------------------------
# Check all the roads for drive, and delete the non-drivable roads
	total_element = len (root)
	i = 0
	while (i < total_element):
		if (root[i].tag == 'way'):
			if (check_way_for_drive(root[i]) == 1):
				print get_way_name(root[i])
				correct_way_name(root[i])
			if (check_way_for_drive(root[i]) == 0):
				# remove will reduce the total element number, meanwhile, all the element after the deleted node will
				# move forward by 1 unit. Thus i-=1 and total_element -= 1
				root.remove(root[i])
				i -= 1
				total_element -= 1
		if (root[i].tag == 'relation'):
			root.remove(root[i])
			i -= 1
			total_element -= 1
		i += 1
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------
# Check all the nodes possible for TURN, and delete non-connecting points
	total_element = len (root)
	i = 0
	while (i < total_element):
		print i
		count = 0
		if root[i].tag == 'way':
			break
		if root[i].tag == 'node':
			node_id = (root[i].attrib['id'])
			for child in root:
				if child.tag != 'way':
					continue
				for grandchild in child:
	#				print grandchild.attrib
					if len(grandchild.attrib) == 1:
						road_node_id = grandchild.attrib['ref']
						if road_node_id == node_id:
							count += 1
		if count < 2:
			root.remove(root[i])
			total_element -= 1
			i -= 1
		else:
			lat = float(root[i].attrib['lat'])
			lng = float(root[i].attrib['lon'])
			altitude = get_altitude(lat, lng)
			root[i].set('alt', str(altitude))
		i += 1
#------------------------------------------------------------------------------
# remove all the non_turnable node stored in the way
	total_element = len (root)
	i = 0
	while (i < total_element):
		if root[i].tag == 'way':
			j = 0
			way_length = len (root[i])
			while (j < way_length):
				if len(root[i][j].attrib) == 1:
					road_node_id = root[i][j].attrib['ref']
					exist = 0
					for child in root:
						if child.tag == 'node':
							node_id = child.attrib['id']
							if node_id == road_node_id:
								exist = 1
								break
					if exist == 0:
						root[i].remove(root[i][j])
						j -= 1
						way_length -= 1
				j += 1
		i += 1	
	tree.write(MAP_NAME + '_outmap.xml')
#------------------------------------------------------------------------------------
#####################################################################################

#-------------------------------------------------------------------------------------
# Use Google Map API to auto correct the route, and write the output file
#-------------------------------------------------------------------------------------
class map_analysis:
	def __init__(self, map_init):
		self.init = map_init
		self.Gmaps = googlemaps.Client(key='AIzaSyDy3tIldJmugqv8Vmnpu69FPrSLrttXwR4')
		self.vb = 1
		return None
	def get_correction(self):
		self.read = open ('latlng', 'r')
		self.data = self.read.readlines()
		self.path = []
		for i in range (len(self.data)):
#			print 'cc'
			self.path.insert(i,eval(self.data[i]))
		self.snap = self.Gmaps.snap_to_roads(self.path, interpolate = True)
		self.writedump = ''
#		print self.snap
		for i in range (len(self.snap)):
			self.writedump = self.writedump + '{ "lat": ' + str(self.snap[i]['location']['latitude']) +', "lng": ' + str(self.snap[i]['location']['longitude']) +\
			'}, \n'
		self.htmlinput = open ('map.html', 'r')
		self.htmlinputdata = self.htmlinput.readlines()
		self.htmloutput = open ('mapfinal.html', 'w')
		for i in range (35):
			self.htmloutput.write(str(self.htmlinputdata[i]))
		self.htmloutput.writelines(self.writedump)
		for i in range (len(self.htmlinputdata) - 35):
			self.htmloutput.write(str(self.htmlinputdata[i+35]))
		self.htmlinput.close()
		self.htmloutput.close()
		self.read.close()

def read_latlng(node_id):
	for node_child in map_root:
		if (node_child.tag == 'node') and (node_child.attrib['id'] == node_id):
				return (float(node_child.attrib['lat']), float(node_child.attrib['lon']))
	return (0,0)


def read_altitude(node_id):
	for node_child in map_root:
		if (node_child.tag == 'node') and (node_child.attrib['id'] == node_id):
				return float(node_child.attrib['alt'])
	return 0

def Add_possible_start_point(alt):
	for child in map_root:
		if child.tag != 'node':
			continue
		node_id = (child.attrib['id'])
		error = abs( alt - read_altitude(str(node_id)))
		if error <= 3:
#			print node_id
			new_node = ET.Element('node', ID = str(node_id), depth = '1', error = str(error) , distance = '0')
			result_root.append(new_node)
def Add_IDs_from_way(depth, node, way_root, start_id, orientation, height, time_interval):
	for way_child in way_root:
		if len(way_child.attrib) != 1:
			continue
		possible_id = way_child.attrib['ref']
		if possible_id == start_id:
			continue
		(lat0, lng0) = read_latlng(start_id)
		(lat1, lng1) = read_latlng(str(possible_id))
		direction = get_direction(lat0, lng0, lat1, lng1)
		distance = get_distance(lat0, lng0, lat1, lng1)
		angle_error =  get_angle(float(direction), float(orientation))
		if start_id =='104068339' and possible_id == '104017838' and 0 :
			print angle_error
		if angle_error >= 30:
			continue
		temp_error = abs(read_altitude(possible_id) - height) + (angle_error / 30) + ((time_interval * SPEED) / (20 * distance))
		if abs(read_altitude(possible_id) - height) >=4.0:
			continue
		if temp_error >= 4:
			continue
		add = 1
		for element in result_tree.iter('*'):
			if element.attrib['depth'] == str(depth) and element.attrib['ID'] == str(possible_id):
				add = 0
				break
		if add == 1:
			new_node = ET.Element('node', ID = str(possible_id), depth = str(depth), error = str(temp_error),\
				distance = str((distance) + float(node.attrib['distance'])),\
				latlng =  str(lat1) + ',' + str(lng1))
			node.append(new_node)

def Add_next_layer(depth, direction, altitude, time):
	for node in result_tree.iter('*'):
		if node.attrib['depth'] != str(depth - 1):
			continue
#		print node.attrib['ID']
		current_id = node.attrib['ID']
		for child in map_root:
			if child.tag != 'way':
				continue
			for grandchild in child:
				if len(grandchild.attrib) != 1 or ((grandchild.attrib['ref']) != current_id):
					continue
				way_name = get_way_name(child)
				for son in map_root:
					if get_way_name(son) != way_name:
						continue
					Add_IDs_from_way(depth, node, son, current_id, direction, altitude, time)
	return 1
def get_result_tree(TREE_CLEAN):
	global map_tree
	global map_root
	global result_root
	global result_tree
	if TREE_CLEAN == 1:
		tree_clean()
	map_tree = ET.parse(MAP_NAME + '_outmap.xml')
	map_root = map_tree.getroot()
	f = open ('result', 'r')
	d = f.readlines()
	writedump = ''
	neglect = 11
	for k in range (neglect):
#------ start building the tree structure
		result_root = ET.Element('root', depth = '0', ID ="root", error = '0')
		result_tree = ET.ElementTree(result_root)
		altitude = float(d[k + 1].split()[4])
		print 'start_point_alt: ' + str(altitude)
		Add_possible_start_point(altitude)
		for m in range (len(d)-2- neglect):
			i = k + m
			altitude = float(d[i+2].split()[4])
			print altitude
#			print 'analyzing step: ' + str(i) + '  altitude:' + str(altitude)
			direction = float(d[i+2].split()[1])
			time = float(d[i+2].split()[0])
			Add_next_layer(i+2 - k, direction, altitude, time)
		final_lat = float(d[i+2].split()[5])
		final_lng = float(d[i+2].split()[6])
		total_error = 1.0
		total_results = 0
		for node in result_tree.iter('*'):
			if node.attrib['depth'] == str(len(d) - 1 - neglect):
				total_results += 1
				node_id = node.attrib['ID']
				(guess_lat, guess_lng) = read_latlng(node_id)
				distance_error = get_distance(guess_lat, guess_lng, final_lat, final_lng)
				overall_distance = float(node.attrib['distance'])
#				print guess_lat,guess_lng
				if distance_error/overall_distance <= total_error:
					total_error = distance_error/overall_distance
		print total_error
		writedump = writedump +'	' + str(total_error) + '	' + str(total_results)
		total_results = 0
		if k==0:
			result_tree.write('analysis_result_tree.xml', pretty_print=True)
	writedump = writedump + '\n'
	f = open('num_of_turns', 'a')
	f.writelines(writedump)
	f.close()
#test = result_tree()
#test.get_correction()
'''
def analyze_road(way_root, start_id, orientation, height, time_interval):
	error = 100
	best_guess_id = 0
	for way_child in way_root:
		if len(way_child.attrib) != 1:
			continue
		possible_id = way_child.attrib['ref']
		if possible_id == start_id:
			continue
		(lat0, lng0) = read_latlng(start_id)
		(lat1, lng1) = read_latlng(str(possible_id))
		direction = get_direction(lat0, lng0, lat1, lng1)
		distance = get_distance(lat0, lng0, lat1, lng1)
		angle_error =  get_angle(float(direction), float(orientation))
		if angle_error >= 30:
			continue
		temp_error = abs(read_altitude(possible_id) - height) + (angle_error / 30) + ((time_interval * SPEED) / (5 * distance))
		if temp_error >= 3:
			continue
		if (error >= temp_error):
			best_guess_id = possible_id
			error = temp_error
	return (best_guess_id, error)
				
			
def find_next_turn_id(ID_0, Toward, Alt, Time):
	error = 10
	next_node_id = 0
	final_way_name = ''
	for child in map_root:
		if child.tag != 'way':
			continue
		for grandchild in child:
			if len(grandchild.attrib) != 1 or ((grandchild.attrib['ref']) != ID_0):
				continue
			way_name = get_way_name(child)
			for son in map_root:
				if get_way_name(son) != way_name:
					continue
				(node_id, temp_error) = analyze_road(son, ID_0, Toward, Alt, Time)
				if temp_error <= error:
					error = temp_error
					next_node_id = node_id
					final_way_name = way_name
	return (next_node_id, error, final_way_name)
'''

'''for child in map_root:
	if child.tag != 'node':
		continue
#	current_id = 3734788110
	total_error = 0
	current_route = []
	current_id = (child.attrib['id'])
	current_route.append(current_id)
	direction = 72.46
	altitude = 29.48
	time = 60
	total_error = abs( altitude - read_altitude(str(current_id)))
	if abs( altitude - read_altitude(str(current_id))) >= 2:
		continue
	for i in range (len(d)-2):
		altitude = float(d[i+2].split()[4])
		direction = float(d[i+2].split()[1])
		time = float(d[i+2].split()[0])
		(next_id, error, way_name) = find_next_turn_id((current_id), direction, altitude, time)
		(lat, lng) = read_latlng(str(current_id))
		total_error += error
		#print next_id
		#print way_name
		current_id = (next_id)
		current_route.append(current_id)
	if total_error < lowest_error:
		lowest_error = total_error
		final_route = current_route
print final_route
print lowest_error
writedump = writedump + str(final_route)
fwrite = open ('latlngresult','w')
fwrite.writelines(writedump)
f.close()
fwrite.close()'''

