import sys
import csv
import datetime

# Global Varaiables
logArray = []
filenames = []
name = ""
startTimeOfLog = ""
endTimeOfLog = ""

# Read file from command line and save each line to list "logArray"
def readFile():
	global logArray
    # Open log file
	in_file = open(sys.argv[1], "r")
	
	# Go through log file and save each line to an array.
	for line in in_file:
		logArray.append(line)
    #Close log file
	in_file.close()
	
# Remove logs that have status codes 304 and save status codes above 400 to an errorlog.
def removeNotNeededLogs():
	global logArray
	keepLogs = []
	openFile = open('errorLog.csv', 'wb')
	writeToFile = csv.writer(openFile)
	writeToFile.writerow(['Date'] + ['Time'] + ['User'] + ['Page'] + ['Status Code'])
	x = 0
	while x < len(logArray):
		status = "200"
		values = logArray[x].split()
		date = values[1]
		time = values[2]
		username = values[3]
		page = values[4]
		statusCode = values[5]
		if (str(statusCode) == status):
			if page.startswith("/site"):
				pass
			else:
				keepLogs.append(logArray[x])
		elif int(statusCode) > 400:
			writeToFile.writerow([date] + [time] + [username] + [page] + [statusCode])
		x = x + 1
	openFile.close()
	logArray = keepLogs
	
# Get benning and end time of the log
def getLogTime():
	global startTimeOfLog
	global endTimeOfLog
	global logArray
	# Get start and end time of log
	getStartTimeOfLog = logArray[0].split()
	getEndTimeOfLog = logArray[len(logArray) - 1].split()
	startTimeOfLog = getStartTimeOfLog[1] + "_" + getStartTimeOfLog[2].replace(":", "-")
	endTimeOfLog = getEndTimeOfLog[1] + "_" + getEndTimeOfLog[2].replace(":", "-")
	
# Create each user's individual file
def createCSVFiles():
	x = 0
	while x < len(logArray):
		values = logArray[x].split()
		name = values[3]
		page = values[4]
		date = values[1]
		time = values[2]
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'ab')
		writeToFile = csv.writer(openFile)
		writeToFile.writerow([page] + [date] + [time])
		openFile.close()
		x = x + 1
	
# Retrieve usernames from the log to open respective files.	
def getFileNames():
	global filenames
	match = "false"
	x = 0
	while x < len(logArray):
		values = logArray[x].split()
		name = values[3]
		if (len(filenames) == 0):
			filenames.append(logArray[x])
			match = "true"
		else:
			y = 0
			while y < len(filenames):
				val = filenames[y].split()
				nam = val[3]
				if (name == nam):
					match = "true"
				y = y + 1
		if (match == "false"):
			filenames.append(logArray[x])
		match = "false"
		x = x + 1
		
# Open Individual Files and call accessFile() to add data up.
def accessIndividualFiles():
	global name
	x = 0
	while x < len(filenames):
		values = filenames[x].split()
		name = values[3]
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'rb')
		writeToFile = csv.reader(openFile)
		# Every row in the file add it to contents[]
		contents = []
		for row in writeToFile:
			line = ' '.join(row)
			contents.append(line)
		openFile.close()
		# print "opening file " + name
		accessFile(contents)
		# print "-------------"
		x = x + 1
	
