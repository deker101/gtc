#latlon to z xy
import math
import os
import numpy as np
import cv2
import requests
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = (lon_deg + 180.0) / 360.0 * n
  ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
  #print (xtile,ytile)
  return (int(xtile), int(ytile))

def deg2num_trunc(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = (lon_deg + 180.0) / 360.0 * n
  ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
  #print (xtile,ytile)
  return (xtile, ytile)
  
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)  
#zel=[56.0,37.0]
#zoom = [0,1,2,3,4,5,6,7,8,10,11,12,13]
#https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers
#for z in zoom:
#    x,y = deg2num(zel[0],zel[1],z)
#    url = 'https://c.tile.openstreetmap.de/%d/%d/%d.png'%(z,x,y)
#    print (url)

def get_tile(x,y,z):
  localpath = "mapcache/%d-%d-%d.png"%(z,x,y)
  check_file = os.path.isfile(localpath)
  print (localpath, check_file)
  if not check_file:
    url = 'http://a.tile.openstreetmap.fr/hot/%d/%d/%d.png'%(z,x,y)
    print (url)
    resp = requests.get(url, stream=True).raw
    png = resp.read()
    cache_tile = open(localpath, "wb")
    # write to file
    cache_tile.write(png)
    cache_tile.close()
    print (url)
  else:
    cache_tile = open(localpath, "rb")
    # write to file
    png = cache_tile.read()
    cache_tile.close()
  # download the image, convert it to a NumPy array, and then read
  # it into OpenCV format
  
  image = np.asarray(bytearray(png), dtype="uint8")
  image = cv2.imdecode(image, cv2.IMREAD_COLOR)
  # return the image
  return image