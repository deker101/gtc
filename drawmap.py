import os
import gpxpy
import gpxpy.gpx
from tile import deg2num, deg2num_trunc, get_tile

from PIL import Image, ImageDraw
import cv2
import numpy as np
import math
import argparse

fps = 25

def get_gpx_points(gpx):
    first_time = None
    points = []
    for track in gpx.tracks:
        print (track)
        for segment in track.segments:
            
            print (segment)
            for point in segment.points:
                if not first_time:
                    first_time=point.time.timestamp()

                p = [point.longitude, point.latitude, point.elevation, point.time.timestamp()-first_time]
                points.append(p)
                print (p)
                
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
    vtrack = []
    x_min,y_min = deg2num(latmax,lonmin,z)
    x_min-=1
    y_min-=1
    #print (z, x,y)
    x_max,y_max = deg2num(latmin,lonmax,z)
    x_max+=1
    y_max+=1
    #print (z, w, h)
    w=(x_max-x_min)+1
    h=(y_max-y_min)+1
    w*=256
    h*=256
    print (z, w, h)
    full_image = np.zeros((h,w,3), np.uint8)
    tiles_cnt = (x_max-x_min)*(y_max-y_min)
    dnl=0
    #get all tiles:
    if False:
        for x in range(x_min,x_max+1,1):
            for y in range(y_min,y_max+1,1):
                #url = 'https://c.tile.openstreetmap.de/%d/%d/%d.png'%(z,x,y)
                #url = 'https://stamen-tiles.a.ssl.fastly.net/toner/%d/%d/%d.png'%(z,x,y)
                
                #surl = 'https://core-sat.maps.yandex.net/tiles?l=sat&x=%d&y=%d&z=%d'%(x,y,z)
                #print (url)
                tile = get_tile(x,y,z)
                dnl+=1
                xt = (x-x_min)*256
                yt = (y-y_min)*256
                print (dnl, tiles_cnt,xt,yt)
                full_image[yt:yt+256,xt:xt+256] = tile
    
    if True:
        print ('hello')
        tiles = []
        for p in points:
            lat = p[1]
            lon = p[0]
            x,y = deg2num(lat,lon,z)
            
            
            #t = (xt,yt)
            for dtx in [-1, 0, 1]:
                for dty in [-1, 0, 1]:
                    t = (x+dtx,y+dty)
                    if t not in tiles:
                        tile = get_tile(t[0],t[1],z)
                        xt = (t[0]-x_min)*256
                        yt = (t[1]-y_min)*256
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
    #cv2.circle(image,tuple(pts[-1][0]), 100, (0,0,255), 20, lineType=cv2.LINE_AA)
    #https://stackoverflow.com/questions/31519197/python-opencv-how-to-crop-circle
    #cv2.imwrite("temp-%dc.png"%z, tile)
    cv2.imwrite("%s-%dc.png"%(name,z), full_image)
    
    #exit()

    for i,p in enumerate(points):
        x,y = deg2num_trunc(p[1],p[0],z)
        x=int(256*(x-x_min))
        y=int(256*(y-y_min))
        #print (x,y)
        #if len(track)<20:
        if p[3] == 0:
            #for pp in range(fps):
            vtrack.append([x,y,0.0])
            #break
        else:
            td = p[3]-points[i-1][3]
            prev_x,prev_y = deg2num_trunc(points[i-1][1],points[i-1][0],z)
            next_x,next_y = deg2num_trunc(p[1],p[0],z)
            framecnt = int(td*fps)
            print ('prev', prev_x, prev_y)
            print ('next', next_x, next_y)
            
            for d in range(framecnt):
                #print (d)
                #print ('td = ',td, d)
                x = prev_x + (next_x-prev_x)/framecnt*d
                y = prev_y + (next_y-prev_y)/framecnt*d
                dx = next_x-prev_x
                dy = next_y-prev_y
                a = math.atan2(dy, dx)/math.pi*180
                a+=360.0
                #if a < 0:
                #    a = 360 + a
                x=round(256*(x-x_min))
                y=round(256*(y-y_min))
                print (i, 'td = ',td, d, x,y)
                vtrack.append([x,y,a])
    vtrack[0][2]=vtrack[1][2]
            #break
    print (ctrack[0:3])
    print (vtrack)
    print (len(vtrack))
    #exit()  
    mask = np.zeros((200, 200, 4))
    mask = cv2.circle(mask, (100,100), 100, (255,255,255), -1)
    angle = 3.0
    for i,p in enumerate(vtrack[:-10]):
        x_s=0
        y_s=0
        a_s=0
        for j in range(10):
            x_s += vtrack[i+j][0]
            y_s += vtrack[i+j][1]
            a_s += vtrack[i+j][2]
        x_s/=10
        y_s/=10
        a_s/=10

        for j in range(10):
            vtrack[i+j][0] = x_s
            vtrack[i+j][1] = y_s
            vtrack[i+j][2] = a_s

            
    for i,p in enumerate(vtrack):
        print (i,p)
        x = round(p[0]-100)
        y = round(p[1]-100)
        #res = np.zeros((200, 200, 4))
        res = full_image[y:y+200,x:x+200]
        
        angle = p[2]+90.0
        rot_mat = cv2.getRotationMatrix2D((100,100), angle, 1.0) #1.0 - scale
        res = cv2.warpAffine(res, rot_mat, res.shape[1::-1], flags=cv2.INTER_LINEAR)
        
        res = cv2.cvtColor(res, cv2.COLOR_BGR2BGRA)
        res[:, :, 3] = mask[:,:,0]
        res = cv2.cvtColor(res, cv2.COLOR_BGR2BGRA)
        
        cv2.imwrite("output/res_%06d.png"%i, res)
        #image_center = tuple(100,100)
        
        
    return

    
 
msg = "Just a map with a track"
 
# Initialize parser
parser = argparse.ArgumentParser(description = msg)
parser.add_argument("-i", "--input", help = "Input file")
parser.add_argument("-o", "--output", help = "Output file", default="output/output.png")
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
