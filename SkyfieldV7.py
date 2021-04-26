## Version 7 - Starlink ##
# Starlink satellieten zijn nieuw + laden van satelliet wanneer nodig

##_____LIBRARIES_____##
from skyfield.api import load, wgs84, EarthSatellite    # Skyfield (main)
import requests                                         # Webscraping #1
from bs4 import BeautifulSoup as bs                     # Webscraping #2
import datetime                                         # Time #1
from time import sleep                                  # Time #2
import pytz                                             # Time #3
import serial                                           # Serial communication #1
import serial.tools.list_ports                          # Serial communication #2
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

def Starlink(starlinkNumber):
    url_starlink = "https://celestrak.com/NORAD/elements/supplemental/starlink.txt"

    response = requests.get(url_starlink)

    if response.status_code != 200:
        sys.exit("Error fetching page")
    else:
        content = response.content

    soup = bs(content, "html5lib")
    text = soup.get_text()
    tle = list(text.splitlines())

    # Naam maken om te zoek (!!! moet 24 lang zijn !!!)
    name = "STARLINK-" + str(starlinkNumber)
    length = 24 - len(name)
    name += length * " "

    for index in range(len(tle)):
        if tle[index] == name:
            satName = tle[index]
            satLine1 = tle[index + 1]
            satLine2 = tle[index + 2]

    return EarthSatellite(satLine1, satLine2, satName, timescale)

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
            11: "iss",
            12: "starlink"
        }
    return switcher.get(number)



##_____TIMESCALE_____##
timescale = load.timescale()                                                # Tijdschaal, omrekenen makkelijk maken



##_____PLANETS_____##
planets = load('de421.bsp')                                                 # Planeten inladen van 1900 - 2050
earth = planets['earth']                                                    # Planeet aarde laden



##_____TOPOS_____##
vtiSat = wgs84.latlon(50.855108, 2.864798, elevation_m=20)                  # VTI - locatie (voor ISS)
vti = earth + vtiSat                                                        # VTI - locatie

reningelstSat = wgs84.latlon(50.815143, 2.771039, elevation_m=34)           # Jarne thuis - locatie (voor ISS)
reningelst = earth + reningelstSat                                          # Jarne thuis - locatie

brussel = pytz.timezone('Europe/Brussels')                                  # Tijdzone instellen



##_____LOOPS_____##
loops = 0                                                                   # Overgang teller (0 <--> 359)
loopTijd = 0.25                                                             # Hoe snel de loop zich herhaalt



##_____COMMUNICATION_____##
sleep(1)

ser = serial.Serial()
ser.baudrate = 9600
firstDevice = 0

ports = list(serial.tools.list_ports.comports())

if not len(ports) == 0:
    arduino = ports[0].name
    ser.port = arduino
    ser.open()
    print("")
    print("I connected to ", arduino)



##_____WHAT_WILL_YOU_SEE_____##
sleep(1)
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
    12: Starlink (Only as target)
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
inputTarget = int(input("Target position (0 - 12): "))                      # Input keuze target

if inputTarget == 0:                                                        # Manueel: altitude en azimuth kiezen
    print("You chose manual (Format: xxx°xx'xx\")")
    altT = input("Altitude: ")
    azT = input("Azimuth: ")
    altTarget = format2deg(altT)
    azTarget = format2deg(azT)
    #Overgang moet niet omdat manueel niet gevolgd wordt (momenteel)

if inputTarget == 11:
    t = timescale.now()
    iss = ISS()

if inputTarget == 12:
    print("You chose to follow starlink")
    starlinkNumber = input("What's the number: ")
    starlink = Starlink(starlinkNumber)

# Wacht niet te lang, anders verschuift je startpunt en je manueel gekozen punt te veel
readySign = input("Are you ready? Type 'R': ")                          # Sein geven dat je klaar bent 



##_____WHILE_____##
if (readySign == "R" and inputStart <=10 and inputTarget <=12):
    while True:
        time = datetime.datetime.now()
        t = timescale.from_datetime(brussel.localize(time))
        t1 = timescale.from_datetime(brussel.localize(time + datetime.timedelta(seconds=loopTijd)))

        if inputTarget <= 10 and inputTarget != 0:
            apparentTarget = reningelst.at(t).observe(planets[choice(inputTarget)]).apparent()
            altT, azT, distanceT = apparentTarget.altaz("standard")
            altTarget = altT.degrees
            azTarget = azT.degrees

            apparentTarget1 = reningelst.at(t1).observe(planets[choice(inputTarget)]).apparent()
            altT1, azT1, distanceT1 = apparentTarget1.altaz("standard")
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        elif inputTarget == 11:
            difference = iss - reningelstSat

            topocentric = difference.at(t)
            altT, azT, distanceT = topocentric.altaz("standard")
            altTarget = altT.degrees
            azTarget = azT.degrees

            topocentric1 = difference.at(t1)
            altT1, azT1, distanceT1 = topocentric1.altaz("standard")
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        elif inputTarget == 12:
            difference = starlink - reningelstSat

            topocentric = difference.at(t)
            altT, azT, distanceT = topocentric.altaz("standard")
            altTarget = altT.degrees
            azTarget = azT.degrees

            topocentric1 = difference.at(t1)
            altT1, azT1, distanceT1 = topocentric1.altaz("standard")
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        # Overgang 359 --> 0
        if azTarget > azTarget1 + 345:
            loops += 1
            skip = 1
        # Overgang 0 -- > 359
        elif azTarget + 345 < azTarget1:
            loops -= 1
            skip = 1
        # Geen overgang
        else:
            skip = 0

        if skip == 0:
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
            Loops:      {}
        '''.format(choice(inputStart), choice(inputTarget), altS, altT, azS, azT, data, loops))

        sleep(loopTijd)
else:
    sleep(1)
    sys.exit("U heeft een fout gemaakt ...")

