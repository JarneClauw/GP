## Version 8 - Locatie ##
# Locatie waar je observeert kan je kiezen (met sqlite3)

##_____LIBRARIES_____##
from skyfield.api import load, wgs84, EarthSatellite    # Skyfield
import requests                                         # Webscraping #1
from bs4 import BeautifulSoup as bs                     # Webscraping #2
import datetime                                         # Time #1
from time import sleep                                  # Time #2
import pytz                                             # Time #3
import serial                                           # Serial communication #1
import serial.tools.list_ports                          # Serial communication #2
import re                                               # Text splitter (regular expression)
import sys                                              # System
import sqlite3                                          # Database

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
    ##_____CONFIGURATION_____##
    stepsPerRev = 200
    stepMode = 2
    altDiameterWiel = 16.5
    altLengteWiel = 9
    altDiameterSchijf = 370
    #azDiameterWiel = 14
    #azLengteWiel = 9
    #azDiameterSchijf = 400

    ##_____CALCULATIONS_____##
    altOverbrenging = (altDiameterSchijf - altLengteWiel) / altDiameterWiel         # Overbrenging altitude
    #azOverbrenging = (azDiameterSchijf - azLengteWiel) / azDiameterWiel             # Overbrenging azimuth

    altPerStep = 360 / (altOverbrenging * stepsPerRev * stepMode)                   # ° / step altitude
    #azPerStep = 360 / (azOverbrenging * stepsPerRev * stepMode)                     # ° / step azimuth
    
    #altPerStep = 360 / x
    azPerStep = 360 / 9600

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

    print("")      
    print(bestName, bestSat.epoch.utc_jpl())
        
    return EarthSatellite(bestLine1, bestLine2, bestName, timescale)

def Starlink(starlinkNumber):
    url_starlink = "https://celestrak.com/NORAD/elements/supplemental/starlink.txt"     # Url van tle bestand

    response = requests.get(url_starlink)                                               # Aanvraag voor de informatie
                                                                                        # Kijkt of er geen fout is
    if response.status_code != 200:                 
        sys.exit("Error fetching page")
    else:
        content = response.content

    soup = bs(content, "html5lib")                                                      # BS4 object om te scrapen
    text = soup.get_text()                                                              # Text van de pagina halen
    tle = list(text.splitlines())                                                       # Volledige text in lijnen opdelen

    # Naam maken om te zoek (!!! moet 24 lang zijn !!!)
    name = "STARLINK-" + str(starlinkNumber)                                            # Naam maken om daarmee de juiste tle te vinden
    length = 24 - len(name)
    name += length * " "

    for index in range(len(tle)):                                                       # De naam in het bestand zoeken
        if tle[index] == name:                                                          # Gegevens opslaan in variabelen
            satName = tle[index]
            satLine1 = tle[index + 1]
            satLine2 = tle[index + 2]

    starlink = EarthSatellite(satLine1, satLine2, satName, timescale)                   # Satelliet object maken
    print("")
    print(satName, starlink.epoch.utc_jpl())
    return starlink

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

