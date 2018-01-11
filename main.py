#----------------------------------------------------------
# Main purpose for the main function is to do a time sweep, 
# and thus record the data.
#----------------------------------------------------------

# Specified Parameters
MEASURE_FREQUENCY = 0.05  #Unit:HZ
TURN_CHECK_PERIOD = 4  #Unit:s
FILE_NAME = "Princeton.csv"
START_LAT = 40.338321
START_LNG = -74.655101 #For Texas1
ALT_CORRECTION = 53.75 #For Princeton
#ALT_CORRECTION = 93.038
OUTPUT_NAME = 'result'
CORRECTION_COEFFICIENT = 1.2
HTML_OPEN_COMMAND = 'firefox'
MODE = 0
# MODE: 0 for driving, 1 for walking, 2 for taking train, 3 for flying

import string
import os
from TURN import *
from READ_DATA import *
from DISTANCE import *
from LATLNG import *
import MAPS

Turn = turn(MEASURE_FREQUENCY, TURN_CHECK_PERIOD)
Data = data(FILE_NAME)
Distance = distance(Data.getCorrection())
Latlng = latlng()
Mapcorrection = MAPS.map_analysis(0)

writedump = ''
# Read & analyze data
for count in range ( int((len(Data.d) - 1)*(MEASURE_FREQUENCY / 5.0))):
	line = int(count / (MEASURE_FREQUENCY / 5.0))
	Data.update_Time(line)
	Turn.update(Data.getDirection_True_North(line))
	if (MODE == 0):
		Distance.update_automobile(Data.getAcc_Y(line), Data.getDM_Pitch(line), Data.getStatus(line), Data.getmsecond())	
	elif (MODE == 1):
		Distance.update_walk(Data.getWalk_Distance(line))
	elif (MODE == 2):
		Distance.update_train()
	elif (MODE == 3):
		Distance.update_plain()
	# Initialization
	if line == 0:
		time_second = Data.getsecond()
		time_total_second = Data.get_total_second()
		writedump = writedump + str(Data.get_Latitude(line)) + ',' + str(Data.get_Longitude(line)) + '\n'
	# Do a turning analyse every TURN_CHECK_PERIOD
	print Data.getsecond()
	if (Data.getsecond() + 60 - time_second) % 60 >= TURN_CHECK_PERIOD:
		time_second = Data.get_total_second()
		if Turn.check() == 1:
			direction = Turn.getdirection()
			length = CORRECTION_COEFFICIENT * Distance.getDistance()
			writedump = writedump + str (Data.get_total_second() - time_total_second) + '  ' + str(direction) + '  ' + \
			str(length) + '  ' + 'm' + '  ' + str(Data.get_altitude(line) + ALT_CORRECTION) + '  '+ \
			str(Data.get_Latitude(line)) + '	' + str(Data.get_Longitude(line)) + '\n'
			time_total_second = Data.get_total_second()

length = CORRECTION_COEFFICIENT * Distance.getDistance()
writedump = writedump + str (Data.get_total_second() - time_total_second) + '  ' + str(Turn.get_last_direction()) + '  ' + str(length) +\
'  ' +  'm'  + '  ' + str(Data.get_altitude(line) + ALT_CORRECTION) + '  ' + str(Data.get_Latitude(line)) + '	' + str(Data.get_Longitude(line)) + '\n'

Data.close()

# Output data
fudge = open(OUTPUT_NAME,'w')
fudge.writelines(writedump)
fudge.close()
#Latlng.compute_and_write(OUTPUT_NAME)
#Latlng.html_generate()
#Mapcorrection.get_correction()
MAPS.get_result_tree(0)
#os.system( str(HTML_OPEN_COMMAND) + ' maptest.html &')
#os.system( str(HTML_OPEN_COMMAND) + ' mapfinal.html &')

