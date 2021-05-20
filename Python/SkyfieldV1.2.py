## Versie 1.2 ##
# Overbrenging meegerekend
# Communicatie met arduino
# Herhalend printen / doorsturen

##_____LIBRARIES_____##
from skyfield.api import load, Topos, EarthSatellite
import requests
from bs4 import BeautifulSoup as bs
import serial
import time

##_____FUNCTIONS_____##
def get_tle():
  #Lengte 1 tle blok is 165 karakters
  TLE_BlockLength = 165

  #Website TLE URL
  url = "https://www.celestrak.com/NORAD/elements/supplemental/iss.txt"
  response = requests.get(url)
  soup = bs(response.content, "html5lib")

  #Volledige tle list
  tle_list = soup.get_text()

  #Verschillende tle's tellen
  tle_blockCount = tle_list.count("ISS")

  #Verdelen in lijnen
  tle = list(tle_list.splitlines())

  #Laatste toegevoegde tle nemen
  tle_last_n = ((tle_blockCount-1)*3)
  tle_last_l1 = ((tle_blockCount-1)*3+1)
  tle_last_l2 = ((tle_blockCount-2)*3+2)

  #Variabelen voor tle reader
  tle_n = tle[tle_last_n]
  tle_l1 = tle[tle_last_l1]
  tle_l2 = tle[tle_last_l2]

  return [tle_n, tle_l1, tle_l2]

def get_alt_az_steps():
  ##_____ALTITUDE_____##
  alt_str = str(alt)
  alt_lst = alt_str.split(" ")
  alt_deg_lst = alt_lst[0].split("deg")
  alt_mnt_lst = alt_lst[1].split("'")
  alt_sec_lst = alt_lst[2].split('"')
  alt_deg = int(alt_deg_lst[0])
  alt_mnt = int(alt_mnt_lst[0])
  alt_sec = float(alt_sec_lst[0])

  if alt_deg > 0:
    alt_angle = alt_deg + ((alt_mnt+(alt_sec/60))/60)
  elif alt_deg < 0:
    alt_angle = alt_deg - ((alt_mnt+(alt_sec/60))/60)
  elif alt_deg == 0:
    if alt_str[0] == '-':
      alt_angle = - ((alt_mnt+(alt_sec/60))/60)
    else:
      alt_angle = ((alt_mnt+(alt_sec/60))/60)

  alt_per_step = 360 / stepsPerRevolution
  alt_steps = alt_angle / alt_per_step

  ##______AZIMUTH_____##
  az_str = str(az)
  az_lst = az_str.split(" ")
  az_deg_lst = az_lst[0].split("deg")
  az_mnt_lst = az_lst[1].split("'")
  az_sec_lst = az_lst[2].split('"')
  az_deg = int(az_deg_lst[0])
  az_mnt = int(az_mnt_lst[0])
  az_sec = float(az_sec_lst[0])

  if az_deg > 0:
    az_angle = az_deg + ((az_mnt+(az_sec/60))/60)
  elif az_deg < 0:
    az_angle = az_deg - ((az_mnt+(az_sec/60))/60)
  elif az_deg == 0:
    if az_str[0] == '-':
      az_angle = - ((az_mnt+(az_sec/60))/60)
    else:
      az_angle = ((az_mnt+(az_sec/60))/60)
    
  az_per_step = 360 / stepsPerRevolution
  az_steps = az_angle / az_per_step
  
  # - is voor de juiste richting, kan ook door kabels te draaien
  return [-alt_steps, az_steps]

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
tle = get_tle()
iss = EarthSatellite(tle[1], tle[2], tle[0])

epoch = iss.epoch.utc_jpl()     #Epoch is de datum wnnr de berekeningen het meest kloppen

##_____STEPPER + SERIAL_____##
stepsPerRevolution = 400

serialcomm = serial.Serial(port='COM9', baudrate=115200, timeout=1)

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

  time.sleep(2)