def location():
    # Connectie maken met bestand of aanmaken
    try:
        con = sqlite3.connect('GP.db')
        cursor = con.cursor()
    except serial.tools.list_ports.Error:
        sys.exit("Couldn't connect with the database!")

    # Check of er al een table bestaat, zoniet maak een
    cursor.execute("CREATE TABLE IF NOT EXISTS location(id integer PRIMARY KEY, name text, longitude real, latitude real, elevation real)")
    con.commit()

    # Bestaande locaties printen (Naam)
    print("---- Locations ----")
    cursor.execute("SELECT name FROM location")
    locations = cursor.fetchall()
    for location in locations:
        print("> " + location[0])

    # Keuze menu (Choose / Make / Delete)
    print("")
    print("---- Options ----")
    print("> Choosing a location (0)")
    print("> Make a new location (1)")
    print("> Delete a location   (2)", "\n")

    answer = input("Option number: ")

    # (0) Choosing location 
    if answer == "0":
        # Bestaande locaties printen (ID, Naam)
        print("")
        print("---- Locations ----")
        cursor.execute("SELECT id, name FROM location")
        locations = cursor.fetchall()
        for location in locations:
            print("> " + str(location[0]) + ": " + str(location[1]))
        
        print("")
        answer = int(input("City number: "))    

        cursor.execute("SELECT * FROM location")
        numberOfLocations = len(cursor.fetchall())

        # Locatie maken met gegevens die gekozen werden
        if answer <= numberOfLocations and answer >= 0:   
            cursor.execute("SELECT longitude, latitude, elevation FROM location WHERE id = ?", (str(answer)))
            info = cursor.fetchone()
            longitude = info[0]
            latitude = info[1]
            elevation = info[2]

            locationSat = wgs84.latlon(latitude, longitude, elevation_m= elevation)
        # Afsluiten van het programma bij fouten
        else:
            con.close()
            sys.exit("Error by choosing location!")


    # (1) New location
    elif answer == "1":
        # Nieuwe locatie toevoegen
        cursor.execute("SELECT * FROM location")
        key = len(cursor.fetchall()) + 1

        print("\n" + "---- Adding ----")
        name = input("> Location name: ")
        longitude = input("> Longitude: ")
        latitude = input("> Latitude: ")
        elevation = input("> Elevation: ")
        print("")

        info = (key, name, longitude, latitude, elevation)
        cursor.execute("INSERT INTO location(id, name, longitude, latitude, elevation) VALUES(?,?,?,?,?)", info)
        con.commit()
        
        # Bestaande locaties printen (ID, Naam)
        print("---- Locations ----")
        cursor.execute("SELECT id, name FROM location")
        locations = cursor.fetchall()
        for location in locations:
            print("> " + str(location[0]) + ": " + str(location[1]))

        # Locatie maken van gekozen nummer
        print("")
        answer = int(input("City Number: "))    

        if answer <= key and answer >= 0:   
            cursor.execute("SELECT longitude, latitude, elevation FROM location WHERE id = ?", (answer,))
            info = cursor.fetchone()
            longitude = info[0]
            latitude = info[1]
            elevation = info[2]

            locationSat = wgs84.latlon(latitude, longitude, elevation_m= elevation)
        else:
            con.close()
            sys.exit("Error by adding a new locationn!")


    # (2) Delete location
    elif answer == "2":
        # Bestaande locaties printen (ID, Naam)
        print("\n", "---- Delete ----")
        cursor.execute("SELECT id, name FROM location")
        locations = cursor.fetchall()
        for location in locations:
            print("> " + str(location[0]) + ": " + str(location[1]))   

        # Verwijderen van locatie
        print("")
        answer = input("Delete number: ")

        cursor.execute("DELETE FROM location WHERE id = ?", (answer,))
        con.commit()

        # Bestaande locaties printen (ID, Naam)
        print("\n", "---- Locations ----")
        cursor.execute("SELECT id, name FROM location")
        locations = cursor.fetchall()
        for location in locations:
            print("> " + str(location[0]) + ": " + str(location[1]))

        # Locatie maken met gegevens
        print("")
        answer = int(input("Number of the city: "))    

        cursor.execute("SELECT * FROM location")
        numberOfLocations = len(cursor.fetchall())

        if answer <= numberOfLocations and answer >= 0:   
            cursor.execute("SELECT longitude, latitude, elevation FROM location WHERE id = ?", (answer,))
            info = cursor.fetchone()
            longitude = info[0]
            latitude = info[1]
            elevation = info[2]

            locationSat = wgs84.latlon(latitude, longitude, elevation_m= elevation)

        else:
            con.close()
            sys.exit("Error by deleting a location!")


    # Alle andere mogelijke antwoorden
    else:
        con.close()
        sys.exit("Wrong number! (Location - Options)")
    
    # Database sluiten
    con.close()

    # Locatie maken 
    # locationSat hierboven al gemaakt
    location = earth + locationSat

    return [locationSat, location]

##_____TIMESCALE_____##
timescale = load.timescale()                                                # Tijdschaal, maakt omrekenen makkelijk

##_____PLANETS_____##
planets = load('de421.bsp')                                                 # Planeten inladen van 1900 - 2050
earth = planets['earth']                                                    # Planeet aarde laden

##_____TIMEZONE_____##
brussel = pytz.timezone("Europe/Brussels")                                  # Tijdzone instellen

##_____OVERGANG/LOOPS_____##
overgang = 0                                                                # Overgang teller (0 <--> 359)
loopTijd = 0.25                                                             # Hoe snel de loop zich herhaalt

##_____COMMUNICATION_____##
ser = serial.Serial()                                                       # Seriële communicatie starten
ser.baudrate = 9600                                                         # Baudrate instellen

ports = list(serial.tools.list_ports.comports())                            # Lijst van alle aangesloten apparaten

if not len(ports) == 0:                                                     # Als het niet leeg is ...
    arduino = ports[0].name                                                 # 1 ste apparaat nemen
    ser.port = arduino                                                      # Instellen als poort
    ser.open()                                                              # Poort open zetten voor gebruik
    print("")
    print("I connected to ", arduino)

##_____LOCATIE_(DB)_____##
locInfo = location()
locationSat = locInfo[0]
location = locInfo[1]

