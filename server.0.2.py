# imports

import tobii_research as tobii

import json, signal, sys, time
import multiprocessing, threading
from Queue import Empty

from imports.websocket_server import WebsocketServer


def printWithTime(message):
	outputStr = time.strftime("%Y.%m.%d.at.%H.%M.%S") + ": " + message
	print outputStr

def initWebSocketServer(eyetrackerController):

	wsPort 		= 8080
	wsServer 	= WebsocketServer(wsPort)

	def onNewClient(client, server):
		# print("New client connected and was given id %d" % client['id'])
		printWithTime("New client connected")

	def onMessageReceived(client, server, message):

		messageDict = json.loads(message)

		if "request" in messageDict:

			if not messageDict["request"] == "reportStatus":
				# print "New client request: " + messageDict["request"]
				printWithTime("New client request: " + messageDict["request"])

			if messageDict["request"] == "startDataCollection":
				eyetrackerController.startDataCollection()

			if messageDict["request"] == "stopDataCollection":
				eyetrackerController.stopDataCollection()

			if messageDict["request"] == "reportStatus":
				controllerStatus = eyetrackerController.getStatusAsJson()
				server.send_message_to_all(controllerStatus)

			if messageDict["request"] == "dumpAttachment":
				
				if messageDict["attachment"]:
					
					fileName = "clientDump." + time.strftime("%Y.%m.%d.at.%H.%M.%S") + ".out"
					outputFile = open(fileName, "ab") # open for writing, append to an existing file, open in binary mode (don't auto-convert \n characters), default system buffer
					
					attachmentStr = json.dumps(messageDict["attachment"])
					outputFile.write(attachmentStr + "\n")

				else:
					# print "Got a request to dump attachment but no attachment, did nothing."
					printWithTime("Got a request to dump attachment but no attachment, did nothing.")

		else:
			# print "Got a JSON message without a 'request' field, couldn't process."
			printWithTime("Got a JSON message without a 'request' field, couldn't process.")

	wsServer.set_fn_new_client(onNewClient)
	wsServer.set_fn_message_received(onMessageReceived)

	eyetrackerController.setWebsocketServer(wsServer)

	# ######################

	# wsServer.run_forever()

	server_thread = threading.Thread(target=wsServer.run_forever)
	
	# exit the server thread when the main thread terminates
	# server_thread.daemon = True 	

	# the above line causes this app to exit immediately after last line of init() is executed
	# the dumping process isn't activated until someone calls startDumpingData() - which means clicking a button in the web client - so there's nothing else running
	
	server_thread.start()

	# ######################

	# print("Websocker server initiated.")
	printWithTime("Websocker server initiated.")

	return server_thread


