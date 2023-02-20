import os
import gpxpy
import gpxpy.gpx
from tile import deg2num, deg2num_trunc, get_tile

from PIL import Image, ImageDraw
import cv2
import numpy as np

import argparse

def get_gpx_points(gpx):
    points = []
    for track in gpx.tracks:
        print (track)
        for segment in track.segments:
            
            print (segment)
            for point in segment.points:
                p = [point.longitude, point.latitude, point.elevation]
                points.append(p)
    return points

def get_osm_tiles(points,name):
    tiles = []
    track = []
    latmin = None
    latmax = None
    lonmin = None
    lonmax = None
    for p in points:
        if latmin is None:
            latmin = p[1]
        if latmax is None:
            latmax = p[1]
        if lonmin is None:
            lonmin = p[0]
        if lonmax is None:
            lonmax = p[0]
        
        if latmin > p[1]:
            latmin = p[1]
        if latmax < p[1]:
            latmax = p[1]
        if lonmin > p[0]:
            lonmin = p[0]
        if lonmax < p[0]:
            lonmax = p[0]   
    print (latmin,latmax,lonmin,lonmax)

    z = zoom
    track = []
    ctrack = []
    x_min,y_min = deg2num(latmax,lonmin,z)
    #print (z, x,y)
    x_max,y_max = deg2num(latmin,lonmax,z)
    #print (z, w, h)
    w=(x_max-x_min)+1
    h=(y_max-y_min)+1
    w*=256
    h*=256
    print (z, w, h)
    full_image = np.zeros((h,w,3), np.uint8)
    for x in range(x_min,x_max+1,1):
        for y in range(y_min,y_max+1,1):
            #url = 'https://c.tile.openstreetmap.de/%d/%d/%d.png'%(z,x,y)
            #url = 'https://stamen-tiles.a.ssl.fastly.net/toner/%d/%d/%d.png'%(z,x,y)
            
            #surl = 'https://core-sat.maps.yandex.net/tiles?l=sat&x=%d&y=%d&z=%d'%(x,y,z)
            #print (url)
            tile = get_tile(x,y,z)
            xt = (x-x_min)*256
            yt = (y-y_min)*256
            print (xt,yt)
            full_image[yt:yt+256,xt:xt+256] = tile
    
    for p in points:
        x,y = deg2num_trunc(p[1],p[0],z)
        x=int(256*(x-x_min))
        y=int(256*(y-y_min))
        #print (x,y)
        #if len(track)<20:
        track.append(x)
        track.append(y)
        ctrack.append([x,y])
    
    
    print (ctrack)
    isClosed = False
      
    # Blue color in BGR
    color = (255, 127, 0)
      
    # Line thickness of 2 px
    thickness = 2
      
    # Using cv2.polylines() method
    # Draw a Blue polygon with 
    # thickness of 1 px
    pts = np.array(ctrack,np.int32)
    pts = pts.reshape((-1, 1, 2))
    image = cv2.polylines(full_image, [pts], 
                          isClosed, color, thickness, cv2.LINE_AA)
    print (tuple(pts[-1][0]))
    cv2.circle(image,tuple(pts[-1][0]), 100, (0,0,255), 20, lineType=cv2.LINE_AA)
    #https://stackoverflow.com/questions/31519197/python-opencv-how-to-crop-circle
    #cv2.imwrite("temp-%dc.png"%z, tile)
    cv2.imwrite("%s-%dc.png"%(name,z), full_image)

    for i,p in enumerate(ctrack):
    	print (i,p)

 
msg = "Just a map with a track"
 
# Initialize parser
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("-i", "--input", help = "Input file")
parser.add_argument("-o", "--output", help = "Output file", default="output.png")
parser.add_argument("-z", "--zoom", help = "Zoom level", default=15)


args = parser.parse_args()
    
if not args.input:
	print ("no input gpx")
	exit()

print("input file: %s" % args.input)
zoom = int(args.zoom)
print ("zoom %d"%zoom)
gpx_file = open(args.input, 'r', encoding='utf-8')
gpx = gpxpy.parse(gpx_file)
points = get_gpx_points(gpx)
print ("%d points"%len(points))
output = args.output
tiles = get_osm_tiles(points,output)
