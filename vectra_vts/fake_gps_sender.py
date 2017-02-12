import csv
import os
import time
import requests
loc_coords = []
loc_data = csv.reader(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'go_track_trackspoints.csv'), 'r'))

for ld in loc_data:
	loc_coords.append([])
	loc_coords[-1].append(float(ld[0])) #insert the latitude
	loc_coords[-1].append(float(ld[1])) #insert the longitude
	#ignoring the altitude (2)
for k in  range (len(loc_coords)):
	print loc_coords[k]
	r = requests.post("http://localhost:8000/gps/098765/",data={'lat':loc_coords[k][0],'long':loc_coords[k][1]})
	print r.status_code , r.reason
	time.sleep(0.01)
