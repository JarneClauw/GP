## Version 6.1 ##
# wgs84 i.p.v. Topos, COM poorten (v1)

##_____TODO_____##
# Hemelkoepel verdraaijg (2sterren nodig) om ster te volgen



##_____LIBRARIES_____##
from   skyfield.api import load, wgs84, EarthSatellite  # Skyfield (main)
import requests                                         # Webscraping #1
from   bs4 import BeautifulSoup as bs                   # Webscraping #2
import datetime                                         # Time #1
import time                                             # Time #2
import pytz                                             # Time #3
import serial                                           # Serial communication
import serial.tools.list_ports
import re                                               # Text splitter
import sys                                              # System



##_____FUNCTIONS_____##
def format2deg(format):
    lst = re.split("°|'|\"", format)                    # Splits het gegeven formaat
    degree = int(lst[0])                                # Graden uit het formaat
    minute = float(int(lst[1]) / 60)                    # Minuten uit het formaat
    second = float(float(lst[2]) / 3600)                # Seconden uit het formaat
                                                        # Vormen van de hoek in decimalen
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
    altOverbrenging = (altDiameterSchijf - altLengteWiel) / altDiameterWiel         # Overbrenging altitude
    azOverbrenging = (azDiameterSchijf - azLengteWiel) / azDiameterWiel             # Overbrenging azimuth

    altPerStep = 360 / (altOverbrenging * stepsPerRev * stepMode)                   # ° / step altitude
    azPerStep = 360 / (azOverbrenging * stepsPerRev * stepMode)                     # ° / step azimuth

    altAngle = altTarget - altStart                                                 # Verschil van de hoeken altitude
    azAngle = azTarget - azStart                                                    # Verschil van de hoeken azimuth

    altSteps = int(altAngle / altPerStep)                                           # Steps altitude
    azSteps = int(azAngle / azPerStep)                                              # Steps azimuth               

    return [altSteps, azSteps]

def ISS():
    url = "https://www.celestrak.com/NORAD/elements/supplemental/iss.txt"       # Url van tle bestand

    response = requests.get(url)                                                # Aanvraag voor de informatie
                                                                                # Kijkt of er geen fout is
    if response.status_code != 200:
        sys.exit("Error fetching page")
    else:
        content = response.content

    soup = bs(content, "html5lib")                                              # BS4 object om te scrapen

    tle_list = soup.get_text()                                                  # Text van de pagina halen

    tle_blocks = int(tle_list.count("ISS"))                                     # Aantal keer het woord 'ISS' tellen

    tle = list(tle_list.splitlines())                                           # Volledige text in lijnen opdelen

    t1 = float(re.split('=|>', str(t))[1])                                      # Tijd van nu maar als getal

    bestSatEpoch = t1 - 3                                                       # Geen tle ouder dan 3 dagen
                                                                                # zeker wordt opgeslagen
    for index in range(tle_blocks):
        lineNum = index * 3                                                     # Elke tle block is 3 lijntjes
        name = tle[lineNum]                                                     # De satelliet naam is lijn #1
        line1 = tle[lineNum + 1]                                                # De 1ste tle lijn is lijn #2
        line2 = tle[lineNum + 2]                                                # De 2de tle lijn is lijn #3

        satellite = EarthSatellite(line1, line2, name, timescale)               # Skyfield satellite object

        satEpoch = float(re.split('=|>', str(satellite.epoch))[1])              # Epoch op satellite object

        if abs(satEpoch - t1) < abs(bestSatEpoch - t1):                         # Kortste Epoch zoeken
            bestName = name                                                     # Recentste naam
            bestLine1 = line1                                                   # Recentste 1ste lijn
            bestLine2 = line2                                                   # Recentste 2de lijn
            bestSat = EarthSatellite(line1, line2, name, timescale)             # Recentste satelliet object
            bestSatEpoch = float(re.split('=|>', str(bestSat.epoch))[1])        # Epoch recentste sattelliet
            print(bestName, bestSat.epoch.utc_jpl())
        
    return EarthSatellite(bestLine1, bestLine2, bestName, timescale)            
  
def choice(number):
    # Keuze menu 
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
timescale = load.timescale()                                                # Tijdschaal, omrekenen makkelijk maken



##_____PLANETS_____##
planets = load('de421.bsp')                                                 # Planeten inladen van 1900 - 2050
earth = planets['earth']                                                    # Planeet aarde laden



##_____TOPOS_____##
vtiISS = wgs84.latlon(50.855108, 2.864798, elevation_m=20)                  # VTI - locatie (voor ISS)
vti = earth + vtiISS                                                        # VTI - locatie
vtiTemp = 15                                                                # Instelbare temperatuur
vtiPress = 1013                                                             # Instelbare druk

