# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 16:32:05 2019

@author: u56903
"""
import json
import sys
import os
import folium
from folium.plugins import MarkerCluster
import numpy as np

# Get the GeoJSON file path from command line argument or prompt the user
if len(sys.argv) > 1:
    jsonFilePath = sys.argv[1]
else:
    # Prompt the user for the file path
    jsonFilePath = input("Enter the path to the GeoJSON file: ")

# Check if the provided file path exists
if not os.path.exists(jsonFilePath):
    print("The file does not exist. Please check the path.")
    sys.exit(1)

# Load GeoJSON data
with open(jsonFilePath) as f:
    data = json.load(f)

dyfi_dict = []
for feature in data['features']:
    tmp = {'geometry': feature['geometry']['coordinates'][0],
           'centroid': feature['properties']['center']['coordinates'],
           'intensity': feature['properties']['intensityFine'],
           'nresp': feature['properties']['nresp']}
    
    # append to list
    dyfi_dict.append(tmp)
        
###############################################################################
# set eq details
###############################################################################

# Woods Point
mag  = 5.9
eqdep = 12.0
eqla = -37.5063
eqlo = 146.4022
degrng = 5.9
latoff = -0.0
lonoff = -1.2
mstr = '5.9'
place = 'Woods Point, VIC'
evid = '2021-09-21'

##########################################################################################
# Set up interactive map using folium
##########################################################################################

# Create a folium map centered at the earthquake location
m = folium.Map(location=[eqla, eqlo], zoom_start=7, tiles='OpenStreetMap')

# Add earthquake epicenter marker
folium.Marker(
    location=[eqla, eqlo],
    popup=f"<strong>Earthquake Epicenter</strong><br>Magnitude: {mag}",
    icon=folium.Icon(color='red', icon='star')
).add_to(m)

# Add scale bar using the `MeasureControl` plugin from folium
folium.plugins.MeasureControl(primary_length_unit='kilometers').add_to(m)

# Custom colormap definition
colors = [
    '#FFFFFF',  # Intensity 1
    '#EFF2FF',  # Intensity 2
    '#B0D9FF',  # Intensity 3
    '#88F9FF',  # Intensity 4
    '#7AFF93',  # Intensity 5
    '#FFF100',  # Intensity 6
    '#FFAC00',  # Intensity 7
    '#FF2400',  # Intensity 8
    '#C80000',  # Intensity 9
    '#A40000'   # Intensity 10
]

##########################################################################################
# Plot DYFI data
##########################################################################################

# Marker cluster for all dyfi points
marker_cluster = MarkerCluster().add_to(m)

# Loop through each DYFI dictionary entry and add polygons
for dyfi in dyfi_dict:
    if dyfi['nresp'] > 0:
        intensity_index = int(np.clip(round(dyfi['intensity']) - 1, 0, len(colors) - 1))
        color = colors[intensity_index]
        polygon_coords = [[lat, lon] for lon, lat in dyfi['geometry']]
        folium.Polygon(
            locations=polygon_coords,
            color=color,
            weight=0.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.6
        ).add_to(marker_cluster)

##########################################################################################
# Annotate with population centers
##########################################################################################

# Ask user for population size threshold
pop_threshold = int(input("Enter the minimum population size for cities to be plotted: "))

# Use Natural Earth data for populated places (10m resolution)
from cartopy.io import shapereader
shpfilename = shapereader.natural_earth(resolution='10m', category='cultural', name='populated_places')
reader = shapereader.Reader(shpfilename)
for record in reader.records():
    # Get latitude, longitude, and name of the city
    city_name = record.attributes['NAME']
    lat = record.geometry.y
    lon = record.geometry.x

    # Only plot cities with population over user-defined threshold within the current map extent
    if record.attributes['POP_MAX'] > pop_threshold:
        folium.Marker(
            location=[lat, lon],
            popup=f"<strong>{city_name}</strong>",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

##########################################################################################
# Save the interactive map
##########################################################################################

# Save the folium map to an HTML file
output_file = '_'.join((evid.replace('-', ''), place.split(',')[0].replace(' ', '_'), 'interactive_map.html'))
m.save(output_file)

print(f"Interactive map saved as {output_file}")
