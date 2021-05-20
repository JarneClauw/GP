## Versie 2 ##
# .degrees gevonden
# Skyfield de tle laten lezen ipv bs4
# Niet meer de laatste tle genomen

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
  alt_angle = alt.degrees

  ##______AZIMUTH_____##
  az_angle = az.degrees

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
altDiameterGroot = 385

serialcomm = serial.Serial(port='COM6', baudrate=9600, timeout=1)

##_____WHILE LOOP_____##
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

  serialcomm.write(data.encode())
 
  print("Data     : ", data)
  print("--------------------")
  print("Latitude : ", subpoint.latitude)
  print("Longitude: ", subpoint.longitude)
  print("Altitude : ", alt)
  print("Azimuth  : ", az)
  print("--------------------")

  time.sleep(1)