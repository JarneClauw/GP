## Version 4.2 ##
# start input maar 1x doen (je rekent anders met het verschil tussen de 2)

##_____TODO_____##
# 360 --> 0 moet doorlopen
# Serialcomm automatisch?

##_____LIBRARIES_____##
from skyfield.api import load, Topos
import serial
import time
import re
import sys

##_____FUNCTIONS_____##
def format2deg(format):
    lst = re.split("°|'|\"", format)
    degree = int(lst[0])
    minute = float(int(lst[1]) / 60)
    second = float(float(lst[2]) / 3600)

    if degree > 0:
        angle = degree + minute + second
    elif degree < 0:
        angle = degree - minute - second
    elif degree == 0:
        if format[0] == '-':
            angle = - minute - second
        else:
            angle = minute + second
    
    return angle

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

    print("Epoch of ISS tle: ", satellites[bestIndex].epoch.utc_jpl())

    # We geven iss de recenste tle
    return satellites[bestIndex]   

def choice(number):
    switcher = {
            0: "manual",
            1: "sun",
            2: "mercury",
            3: "venus",
            4: "moon",
            5: "mars",
            6: "jupiter barycenter",
            7: "saturn barycenter",
            8: "uranus barycenter",
            9: "neptune barycenter",
            10: "pluto barycenter",
            11: "iss"
        }
    return switcher.get(number)

##_____TIMESCALE_____##
timescale = load.timescale()

##_____PLANETS_____##
planets = load('de421.bsp')
earth = planets['earth']

##_____TOPOS_____##
vti = earth + Topos('50.855108 N', '2.864798 E', elevation_m=20)
vtiISS = Topos('50.855108 N', '2.864798 E', elevation_m=20)
vtiTemp = 15 
vtiPress = 1013 

reningelst = earth + Topos('50.815143 N', '2.771039 E', elevation_m=34)
reningelstISS = Topos('50.815143 N', '2.771039 E', elevation_m=34)
reningelstTemp = -2
reningelstPress = 1034

##_____ISS_____##
t = timescale.now()
iss = ISS()

##_____COMMUNICATION_____##
# Vergeet het versturen niet aan te zetten !
#serialcomm = serial.Serial(port='COM6', baudrate=9600, timeout=1)

##_____WHAT_WILL_YOU_SEE_____##
print('''
Your choices for tonight:
    0: Manual (Stars for example)
    1: Sun (Not recommended)
    2: Mercury
    3: Venus
    4: Moon
    5: Mars
    6: Jupiter
    7: Saturn
    8: Uranus
    9: Neptune
    10: Pluto
    11: ISS (Only as target)
''')

##_____START_POSITION_INPUT_____##
inputStart = int(input("Start position (0 - 10): "))

if inputStart == 0:
    print("You chose manual (Format: xxx°xx'xx\")")
    altS = input("Altitude: ")
    azS = input("Azimuth: ")
    altStart = format2deg(altS)
    azStart = format2deg(azS)

if inputStart <= 10 and inputStart != 0:
    apparentStart = reningelst.at(t).observe(planets[choice(inputStart)]).apparent()
    altS, azS, distanceS = apparentStart.altaz()
    altStart = altS.degrees
    azStart = azS.degrees

##_____TARGET_POSITION_INPUT_____##
inputTarget = int(input("Target position (0 - 11): "))

if inputTarget == 0:
    print("You chose manual (Format: xxx°xx'xx\")")
    altT = input("Altitude: ")
    azT = input("Azimuth: ")
    altTarget = format2deg(altT)
    azTarget = format2deg(azT)

readySign = input("Are you ready? Type 'ready': ")

##_____WHILE_____##
if (readySign == "ready" and inputStart <=10 and inputTarget <=11):
    while True:
        t = timescale.now()

        if inputTarget <= 10 and inputTarget != 0:
            apparentTarget = reningelst.at(t).observe(planets[choice(inputTarget)]).apparent()
            altT, azT, distanceT = apparentTarget.altaz()
            altTarget = altT.degrees
            azTarget = azT.degrees
        elif inputTarget == 11:
            difference = iss - reningelstISS
            topocentric = difference.at(t)
            altT, azT, distanceT = topocentric.altaz(temperature_C= reningelstTemp, pressure_mbar= reningelstPress)
            altTarget = altT.degrees
            azTarget = azT.degrees

        steps = deg2step(altStart, azStart, altTarget, azTarget)

        data = "<" + str(steps[0]) + "|" + str(steps[1]) + ">"

        #serialcomm.write(data.encode())
        print('''
            Start Position ({}) - - - - - Target Position ({})
            Altitude:   {} - - - - -  {}
            Azimuth:    {} - - - - -  {}
            
            Data:       {}

        '''.format(choice(inputStart), choice(inputTarget), altS, altT, azS, azT, data))

        time.sleep(0.25)
else:
    time.sleep(1)
    sys.exit("U heeft een fout gemaakt ...")

