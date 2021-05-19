##_____LIBRARIES_____##
from skyfield.api import load, wgs84, EarthSatellite  # Skyfield
import requests  # Webscraping #1
from bs4 import BeautifulSoup as bs  # Webscraping #2
import datetime  # Time #1
from time import sleep, time  # Time #2
import pytz  # Time #3
import serial  # Serial communication #1
import serial.tools.list_ports  # Serial communication #2
import re  # Text splitter (regular expression)
import sys  # System
import sqlite3  # Database

# overgang klopt niet

# Stopt niet aan 30° hoogte

# Sleep(looptijd)

# Tijd bij de berekeningen klopt niet, ga van 30 na 25 of 8 ??!!!



# Herschrijven van Hopping functie

overgang = 0  # Overgang teller (0 <--> 359)
loopTijd = 0.25  # Hoe snel de loop zich herhaalt
nextTimeStart = 5 # s
nextTime = 20    # s
startAngle = 30  # °
waitTime = 5     # s
firstRotation = True
firstHop = True
extra = datetime.timedelta(hours=0, minutes=0)

def hopping():
	global firstHop
	global time2
	global altT
	global azT
	global altTarget
	global azTarget

	# Eerste hop
	if firstHop == True:
		# Zorgen dat het maar 1x kan
		firstHop = False
		time = datetime.datetime.now() + extra
		time2 = time

		# Berekenen om positie nu te weten
		topocentric = difference.at(t)
		altT, azT, distanceT = topocentric.altaz("standard")
		altTarget = altT.degrees
		azTarget = azT.degrees
		altTarget1 = altTarget
		azTarget1 = azTarget

		# Zoeken naar tijd waar hoogte voor het eerst boven 30° gaat
		while altTarget < startAngle:
			time2 += datetime.timedelta(seconds=nextTimeStart)
			t2 = timescale.from_datetime(brussel.localize(time2))
			print(time2)
			topocentric = difference.at(t2)
			altT, azT, distanceT = topocentric.altaz("standard")
			altTarget = altT.degrees
			azTarget = azT.degrees
			altTarget1 = altTarget
			azTarget1 = azTarget
	
	# Volgende hops
	else:
		if altTarget < startAngle:
			sys.exit("The satellite has reached the minimum altitude: {}°".format(startAngle))
		
		time2 += datetime.timedelta(seconds=waitTime)

		# Timer
		while True:
			time = datetime.datetime.now() + extra
			timeD = time2 - time
			timeDHour = timeD.seconds//3600
			timeDMin = (timeD.seconds//60)%60
			timeDSec = timeD.seconds%60

			if timeDHour == 0 and timeDMin == 0:
				print("Countdown: {} second(s)".format(timeDSec))
			elif timeDHour == 0:
				print("Countdown: {} minute(s) {} second(s)".format(timeDMin, timeDSec))
			else:
				print("Countdown: {} hour(s) {} minute(s) {} second(s)".format(timeDHour, timeDMin, timeDSec))

			if timeD.seconds == 0:
				break

			sleep(1)

		# Berekenen van volgende positie
		time2 = time + datetime.timedelta(seconds=nextTime)
		t2 = timescale.from_datetime(brussel.localize(time2))
		topocentric = difference.at(t)
		altT, azT, distanceT = topocentric.altaz("standard")
		altTarget = altT.degrees
		azTarget = azT.degrees

		time2T = time2 + datetime.timedelta(seconds=nextTime)
		t2T = timescale.from_datetime(brussel.localize(time2T))
		topocentric1 = difference.at(t2T)
		altT1, azT1, distanceT1 = topocentric1.altaz("standard")
		altTarget1 = altT1.degrees
		azTarget1 = azT1.degrees