##_____WHAT_WILL_YOU_SEE_____##
                                                                            # Printen van de keuzes
print('''
---- Objects ----
> 0: Manual (Stars for example)
> 1: Sun (Not recommended)
> 2: Mercury
> 3: Venus
> 4: Moon
> 5: Mars
> 6: Jupiter
> 7: Saturn
> 8: Uranus
> 9: Neptune
> 10: Pluto
> 11: ISS (Only as target)
> 12: Starlink (Only as target)
''')

##_____START_POSITION_INPUT_____##
inputStart = int(input("Start position (0 - 10): "))                        # Input keuze start object

if inputStart == 0:                                                         # Manueel: altitude en azimuth kiezen
    print("\n" + "You chose manual (Format: xxx°xx'xx\")")
    altS = input("> Altitude: ")
    azS = input("> Azimuth: ")
    altStart = format2deg(altS)
    azStart = format2deg(azS)

t = timescale.now()

if inputStart <= 10 and inputStart != 0:                                    # Planeet: bereken altitude en azimuth
    apparentStart = location.at(t).observe(planets[choice(inputStart)]).apparent()
    altS, azS, distanceS = apparentStart.altaz()
    altStart = altS.degrees
    azStart = azS.degrees

##_____TARGET_POSITION_INPUT_____##
inputTarget = int(input("Target position (0 - 12): "))                      # Input keuze target object

if inputTarget == 0:                                                        # Manueel: altitude en azimuth kiezen
    print("\n" + "You chose manual (Format: xxx°xx'xx\")")
    altT = input("> Altitude: ")
    azT = input("> Azimuth: ")
    altTarget = format2deg(altT)
    altTarget1 = altTarget
    azTarget = format2deg(azT)
    azTarget1 = azTarget
    #Overgang moet niet omdat manueel niet gevolgd wordt (momenteel)

if inputTarget == 11:                                                       # ISS: object aanmaken
    t = timescale.now()
    iss = ISS()

if inputTarget == 12:                                                       # Starlink: object aanmaken
    print("\n" + "You chose to follow starlink")                            # Nummer van Starlink vragen
    starlinkNumber = input("What's the number: ")
    starlink = Starlink(starlinkNumber)

##_____START_SIGN_____##
# Wacht niet te lang, anders verschuift je startpunt en je manueel gekozen punt te veel
print("")
readySign = input("Are you ready? Type 'R': ")                              # Sein geven dat je klaar bent 

##_____WHILE_____##
if (readySign == "R" and inputStart <=10 and inputTarget <=12):
    while True:
        time = datetime.datetime.now()
        t = timescale.from_datetime(brussel.localize(time))
        t1 = timescale.from_datetime(brussel.localize(time + datetime.timedelta(seconds=loopTijd)))

        if inputTarget <= 10 and inputTarget != 0:
            apparentTarget = location.at(t).observe(planets[choice(inputTarget)]).apparent()
            altT, azT, distanceT = apparentTarget.altaz("standard")
            altTarget = altT.degrees
            azTarget = azT.degrees

            apparentTarget1 = location.at(t1).observe(planets[choice(inputTarget)]).apparent()
            altT1, azT1, distanceT1 = apparentTarget1.altaz("standard")
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        elif inputTarget == 11:
            difference = iss - locationSat

            topocentric = difference.at(t)
            altT, azT, distanceT = topocentric.altaz("standard")
            altTarget = altT.degrees
            azTarget = azT.degrees

            topocentric1 = difference.at(t1)
            altT1, azT1, distanceT1 = topocentric1.altaz("standard")
            altTarget1 = altT1.degrees
            azTarget1 = azT1.degrees

        elif inputTarget == 12:
            difference = starlink - locationSat

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
            overgang += 1
            skip = 1
        # Overgang 0 -- > 359
        elif azTarget + 345 < azTarget1:
            overgang -= 1
            skip = 1
        # Geen overgang
        else:
            skip = 0

        if skip == 0:
            azTarget = azTarget + 360 * overgang

        steps = deg2step(altStart, azStart, altTarget, azTarget)

        data = "<" + str(steps[0]) + "|" + str(steps[1]) + ">"

        if ser.isOpen() == True:
            ser.write(data.encode())
        else:
            print("This information isn't send to your device")
        
        print('''
            Start Position ({}) - - - - - Target Position ({})
            Altitude:   {} - - - - -  {}
            Azimuth:    {} - - - - -  {}
            
            Data:       {} 
            Overgang:      {}
        '''.format(choice(inputStart), choice(inputTarget), altS, altT, azS, azT, data, overgang))

        sleep(loopTijd)
else:
    sleep(1)
    sys.exit("Ready sign / input- Start/Target is wrong!")