### CODING CHALLENGE ###
 
first_name  = "William"
last_name   = "Clark"
 
# ----------------------------------------------------------------------
# You will be provided with a folder containing several files with '.fastq' extension.
# Your general task is to parse the files and output some useful statistics to a new file called 'summary.txt'.
# ----------------------------------------------------------------------
# Each input file name will have the following format:
# 
#   flowcell-project_subproject_method_id_code.fastq
# 
# Example: 'DV-S2_ACTTGA_L008_R1_001.fastq'
# ----------------------------------------------------------------------
# Sample file content:
# 
#   @HWI-D00351:132:C5DNLANXX:8:1101:1220:1983 2:N:0:GATCAG
#   GACTTAAGAGTTTAATATGACTTAAACATTAAAAGCTCACACTACCCCGAAATATATAATTTCACGCATACGGTGAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCC
#   +
#   BBBBBFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
#   @HWI-D00351:132:C5DNLANXX:8:1101:1685:1968 2:N:0:GATCAG
#   NCCGCTTGGAACTAGCTTTAGTAATATAATCGCGAATTTGAACAAGCCTGCTTACAATCTGGCTGCTCTCCATTGCAGGTTCTCCCCTCCCATCTTCTTCAGTCACCTGACAGTTTTGCAAGATC
#   +
#   #<<<BF//FBBFF<FFFFFFFFF<FFFFFFFFF/FFFFFFFFFFFBF<BFFFFFFFFFFFBF/BFBFFFFFFFFFFFFFFF<FFFFF<FBFFFFF<FFFFFFFFFFBFBFFFFFFFFFFFFFFFF
# ----------------------------------------------------------------------
# Each line on positions {2, 6, .. 4n + 2 ..} in the file will be a string of characters {'A', 'T', 'G', 'C', 'N'}.
# ----------------------------------------------------------------------
 
# TASKS:
#
# 1. Compute the occurrence frequency of the characters {'A', 'T', 'G', 'C'}.
# 
#   The 'summary.txt' file should contain the following format for each file:
# 
#   Example (for one file):
#
#       {
#           'filename'      : 'DV-S2_ACTTGA_L008_R1_001.fastq',
#           'flowcell'      : 'DV',
#           'project'       : 'S2',
#           'subproject'    : 'ACTTGA',
#           'method'        : 'L008',
#           'id'            : 'R1',
#           'code'          : 1,
#           'A_freq'        : 69,
#           'T_freq'        : 70,
#           'G_freq'        : 51,
#           'C_freq'        : 59
#       }
 
# 2. Generalize your script to receive a directory path that contains multiple '.fastq' files as input, from command line.
 
# 3. Parallelize your code.
 
# 4. Consider the following string S that consists entirely of characters 'A', 'T', 'G' and 'C'. Sort S efficiently.
 
S = 'GACTTAAGAGTTTAATATGACTTAAACATTAAAAGCTCACACTACCCCGAAATATATAATTTCACGCATACGGTGAGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCC'
 
def efficient_sort(s):
    return ''.join(sorted(S))
 
S_sorted = efficient_sort(S)
print(S_sorted)

import Queue
import threading
from os import walk, chdir
import time

readDirectory = raw_input(r"Please enter the directory to be read: ")
fileNames = next(walk(readDirectory))[2]
chdir(readDirectory)
fileNames = [name for name in fileNames if name[-6:] == '.fastq']
numFiles = len(fileNames)

class fastq:
	def __init__(self, fileName):
		self.fileName = fileName
		self.flowCell = fileName[0:2]
		self.project = fileName[3:5]
		self.subProject = fileName[6:12]
		self.method = fileName[13:17]
		self.id = fileName[18:20]
		self.code = fileName[21:24]
		with open(fileName, 'r') as currentFile:
		    data = currentFile.read()
		    lines = data.splitlines()
		    numLines = len(lines)
		    lines = [lines[4*i + 1] for i in xrange((numLines+2)/4)]
		self.A_freq = 0
		self.T_freq = 0
		self.G_freq = 0
		self.C_freq = 0
		for line in lines:
			for i in xrange(len(line)):
				currChar = line[i]
				if currChar == 'A':
					self.A_freq += 1
				elif currChar == 'T':
					self.T_freq += 1
				elif currChar == 'G':
					self.G_freq += 1
				elif currChar == 'C':
					self.C_freq += 1
				else:
					pass
	def write(self, writeFile):
		writeFile.write("{\n")
		writeFile.write("    'filename'      : %s,\n" % self.fileName)
		writeFile.write("    'flowcell'      : %s,\n" % self.flowCell)
		writeFile.write("    'project '      : %s,\n" % self.project)
		writeFile.write("    'subproject'    : %s,\n" % self.subProject)
		writeFile.write("    'method'        : %s,\n" % self.method)
		writeFile.write("    'id'            : %s,\n" % self.id)
		writeFile.write("    'code'          : %s,\n" % self.code)
		writeFile.write("    'A_freq'        : %s,\n" % self.A_freq)
		writeFile.write("    'T_freq'        : %s,\n" % self.T_freq)
		writeFile.write("    'G_freq'        : %s,\n" % self.G_freq)
		writeFile.write("    'C_freq'        : %s,\n" % self.C_freq)
		writeFile.write("}\n")

class readThread (threading.Thread):
	def __init__(self, threadID, name, readQueue, writeList):
		threading.Thread.__init__(self)
		self.name = name
		self.readQueue = readQueue
		self.writeList = writeList
	def run(self):
		process_data(self.name, self.readQueue, self.writeList)

def process_data(threadName, readQueue, writeList):
	while not exitFlag:
		queueLock.acquire()
		if not readQueue.empty():
			fileName = readQueue.get()
			queueLock.release()
			print "%s processing %s" % (threadName, fileName)
			writeList.append(fastq(fileName))
		else:
			queueLock.release()
		time.sleep(1)

readQueue = Queue.Queue(numFiles)
writeList = []

numReadThreads = int(raw_input(r"How many read threads? "))
threadNames = ["Thread %s" % str(i + 1) for i in xrange(numReadThreads)]

queueLock = threading.Lock()
threads = []
threadID = 1
exitFlag = 0

for threadName in threadNames:
	thread = readThread(threadID, threadName, readQueue, writeList)
	thread.start()
	threads.append(thread)
	threadID += 1

queueLock.acquire()
for name in fileNames:
	readQueue.put(name)
queueLock.release()

while not readQueue.empty():
	pass

exitFlag = 1

for t in threads:
	t.join()

print "Reading and analyses completed. Writing summary.txt"
writeFile = open("summary.txt", "w")
for item in writeList:
	item.write(writeFile)
	writeFile.write("\n")
writeFile.close()
