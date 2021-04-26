## Versie 3.1 ##
# Verplicht polaris gebruiken om stappen te berekenen

##_____<_>_<_>_<_>_____L_I_N_K_S_____<_>_<_>_<_>_____##
#https://rhodesmill.org/skyfield/earth-satellites.html
#https://rhodesmill.org/skyfield/toc.html
#
#
##___TODO___#
#                                                                      
# Code wat properder maken (beter namen enzo)
# GUI (geen idee)
# Overbrenging aanpassen (verticaal)
# Is er niets om die COM poort automatisch te doen of als ter geen is ook niets sturen
# Mooie pinnetjes om met bordje te verbinden
# richting testen (az + = met klok, az - = tegen klok, alt + = omhoog, alt - = omlaag) ISS - Poolster
#


##_____LIBRARIES_____##
from skyfield.api import load, Topos
import serial
import time
import re

##_____FUNCTIONS_____##
def get_tle():

  url = "https://www.celestrak.com/NORAD/elements/supplemental/iss.txt"

  satellites = load.tle_file(url)

  t1 = float(re.split('=|>', str(t))[1])

  #Als hij tle zoekt, start pas vanaf 3 dagen van of voor nu
  bestsat = 3

  for index in range(len(satellites)):
    sat = float(re.split('=|>', str(satellites[index].epoch))[1])

    if abs(sat - t1) < abs(bestsat - t1):
      bestindex = index
      bestsat = float(re.split('=|>', str(satellites[bestindex].epoch))[1])
      print("We've found a more recent tle:       ", satellites[index].epoch.utc_jpl())
    else:
      print('No tle found within 3 days ...')
 
  return satellites[bestindex]

def get_alt_az_steps():
  ##_____ALTITUDE_____##
  alt_iss = alt.degrees
  alt_polaris_lst = re.split("°|'|\"",givenAlt) #moet nog opgesplitst worden
  alt_polaris = float(int(alt_polaris_lst[0]) + (int(alt_polaris_lst[1])/60) + (int(alt_polaris_lst[2])/3600))
  alt_angle = alt_iss - alt_polaris
  ##______AZIMUTH_____##
  az_iss = az.degrees
  az_polaris_lst = re.split("°|'|\"",givenAz) #moet nog opgesplitst worden
  az_polaris_deg = int(az_polaris_lst[0])
  az_polaris_min = int(az_polaris_lst[1])
  az_polaris_sec = int(az_polaris_lst[2])
  az_polaris = float(az_polaris_deg + (az_polaris_min / 60) + (az_polaris_sec / 3600))
  az_angle = az_iss - az_polaris

  ##______Calculations______##
  altOverbrenging = (altDiameterGroot-altDiameterKlein) / altDiameterKlein
  azOverbrenging = (azDiameterGroot-azDiameterKlein) / azDiameterKlein

  alt_per_step = 360 / (altOverbrenging * stepsPerRevolution * stepMode)
  az_per_step = 360 / (azOverbrenging * stepsPerRevolution * stepMode)

  alt_steps = alt_angle / alt_per_step
  az_steps = az_angle / az_per_step
  
  return [alt_steps, az_steps]

##_____TIMESCALE_____##
ts = load.timescale()           #Timescale van aarde maken

##_____EARTH_____##
planets = load('de421.bsp')
earth = planets['earth']

##_____VTI_____##
vti = Topos('50.855108 N', '2.864798 E', elevation_m=20)
vtiTemp = 15                    #°C
vtiPress = 1013                 #mbar/hPa

##_____ISS_____##
t = ts.now()
iss = get_tle()

epoch = iss.epoch.utc_jpl()     #Epoch is de datum wnnr de berekeningen het meest kloppen

##_____STEPPER + SERIAL_____##
stepsPerRevolution = 200
stepMode = 2
azDiameterKlein = 14
azDiameterGroot = 390
altDiameterKlein = 14
altDiameterGroot = 370

#serialcomm = serial.Serial(port='COM6', baudrate=9600, timeout=1)

##_____COORDS VRAGEN_____##
print("Altitude en Azimuth van de poolster: (format: xxx°xx'xx\")")
givenAlt = input()
givenAz = input()
print('''
      Altitude: {}
      Azimuth:  {}
'''.format(givenAlt, givenAz))
time.sleep(1)
print("Type ready if you're ready")
readySign = input()


##_____WHILE LOOP_____##
if (readySign == "ready"):
  while True:
    t = ts.now()                    #Tijd van de computer nemen

    #Om lat en lon te berekenen
    geocentric = iss.at(t)
    subpoint = geocentric.subpoint()

    difference = iss - vti          #Verschil van iss en vti vector om altaz te berekenen
    topocentric = difference.at(t)  #.at() berekend eerst satteliet positie en dan dat van de locatie
    #Temp. en druk helpen bepalen hoe het licht afgebogen wordt, je kan ook 'standard' invullen
    alt, az, distance = topocentric.altaz(temperature_C= vtiTemp, pressure_mbar=vtiPress)

    steps = get_alt_az_steps()
    alt_steps = int(steps[0])
    az_steps = int(steps[1])

    #Bij get_alt_az_steps kan er bij return een - staan ... => voor de richting
    data = "<" + str(alt_steps) + "|" + str(az_steps) + ">"

    #serialcomm.write(data.encode())
  
    print("Data     : ", data)
    print("--------------------")
    print("Latitude : ", subpoint.latitude)
    print("Longitude: ", subpoint.longitude)
    print("Altitude : ", alt)
    print("Azimuth  : ", az)
    print("--------------------")

    time.sleep(1)
