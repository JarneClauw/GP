## Version 1.1 ## 
# 1x Printen van de alt en az van het iss
# get_tle zit er in (later ISS)

from skyfield.api import load, Topos, EarthSatellite
import requests
from bs4 import BeautifulSoup as bs

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

ts = load.timescale()
t = ts.now()

#EARTH
planets = load('de421.bsp')
earth = planets['earth']
vti = Topos('50.855108 N', '2.864798 E')

#ISS
tle = get_tle()
iss = EarthSatellite(tle[1], tle[2], tle[0])

geocentric = iss.at(t)
subpoint = geocentric.subpoint()

print('')
print('Latitude:', subpoint.latitude)
print('Longitude:', subpoint.longitude)
print('Elevation (m):', int(subpoint.elevation.m))
print('')

difference = iss - vti
topocentric = difference.at(t)

alt, az, distance = topocentric.altaz()

print('')
print('Altitude:', alt )
print('Azimuth:', az)
print('distance:', int(distance.km), 'km')
print('')