# Add data up from opened file
def accessFile(contents):
	addContents = []
	match = "false"
	# delete everything in the csv file
	open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'w')
	
	x = 0
	while x < len(contents):
		try:
			values = contents[x].split()
			page = values[0]
			startTime = values[2]
			getEndTime = contents[x+1].split()
			endTime = getEndTime[2]
			d1 = datetime.datetime.strptime(startTime, "%H:%M:%S")
			d2 = datetime.datetime.strptime(endTime, "%H:%M:%S")
			dt1 = datetime.timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
			dt2 = datetime.timedelta(hours=d2.hour, minutes=d2.minute, seconds=d2.second)
			fin = dt2 - dt1
			if len(addContents) == 0:
				addContents.append(page + " 1 " + str(fin))
			else:
				y = 0
				while y < len(addContents):
					val = addContents[y].split()
					pag = val[0]
					if pag == page:
						visits = int(val[1]) + 1
						val[1] = str(visits)
						totalTime = val[2]
						d1 = datetime.datetime.strptime(str(fin), "%H:%M:%S")
						d2 = datetime.datetime.strptime(totalTime, "%H:%M:%S")
						dt1 = datetime.timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
						dt2 = datetime.timedelta(hours=d2.hour, minutes=d2.minute, seconds=d2.second)
						total = dt1 + dt2
						addContents[y] = pag + " " + val[1] + " " + str(total)
						match = "true"
					y = y + 1
				if match == "false":
					addContents.append(page + " 1 " + str(fin))
				match = "false"
		except IndexError:
			values = contents[x].split()
			page = values[0]
			time = "00:05:00"
			if len(addContents) == 0:
				addContents.append(page + " 1 " + time)
			else:
				y = 0
				while y < len(addContents):
					val = addContents[y].split()
					pag = val[0]
					if pag == page:
						visits = int(val[1]) + 1
						val[1] = str(visits)
						totalTime = val[2]
						d1 = datetime.datetime.strptime(time, "%H:%M:%S")
						d2 = datetime.datetime.strptime(totalTime, "%H:%M:%S")
						dt1 = datetime.timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
						dt2 = datetime.timedelta(hours=d2.hour, minutes=d2.minute, seconds=d2.second)
						total = dt1 + dt2
						addContents[y] = pag + " " + val[1] + " " + str(total)
						match = "true"
					y = y + 1
				if match == "false":
					addContents.append(page + " 1 " + time)
				match = "false"
		x = x + 1
	openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'ab')
	writeToFile = csv.writer(openFile)
	# writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
	x = 0
	while x < len(addContents):
		values = addContents[x].split()
		page = values[0]
		visits = values[1]
		time = values[2]
		writeToFile.writerow([page] + [visits] + [time])
		x = x + 1
	openFile.close()
	
# Open individual files and call averageTimes() to average the total Times
def getAverageOfTotalTimes():
	global name
	x = 0
	while x < len(filenames):
		values = filenames[x].split()
		name = values[3]
		openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'rb')
		writeToFile = csv.reader(openFile)
		# Every row in the file add it to contents[]
		contents = []
		for row in writeToFile:
			line = ' '.join(row)
			contents.append(line)
		openFile.close()
		averageTimes(contents)
		x = x + 1
	
# Open individual file and average the time with visits
def averageTimes(contents):
	addContents = []
	open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'w')
	x = 0
	while x < len(contents):
		values = contents[x].split()
		page = values[0]
		visits = values[1]
		time = values[2]
		d1 = datetime.datetime.strptime(time, "%H:%M:%S")
		dt1 = datetime.timedelta(hours=d1.hour, minutes=d1.minute, seconds=d1.second)
		averageTime = dt1 / int(visits)
		addContents.append(page + " " + visits + " " + " " + time + " " + str(averageTime))
		x = x + 1
	
	openFile = open(name+'-'+startTimeOfLog+'_'+endTimeOfLog+'.csv', 'ab')
	writeToFile = csv.writer(openFile)
	writeToFile.writerow(['Page'] + ['Visits'] + ['Total Time'] + ['Average Time'])
	x = 0
	while x < len(addContents):
		values = addContents[x].split()
		page = values[0]
		visits = values[1]
		time = values[2]
		average = values[3]
		writeToFile.writerow([page] + [visits] + [time] + [average])
		x = x + 1
	openFile.close()
	
# Read a file
if (len(sys.argv) > 2) or (len(sys.argv) <= 1):
	print "To export a log file you need to..."
else:
	readFile()
	removeNotNeededLogs()
	getLogTime()
	createCSVFiles()
	getFileNames()
	accessIndividualFiles()
	getAverageOfTotalTimes()