def dumpingProcessCode(dataQueue, lock):

	def printWithLock(message):
		lock.acquire()
		printWithTime(message)
		lock.release()

	def formatGazeData(data):

		outputStr = ""

		# append right eye data
		outputStr += str(data["right_gaze_origin_validity"]) + "\t"
		outputStr += str(data["right_gaze_origin_in_trackbox_coordinate_system"][0]) + "\t" + str(data["right_gaze_origin_in_trackbox_coordinate_system"][1]) + "\t" + str(data["right_gaze_origin_in_trackbox_coordinate_system"][2]) + "\t"
		outputStr += str(data["right_gaze_origin_in_user_coordinate_system"][0]) + "\t" + str(data["right_gaze_origin_in_user_coordinate_system"][1]) + "\t" + str(data["right_gaze_origin_in_user_coordinate_system"][2]) + "\t"
		outputStr += str(data["right_gaze_point_validity"]) + "\t"
		outputStr += str(data["right_gaze_point_in_user_coordinate_system"][0]) + "\t" + str(data["right_gaze_point_in_user_coordinate_system"][1]) + "\t" + str(data["right_gaze_point_in_user_coordinate_system"][2]) + "\t"
		outputStr += str(data["right_gaze_point_on_display_area"][0]) + "\t" + str(data["right_gaze_point_on_display_area"][1]) + "\t"
		outputStr += str(data["right_pupil_validity"]) + "\t" + str(data["right_pupil_diameter"]) + "\t"

		# append left eye data
		outputStr += str(data["left_gaze_origin_validity"]) + "\t"
		outputStr += str(data["left_gaze_origin_in_trackbox_coordinate_system"][0]) + "\t" + str(data["left_gaze_origin_in_trackbox_coordinate_system"][1]) + "\t" + str(data["left_gaze_origin_in_trackbox_coordinate_system"][2]) + "\t"
		outputStr += str(data["left_gaze_origin_in_user_coordinate_system"][0]) + "\t" + str(data["left_gaze_origin_in_user_coordinate_system"][1]) + "\t" + str(data["left_gaze_origin_in_user_coordinate_system"][2]) + "\t"
		outputStr += str(data["left_gaze_point_validity"]) + "\t" + str(data["left_gaze_point_in_user_coordinate_system"][0]) + "\t" + str(data["left_gaze_point_in_user_coordinate_system"][1]) + "\t" + str(data["left_gaze_point_in_user_coordinate_system"][2]) + "\t"
		outputStr += str(data["left_gaze_point_on_display_area"][0]) + "\t" + str(data["left_gaze_point_on_display_area"][1]) + "\t"
		outputStr += str(data["left_pupil_validity"]) + "\t" + str(data["left_pupil_diameter"]) + "\t"

		# append timestamps
		outputStr += str(data["system_time_stamp"]) + "\t" + str(data["device_time_stamp"]) + "\t"
		outputStr += str("{0:.6f}".format(time.time()))

		return outputStr

	# create new gaze data file

	fileName = "gazeData." + time.strftime("%Y.%m.%d.at.%H.%M.%S") + ".out"
	outputFile = open(fileName, "ab") # open for writing, append to an existing file, open in binary mode (don't auto-convert \n characters), default system buffer


	# generate a header

	header = ""

	header += "rightGazeOriginValidity" + "\t" + "rightGazeOriginTCSx" + "\t" + "rightGazeOriginTCSy" + "\t" + "rightGazeOriginTCSz" + "\t" + "rightGazeOriginUCSx" + "\t" + "rightGazeOriginUCSy" + "\t" + "rightGazeOriginUCSz" + "\t"
	header += "rightGazePointValidity" + "\t" + "rightGazePointUCSx" + "\t" + "rightGazePointUCSy" + "\t" + "rightGazePointUCSz" + "\t" + "rightGazePointDAx" + "\t" + "rightGazePointDAy" + "\t"
	header += "rightPupilValidity" + "\t" + "rightPupilDiameter" + "\t"

	header += "leftGazeOriginValidity" + "\t" + "leftGazeOriginTCSx" + "\t" + "leftGazeOriginTCSy" + "\t" + "leftGazeOriginTCSz" + "\t" + "leftGazeOriginUCSx" + "\t" + "leftGazeOriginUCSy" + "\t" + "leftGazeOriginUCSz" + "\t"
	header += "leftGazePointValidity" + "\t" + "leftGazePointUCSx" + "\t" + "leftGazePointUCSy" + "\t" + "leftGazePointUCSz" + "\t" + "leftGazePointDAx" + "\t" + "leftGazePointDAy" + "\t"
	header += "leftPupilValidity" + "\t" + "leftPupilDiameter" + "\t"

	header += "systemTimeStamp" + "\t" + "deviceTimeStamp" + "\t"
	header += "pythonTimeStamp"

	outputFile.write(header + "\n")


	# write incoming data

	queueItem = None

	while True:

		try:

			queueItem = dataQueue.get()	# blocks by default until a queue item is available

			if queueItem == 'stop':
				printWithLock("Gaze dumping process received a 'stop' command, exiting")
				# print "Gaze data dumping thread received a 'stop' command, exiting"
				break

			# write to file
			outputFile.write(formatGazeData(queueItem) + "\n")

		except Empty:
			# this is raised if queue was empty when .get(block=False) was called, or if 
			# timeout for .get(block=True, timeout) was exceeded without receiving a queue item
			printWithLock("Gaze dumping queue raised an 'empty' exception, exiting")
			# print "Gaze data dumping queue raised an 'empty' exception, exiting"
			break

		except KeyboardInterrupt:
			# this won't be caught until the process is unblocked (e.g. by sending a "stop" item down the queue)
			printWithLock("Gaze dumping process caught a KeyboardInterrupt exception, exiting")
			# print "Gaze data dumping thread caught a KeyboardInterrupt exception, exiting"
			break

	# the lines below are called after the infinite loop is broken

	# close file
	outputFile.close()
	printWithLock("Gaze dumping process closed output file successfully")
	# print "Gaze data dumping thread closed output file successfully"


