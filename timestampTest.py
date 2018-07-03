import tobii_research as tr
import time


# check python time vs tobii system time

tobiiSystemTime = tr.get_system_time_stamp()
pythnSystemTime = time.time()

print("{0}".format(tobiiSystemTime) + " vs " + "{0:.6f}".format(pythnSystemTime))
print("")


# connect to the eye tracker

eyetrackers = tr.find_all_eyetrackers()
currTracker = eyetrackers[0]


# collect time sync data

def time_synchronization_data_callback(time_synchronization_data):
	print(time_synchronization_data)

def time_synchronization_data(eyetracker):
	
	print("Subscribing to time synchronization data ...")
	eyetracker.subscribe_to(tr.EYETRACKER_TIME_SYNCHRONIZATION_DATA, time_synchronization_data_callback, as_dictionary=True)

	# wait while some time synchronization data is collected
	time.sleep(5)

	eyetracker.unsubscribe_from(tr.EYETRACKER_TIME_SYNCHRONIZATION_DATA, time_synchronization_data_callback)
	print("Unsubscribed from time synchronization data.")
	print("")

time_synchronization_data(currTracker)


# check python time vs tobii system time

tobiiSystemTime = tr.get_system_time_stamp()
pythnSystemTime = time.time()

print("{0}".format(tobiiSystemTime) + " vs " + "{0:.6f}".format(pythnSystemTime))





