reningelstISS = wgs84.latlon(50.815143, 2.771039, elevation_m=34)           # Jarne thuis - locatie (voor ISS)
reningelst = earth + reningelstISS                                          # Jarne thuis - locatie
reningelstTemp = -2                                                         # Instelbare temperatuur
reningelstPress = 1034                                                      # Instelbare druk

brussel = pytz.timezone('Europe/Brussels')                                  # Tijdzone instellen



##_____LOOPS_____##
loops = 0                                                                   # Overgang teller (0 <--> 359)
loopTijd = 0.25                                                             # Hoe snel de loop zich herhaalt



##_____ISS_____##
t = timescale.now()                                                         # Tijd nu, nodig om ISS object te bepalen
iss = ISS()                                                                 # ISS object



##_____COMMUNICATION_____##
time.sleep(1)
print("")
print("Wait if you want to connect to an arduino or type 'N' for continuing without")
ser = serial.Serial()
ser.baudrate = 9600
firstArduino = 0

while True:
    ports = list(serial.tools.list_ports.comports())
    
    for p in ports:
        if "Arduino" in p.description and firstArduino == 0:
            print("")
            print(50 * "-")
            print("We connected to ", p.description)
            print(50 * "-")
            firstArduino = 1
            arduino = p.name
            ser.port = arduino
            ser.open()
    
    if ser.isOpen() == True:
        break

    answer = input()

    if answer == "N":
        ser.close()
        break



##_____WHAT_WILL_YOU_SEE_____##
time.sleep(1)
                                                                            # Printen van de keuzes
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
inputStart = int(input("Start position (0 - 10): "))                        # Input keuze start

if inputStart == 0:                                                         # Manueel: altitude en azimuth kiezen
    print("You chose manual (Format: xxx°xx'xx\")")
    altS = input("Altitude: ")
    azS = input("Azimuth: ")
    altStart = format2deg(altS)
    azStart = format2deg(azS)

t = timescale.now()

if inputStart <= 10 and inputStart != 0:                                    # Planeet: bereken altitude en azimuth
    apparentStart = reningelst.at(t).observe(planets[choice(inputStart)]).apparent()
    altS, azS, distanceS = apparentStart.altaz()
    altStart = altS.degrees
    azStart = azS.degrees



##_____TARGET_POSITION_INPUT_____##
inputTarget = int(input("Target position (0 - 11): "))                      # Input keuze target

if inputTarget == 0:                                                        # Manueel: altitude en azimuth kiezen
    print("You chose manual (Format: xxx°xx'xx\")")
    altT = input("Altitude: ")
    azT = input("Azimuth: ")
    altTarget = format2deg(altT)
    azTarget = format2deg(azT)
    #Overgang moet niet omdat manueel niet gevolgd wordt (momenteel)



# Wacht niet te lang, anders verschuift je startpunt en je manueel gekozen punt te veel
readySign = input("Are you ready? Type 'R': ")                          # Sein geven dat je klaar bent 



##_____WHILE_____##
if (readySign == "R" and inputStart <=10 and inputTarget <=11):
    while True:
        t = timescale.from_datetime(brussel.localize(datetime.datetime.now()))
        t1 = timescale.from_datetime(brussel.localize(datetime.datetime.now() + datetime.timedelta(seconds=loopTijd)))

        if inputTarget <= 10 and inputTarget != 0:
            apparentTarget = reningelst.at(t).observe(planets[choice(inputTarget)]).apparent()
            altT, azT, distanceT = apparentTarget.altaz()
            altTarget = altT.degrees
            azTarget = azT.degrees

            apparentTarget1 = reningelst.at(t1).observe(planets[choice(inputTarget)]).apparent()
            altT1, azT1, distanceT1 = apparentTarget1.altaz()
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        elif inputTarget == 11:
            difference = iss - reningelstISS

            topocentric = difference.at(t)
            altT, azT, distanceT = topocentric.altaz(temperature_C= reningelstTemp, pressure_mbar= reningelstPress)
            altTarget = altT.degrees
            azTarget = azT.degrees

            topocentric1 = difference.at(t1)
            altT1, azT1, distanceT1 = topocentric1.altaz(temperature_C= reningelstTemp, pressure_mbar= reningelstPress)
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        elif azTarget > azTarget1 + 345:
            loops += 1
        elif azTarget + 345 < azTarget1:
            loops -= 1
        
        azTarget = azTarget + 360 * loops

        steps = deg2step(altStart, azStart, altTarget, azTarget)

        data = "<" + str(steps[0]) + "|" + str(steps[1]) + ">"

        if ser.isOpen() == True:
            ser.write(data.encode())


        print('''
            Start Position ({}) - - - - - Target Position ({})
            Altitude:   {} - - - - -  {}
            Azimuth:    {} - - - - -  {}
            
            Data:       {}

        '''.format(choice(inputStart), choice(inputTarget), altS, altT, azS, azT, data))

        time.sleep(loopTijd)
else:
    time.sleep(1)
    sys.exit("U heeft een fout gemaakt ...")

