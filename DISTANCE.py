#from READ_DATA import *
import math
class distance:
#	FILE_NAME = "Lakeside_Equard_Data.csv"
#	Data = data(FILE_NAME)
	def __init__(self, Correction):
		self.acc = 0
		self.Now_velocity = 0
		self.Prev_velocity = 0
		self.distance = 0
		self.Prev_msecond = 0
		self.correction = Correction
		self.time_interval = 1
		self.Prev_distance = 0
		self.distance_interval = 0
	def update_automobile(self, Acc, DM_Pitch, Status, Time_msecond):
		self.Now_msecond = Time_msecond
		self.time_interval = (self.Now_msecond + 1000 - self.Prev_msecond) % 1000
		self.Prev_msecond = self.Now_msecond
		if (Status == 'stationary'):
			self.Now_velocity = 0
			self.acc = 0
#			print 'stay'
			return 1
		self.Now_velocity += self.acc * self.time_interval / 1000
		if self.Now_velocity < 0:
			self.Now_velocity = 0
#			print 'velocity < 0'
		self.distance += (self.Now_velocity + self.Prev_velocity) * self.time_interval / 2000
#		print time_interval
		self.acc = (- Acc - math.sin(DM_Pitch) + self.correction) * 9.81
		self.Prev_velocity = self.Now_velocity
#		print acc
#		print str(self.acc) + '	' + str(self.Now_velocity) + '	' + str(self.distance)
		return 1
	def update_walk(self, Walk_distance):
		self.distance = Walk_distance
		return 1
	def update_train(self):
		return 1
	def update_plane(self):
		return 1	
	def getDistance(self):
		self.distance_interval = self.distance - self.Prev_distance
		self.Prev_distance = self.distance
		return self.distance_interval