class eyetrackerController:

	# self:
		# tracker
		# gotData
		# dataQueue

	def __init__(self):
		self.connectedToEyetracker = False
		self.collectingData = False
		self.processLock = multiprocessing.Lock()

	def locateEyetracker(self):

		# found = False

		# print("Looking for the eyetracker.")
		printWithTime("Looking for the eyetracker.")

		# while not found:
		while not self.connectedToEyetracker:

			try:

				eyetrackers = tobii.find_all_eyetrackers()

				if eyetrackers:

					# print "Found the eyetracker at " + eyetrackers[0].address
					printWithTime("Found the eyetracker at " + eyetrackers[0].address)

					self.tracker = eyetrackers[0]

					# check if any calibration data is in place
					if self.tracker.retrieve_calibration_data() is None:
						
						# print "No calibration data loaded"
						printWithTime("No calibration data loaded")
					
					else:

						fileName = "calibrationData." + time.strftime("%Y.%m.%d.at.%H.%M.%S") + ".out"
						outputFile = open(fileName, "wb")

						outputFile.write(self.tracker.retrieve_calibration_data())

						# print "Eyetracker has calibration data loaded, a copy was saved to " + fileName
						printWithTime("Eyetracker has calibration data loaded, a copy was saved to " + fileName)

					# subscribe to status notifications
					self.tracker.subscribe_to(tobii.EYETRACKER_NOTIFICATION_CONNECTION_LOST, self.onConnectionLost, True)
					self.tracker.subscribe_to(tobii.EYETRACKER_STREAM_ERRORS, self.onStreamErrors, True)
					self.tracker.subscribe_to(tobii.EYETRACKER_NOTIFICATION_CONNECTION_RESTORED, self.onConnectionRestored, True)

					# found = True
					self.connectedToEyetracker = True

				else:
					# print "Failed to locate the eyetracker."
					printWithTime("Failed to locate the eyetracker.")
					time.sleep(3)
					# print "Attempting to search again."
					printWithTime("Attempting to search again.")
			
			except tobii.EyeTrackerInternalError:
				# print "EyeTrackerInternalError exception caught while attempting to locate the eyetracker. Attempting to search again."
				printWithTime("EyeTrackerInternalError exception caught while attempting to locate the eyetracker. Attempting to search again.")

	def subscribe(self):
		if self.tracker:
			self.tracker.subscribe_to(tobii.EYETRACKER_GAZE_DATA, self.onGazeData, True) # last parameter makes gaze data a dictionary instead of a custom object
			# print "Subscribed to gaze data."
			printWithTime("Subscribed to gaze data.")
		else:
			# print "Can't subscribe to gaze data, no eyetracker found."
			printWithTime("Can't subscribe to gaze data, no eyetracker found.")

	def unsubscribe(self):
		
		if self.tracker:
			
			self.tracker.unsubscribe_from(tobii.EYETRACKER_GAZE_DATA)
			self.collectingData = False
			
			# print "Unsubscribed from gaze data."
			# printWithTime("Unsubscribed from gaze data.")
			self.printWithLock("Unsubscribed from gaze data.")

		else:
			# print "Can't unsubscribe from gaze data, no eyetracker found. Also, this shouldn't be happening."
			printWithTime("Can't unsubscribe from gaze data, no eyetracker found. Also, this shouldn't be happening.")

	def onGazeData(self, data):

		self.collectingData = True	# this will be done an awful lot of times; but, it's a direct indicator that data is coming

		# dump data to disk
		self.dataQueue.put(data)

		# forward data to client
		# if data["right_gaze_point_validity"] and data["left_gaze_point_validity"]:

		# 	screenX = 1920
		# 	screenY = 1080

		# 	lx = int(data["left_gaze_point_on_display_area"][0] * screenX)
		# 	ly = int(data["left_gaze_point_on_display_area"][1] * screenY)
		# 	rx = int(data["right_gaze_point_on_display_area"][0] * screenX)
		# 	ry = int(data["right_gaze_point_on_display_area"][1] * screenY)

		# 	jsonData = '{"gazeData": true, "lx":' + str(lx) + ', "ly":' + str(ly) + ', "rx":' + str(rx) + ', "ry":' + str(ry) + '}'

		# 	self.wsServer.send_message_to_all(jsonData)

	def onConnectionLost(self, event):

		# print "Received EYETRACKER_NOTIFICATION_CONNECTION_LOST event:"
		printWithTime("Received EYETRACKER_NOTIFICATION_CONNECTION_LOST event:")
		print event

		self.connectedToEyetracker = False
		self.collectingData = False

		# the eye tracker restores the connection on its own
		# it also restarts the data collection process, if ongoing at the time of the disconnect (tested by pulling out the cord)
		# EYETRACKER_NOTIFICATION_CONNECTION_RESTORED is sent once it's back online
		# an EYETRACKER_STREAM_ERRORS was sent prior to EYETRACKER_NOTIFICATION_CONNECTION_LOST, notifying of failure to sync timestamps

	def onConnectionRestored(self, event):
		
		# print "Received EYETRACKER_NOTIFICATION_CONNECTION_RESTORED event:"
		printWithTime("Received EYETRACKER_NOTIFICATION_CONNECTION_RESTORED event:")
		print event

		self.connectedToEyetracker = True

	def onStreamErrors(self, event):
		# print "Received EYETRACKER_STREAM_ERRORS event:"
		printWithTime("Received EYETRACKER_STREAM_ERRORS event:")
		print event

	def startDumpingData(self):

		self.dataQueue = multiprocessing.Queue()

		# self.dumpingProcess = multiprocessing.Process(target=self.dumpingProcessCode, args=(self.dataQueue,))						# pass an instance method
		# self.dumpingProcess = multiprocessing.Process(target=eyetrackerController.dumpingProcessCode, args=(self.dataQueue,))		# pass a static method
		self.dumpingProcess = multiprocessing.Process(target=dumpingProcessCode, args=(self.dataQueue,self.processLock))			# pass a global function
		self.dumpingProcess.start()

	def stopDumpingData(self):
		
		if hasattr(self, "dataQueue"):
			
			# break the loop in the dumping process
			self.dataQueue.put("stop")
			
			# printWithTime("Placed 'stop' into the data dumping queue")
			self.printWithLock("Placed 'stop' into the data dumping queue")

	def startDataCollection(self):
		self.startDumpingData()
		self.subscribe()

	def stopDataCollection(self):
		self.unsubscribe()
		self.stopDumpingData()

	def getStatusAsJson(self):
		return '{"statusReport": {"connectedToEyetracker": ' + str(self.connectedToEyetracker).lower() + ', "collectingData": ' + str(self.collectingData).lower() + '}}'

	def setWebsocketServer(self, wsServer):
		self.wsServer = wsServer

	def stopWebSocketServer(self):
		self.wsServer.shutdown()
		self.wsServer.server_close()
		printWithTime("Shut down the websocket server")

	def signalHandler(self, signal, frame):
		
		# printWithTime("Caught SIGINT")
		self.printWithLock("Caught SIGINT")

		# unsubscribe from gaze data
		self.stopDataCollection()
		
		# Calling self.unsubscribe() isn't enough - it seems that Ctrl-C doesn't make it's way into 
		# dumpingProcessCode() until I pass something down the queue to unblock it.

		# stop websocket server
		self.stopWebSocketServer()

		printWithTime("Clean-up done, exiting")

		sys.exit(0)

	def printWithLock(self, message):
		self.processLock.acquire()
		printWithTime(message)
		self.processLock.release()


def init():

	# init eyetracker controller and locate the eyetracker
	controller = eyetrackerController()
	controller.locateEyetracker()

	# init websocker server
	serverThread = initWebSocketServer(controller)

	# override Ctrl-C for clean exit
	signal.signal(signal.SIGINT, controller.signalHandler)

	# prevent the main process from exiting
	# this keeps the signal handler active
	while True:
		time.sleep(60) # this intercepts Ctrl+C fine
		# pass

	# serverThread.join() # this doesn't intercept Ctrl+C

if __name__ == '__main__':
	init()
