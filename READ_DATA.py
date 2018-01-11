#----------------------------------------------------------------
# Read and return correct value to the main function
#----------------------------------------------------------------
import math
import string
import os
class data:
	def __init__(self, filename):
		self.f = open (filename, 'r')
		self.d = self.f.readlines()
		self.Sum = 0
		self.Average = 0
		self.Time = time_analysis()
	def update_Time (self, line):
		TIME_ALL = self.getTime(line)
		self.Time.update(TIME_ALL)
		return 1
	def gethour (self):
		return (self.Time.time_hour)
	def getminute (self):
		return (self.Time.time_minute)
	def getsecond (self):
		return (self.Time.time_second)
	def getmsecond (self):
		return (self.Time.time_msecond)
	def gettime_hms (self):
		return (self.Time.time_hms)
	def getTime(self,line):
		return self.d[line+1].split(',')[0]
	def get_total_second (self):
		return (self.Time.time_total_second)
	def get_Latitude (self,line):
		return float(self.d[line+1].split(',')[4])
	def get_Longitude (self,line):
		return float(self.d[line+1].split(',')[5])
	def getDirection_X(self, line):
		return float(self.d[line+1].split(',')[13])
	def getDirection_Y(self, line):
		return float(self.d[line+1].split(',')[14])
	def getDirection_Z(self, line):
		return float(self.d[line+1].split(',')[15])
	def getDirection_True_North(self, line):
		return float(self.d[line+1].split(',')[16])
	def getAcc_Y(self, line):
		return float(self.d[line+1].split(',')[21])
	def getDM_Pitch(self, line):
		return float(self.d[line+1].split(',')[30])
	def getStatus (self, line):
		return str(self.d[line+1].split(',')[50])
	def getWalk_Distance (self, line):
		return float(self.d[line+1].split(',')[55])
	def get_altitude (self, line):
		return float(self.d[line+1].split(',')[61])
	def getCorrection (self):
		self.Sum = 0
		for i in range (len(self.d)-1):
			self.Sum += self.getAcc_Y(i) + math.sin(self.getDM_Pitch(i))
		self.Average = self.Sum / (len(self.d)-1)
		return self.Average
	def close(self):
		self.f.close()
		return 1

class time_analysis:
	def __init__(self):
		self.time_stamp_all = 'ss'
	def update (self, TIME_ALL):
		self.time_after_date = (str) (TIME_ALL.split()[1])
		self.time_hms = self.time_after_date.split('.')[0]
		self.time_hour = (int) (self.time_hms.split(':')[0])
		self.time_minute = (int) (self.time_hms.split(':')[1])
		self.time_second = (int) (self.time_hms.split(':')[2])
		self.time_msecond = (int) (self.time_after_date.split('.')[1])
		self.time_total_second = self.time_hour * 3600 + self.time_minute * 60 + self.time_second 
	def gethour (self):
		return (self.time_hour)
	def getminute (self):
		return (self.time_minute)
	def getsecond (self):
		return (self.time_second)
	def getmsecond (self):
		return (self.time_msecond)
	def gettime_hms (self):
		return (self.time_hms)
