## Versie 3.2 ##
# Test coördinaten voor de poolster
# Overbrenging aangepast aan het geen nu
# start/target alt/az gebruikt --> simpelere deg2step

##_____LIBRARIES_____##
from skyfield.api import load, Topos    # pip install skyfield
import serial                           # pip install pyserial
import time                             # standard library
import re                               # standard library
import sys                              # standard library

##_____FUNCTIONS_____##
def ISS():
    # Url met recente tle's van het ISS
    url = "https://www.celestrak.com/NORAD/elements/supplemental/iss.txt"

    # Lijst met de verschillende baangegevens van het ISS
    satellites = load.tle_file(url)

    # t1 (getal) is de tijd 'nu' die we gebruiken om de recenste tle te vinden
    # t: <tt = xxxxx.xxxxx>, t1: xxxxx.xxxxx
    t1 = float(re.split('=|>', str(t))[1])

    # Epoch (getal) die het dichts bij 'nu' is
    # 0 omdat de eerste keer hij sws opgeslagen moet worden
    bestSat = 0

    for index in range(len(satellites)):
        # Zelfde als bij t1, de epoch naar getal splitsen
        sat = float(re.split('=|>', str(satellites[index].epoch))[1])

        if abs(sat - t1) < abs(bestSat - t1):
            # Onthouden van beste beste baan (index)
            bestIndex = index
            # Epoch beste baan (getal) om een nog beter te zoeken
            bestSat = float(re.split('=|>', str(satellites[bestIndex].epoch))[1])
            print("We've found a more recent tle:           ", satellites[index].epoch.utc_jpl())
        else:
            print("This tle will come soon ...")

    # We geven iss de recenste tle
    return satellites[bestIndex]

def deg2step(altStart, azStart, altTarget, azTarget):
    ##_____CONFIG_____##
    stepsPerRev = 200
    stepMode = 2
    altDiameterWiel = 14
    altLengteWiel = 9
    altDiameterSchijf = 370
    azDiameterWiel = 14
    azLengteWiel = 9
    azDiameterSchijf = 400
    
    ##_____CALCULATIONS_____##
    altOverbrenging = (altDiameterSchijf - altLengteWiel) / altDiameterWiel
    azOverbrenging = (azDiameterSchijf - azLengteWiel) / azDiameterWiel

    altPerStep = 360 / (altOverbrenging * stepsPerRev * stepMode)
    azPerStep = 360 / (azOverbrenging * stepsPerRev * stepMode)

    altAngle = altTarget - altStart
    azAngle = azTarget - azStart

    altSteps = int(altAngle / altPerStep)
    azSteps = int(azAngle / azPerStep)

    return [altSteps, azSteps]

def polaris(format):
    # ONLY MADE FOR POLARIS RIGHT NOW !
    lst = re.split("°|'|\"", format)
    angle = float(int(lst[0]) + (int(lst[1]) / 60) + (int(lst[2]) / 3600))
    return angle

##_____TIMESCALE_____##
# Beheert de omzetting van verschillende tijdsschalen
timescale = load.timescale()

##_____PLANETS_____##
planets = load('de421.bsp')
earth = planets['earth']

##_____VTI_____##
vti = Topos('50.855108 N', '2.864798 E', elevation_m=20)    # Voetbalveld VTI
vtiTemp = 15                                                # °C
vtiPress = 1013                                             # mbar / hPa

##_____ISS_____##
t = timescale.now()
iss = ISS()

##_____SERIAL_COMMUNICATION_____##
# Vergeet het versturen niet aan te zetten !
serialcomm = serial.Serial(port='COM6', baudrate=9600, timeout=1)

##_____TERMINAL_INPUT_____##

time.sleep(1)
print("> Wilt u de coordinaten van de poolster ingeven? ( yes / no )")

answer = input()

if (answer == "yes"):
    time.sleep(1)
    print("> Ik verwacht de altitude en azimuth van de poolster in dit formaat: xxx°xx'xx\"")
    altStart = polaris(input())
    azStart = polaris(input())
elif (answer == "no"):
    time.sleep(1)
    print("> Ok, dan gebruik ik de test coordinaten ...")
    altStart = polaris("51°00'00\"")
    azStart = polaris("0°00'00\"")
else:
    time.sleep(1)
    sys.exit("> Dit was niet wat ik vroeg !")

time.sleep(1)
print("> Dit zijn de coordinaten die ik zal gebruiken voor de poolster:")
time.sleep(1)
print(">    Altitude: ", altStart)
print(">    Azimuth:  ", azStart)

time.sleep(1)
print("> Ben je klaar, type 'ready'")
answer = input()

##_____WHILE_LOOP_____##
if (answer == "ready"):
    while True:
        t = timescale.now()

        # Latitude en longitude te berekenen
        geocentric = iss.at(t)
        subpoint = geocentric.subpoint()
        latitude = subpoint.latitude
        longitude = subpoint.longitude

        # Altitude en azimuth berekenen
        difference = iss - vti
        topocentric = difference.at(t)
        altitude, azimuth, distance = topocentric.altaz(temperature_C= vtiTemp, pressure_mbar= vtiPress)

        # Steps berekenen
        # (altStart, azStart, altTarget, azTarget)
        steps = deg2step(altStart, azStart, altitude.degrees, azimuth.degrees)

        # Data maken en verzenden
        data = "<" + str(steps[0]) + "|" + str(steps[1]) + ">"

        # Vergeet de 1-malige opzet niet !
        #serialcomm.write(data.encode())

        # Printing on monitor
        print('''
        ----------------------------------------
        Data        : {}
        ----------------------------------------
        Latitude    : {}
        Longitude   : {}

        Altitude    : {}
        Azimuth     : {}
        '''.format(data, latitude, longitude, altitude, azimuth))

        time.sleep(1)
else:
    time.sleep(1)
    sys.exit("Dit was niet wat ik vroeg !")