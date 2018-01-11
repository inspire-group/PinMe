import string
from LATLNG import get_angle
class turn:
	def __init__(self, MEASURE_FREQUENCY, TURN_CHECK_PERIOD):
		self.frequency = MEASURE_FREQUENCY
		self.period = TURN_CHECK_PERIOD
		self.direction = 11.2
		self.count = 0
		self.TotalDirection_True_North = 0
		self.init = 0
		self.prev_direction = 10.2
		self.situation = 0
		self.temp_direction = 19.2
		self.no_turn_count = 0
	def getdirection(self):
		return (self.direction)
	def getprev_direction(self):
		return (self.prev_direction)
	def get_last_direction(self):
		if self.prev_check == 0:
			return(self.direction)
		return self.temp_direction

	# For each line in the data sheet, update the turning information from the Head just after reading this line
	def update (self, Direction_True_North):
		self.count += 1.0                # this Count if used to calculate the average value
		if self.situation == 0:
			if Direction_True_North < 90.0:		# Handling some situation when direction is around 360
				self.situation = 1
			elif Direction_True_North > 270:
				self.situation = 2
			else:
				self.situation = 3
			self.TotalDirection_True_North += float (Direction_True_North)	
			return 1
		elif self.situation == 1:
			if Direction_True_North > 270:
				self.TotalDirection_True_North += float (Direction_True_North - 360)
			else:
				self.TotalDirection_True_North += float (Direction_True_North)
			return 1
		elif self.situation == 2:
			if Direction_True_North < 90:
				self.TotalDirection_True_North += float (360.0 + Direction_True_North)
			else:
				self.TotalDirection_True_North += float (Direction_True_North)
			return 1
		self.TotalDirection_True_North += float(Direction_True_North)
	def check (self):
		self.situation = 0
		self.temp_direction = (self.TotalDirection_True_North / self.count + 360) % 360

		self.count = 0
		self.TotalDirection_True_North = 0
	#	print 'temp' + str(self.temp_direction)
		# First time check is just an initialization
		if self.init == 0:
			self.direction = self.temp_direction
			self.TotalDirection_True_North = 0
			self.count = 0
			self.init = 1
			self.prev_check = 0
			self.no_turn_count = 1
			return 0

		if self.prev_check == 0:
			self.prev_direction = self.temp_direction
			if get_angle(self.temp_direction, self.direction) >= 40:
				self.prev_check = 1
				return 1
			self.direction = get_ave(self.direction, self.temp_direction, self.no_turn_count)
#			print 'MARK'
#			print self.direction
			self.no_turn_count += 1	
			return 0
		elif get_angle(self.temp_direction, self.prev_direction) <= 15:
			self.direction = self.temp_direction
#			self.prev_direction = self.temp_direction
			self.prev_check = 0
			self.no_turn_count = 1
			return 0
		self.prev_direction = self.temp_direction
		return 0
def get_ave (a0, a1, cnt):
	if (a0 >= 270) and (a1 <= 90):
		return ((a0 * cnt + a1 + 360) / (cnt + 1)) % 360
	if (a0 <= 90) and (a1 >= 270):
		return  ((a0 + 360) * cnt + a1) / (cnt + 1) % 360
	return (a0 * cnt + a1) / (cnt + 1)
