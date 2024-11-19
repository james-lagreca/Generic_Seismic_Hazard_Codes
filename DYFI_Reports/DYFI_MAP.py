import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from matplotlib.colors import ListedColormap
from numpy import mean, percentile, array
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import json
import sys
import os
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patheffects import withStroke
from cartopy.io import shapereader
import matplotlib.patheffects as path_effects
from adjustText import adjust_text
import random
import numpy as np

mpl.style.use('classic')

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

# Prompt the user to enter the zoom level
zoom_factor = float(input("Enter the zoom factor (e.g., 1 for default zoom, 0.5 for closer zoom, 2 for farther view): "))

# Set eq details
mag = 5.9
eqdep = 12.0
eqla = -37.5063
eqlo = 146.4022
degrng = 5.9 * zoom_factor  # Adjust zoom level based on user input
latoff = -0.0
lonoff = -1.2
mstr = '5.9'
place = 'Woods Point, VIC'
evid = '2021-09-21'

# Set the map extent to center around the earthquake
# Adjust the bounds based on `degrng` for zoom
urcrnrlat = eqla + degrng
llcrnrlat = eqla - degrng
urcrnrlon = eqlo + degrng
llcrnrlon = eqlo - degrng

# Set up figure
fig = plt.figure(figsize=(10, 12))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat], crs=ccrs.PlateCarree())


# Add map features
ax.add_feature(cfeature.LAND, facecolor='0.9')
ax.add_feature(cfeature.OCEAN, facecolor='lightskyblue')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAKES, facecolor='lightskyblue')
ax.add_feature(cfeature.RIVERS)
ax.add_feature(cfeature.STATES, linestyle='-', edgecolor='black')

# Add gridlines without visible lines but keep labels
gl = ax.gridlines(draw_labels=True, linewidth=0, dms=True, x_inline=False, y_inline=False)
gl.top_labels = False
gl.right_labels = False

# Ask user for population size threshold
pop_threshold = int(input("Enter the minimum population size for cities to be plotted: "))

# Use Natural Earth data for populated places
shpfilename = shapereader.natural_earth(resolution='10m', category='cultural', name='populated_places')

# Read populated places and plot cities, ensuring they don't overlap with the earthquake symbol
buffer_radius = 1  # Buffer radius to avoid overlap with the earthquake star
reader = shapereader.Reader(shpfilename)


preferred_offset = (-0.3, -0.3)  # Preferred initial offset for placing labels (bottom-left)

texts = []
# Adjust text placement closer to the city markers
for record in reader.records():
    city_name = record.attributes['NAME']
    lat = record.geometry.y
    lon = record.geometry.x

    # Calculate distance from earthquake epicenter
    distance = np.sqrt((lat - eqla)**2 + (lon - eqlo)**2)

    # Only plot cities that meet the population threshold and are within the map extent
    if record.attributes['POP_MAX'] > pop_threshold and \
            (llcrnrlat <= lat <= urcrnrlat) and (llcrnrlon <= lon <= urcrnrlon):

        # Plot the city marker
        ax.plot(lon, lat, 'o', color='black', markersize=5, transform=ccrs.PlateCarree(), zorder=1100)

        # Place the text closer to the city marker with a smaller offset
        text = ax.text(lon + 0.05, lat + 0.05, city_name,
                       fontsize=10, weight='bold', color='black',
                       path_effects=[path_effects.withStroke(linewidth=3, foreground='white')],
                       transform=ccrs.PlateCarree(), zorder=1100)
        texts.append(text)

# Adjust text to avoid overlaps, allowing further movement if the initial placement causes issues
adjust_text(
    texts,
    only_move={'points': 'xy', 'texts': 'xy'},  # Allow text to be adjusted in both x and y directions
    expand_text=(1.2, 1.2),  # Expand space around text labels slightly
    force_text=(5, 5),  # Reduce the force to move texts compared to the original
    avoid_points=[(eqlo, eqla)],  # Avoid the earthquake location
    arrowprops=None
)





# Add scale bar
scalebar = ScaleBar(100, location='lower left', scale_loc='top', units='km', length_fraction=0.2,
                    box_alpha=0.8, color='black', font_properties={'size': 'large'})
ax.add_artist(scalebar)

# Custom colormap definition
colors = [
    (255, 255, 255),  # Intensity 1
    (239, 242, 255),  # Intensity 2
    (176, 217, 255),  # Intensity 3
    (136, 249, 255),  # Intensity 4
    (122, 255, 147),  # Intensity 5
    (255, 241, 0),    # Intensity 6
    (255, 172, 0),    # Intensity 7
    (255, 36, 0),     # Intensity 8
    (200, 0, 0),      # Intensity 9
    (164, 0, 0)       # Intensity 10
]

# Normalize RGB values to [0, 1]
colors = [(r/255.0, g/255.0, b/255.0) for r, g, b in colors]

# Create a custom ListedColormap
custom_cmap = ListedColormap(colors, name='custom_cmap')

##########################################################################################
# plt dyfi
##########################################################################################

# loop thru grid cells values and plt MMI
nresp = 0
min_resp = 0
for dyfi in dyfi_dict:        
    # add to list greater than minObs
    if dyfi['nresp'] > min_resp:
        
        # now plot
        pltx = array(dyfi['geometry'])[:, 0]
        plty = array(dyfi['geometry'])[:, 1]
        
        ax.fill(pltx, plty, fc=colors[int(round(dyfi['intensity'])) - 1], ec='0.45', lw=0.25, transform=ccrs.PlateCarree(), zorder=100)
        
    nresp += dyfi['nresp']
        
##########################################################################################
# annotate
##########################################################################################

# plt earthquake epicentre
x, y = eqlo, eqla
ax.plot(x, y, '*', color='red', markersize=25, markerfacecolor='None', mew=1.5, transform=ccrs.PlateCarree(), zorder=1000)

# Add the number of responses text and set a higher zorder to ensure it stays on top
plttxt = 'Number of Responses = ' + str(nresp)
x, y = llcrnrlon + 0.02 * (urcrnrlon - llcrnrlon), urcrnrlat - 0.02 * (urcrnrlat - llcrnrlat)
props = dict(boxstyle='round', facecolor='w', alpha=1, edgecolor='black', linewidth=1.5)  # Make the box more prominent
ax.text(x, y, plttxt, size=16, ha='left', va='top', bbox=props, transform=ccrs.PlateCarree(), zorder=2000)


##########################################################################################
# make colorbar
##########################################################################################

# set colourbar
plt.gcf().subplots_adjust(bottom=0.15)
cax = fig.add_axes([0.15, 0.15, 0.7, 0.02]) # setup colorbar axes to be better positioned

norm = mpl.colors.Normalize(vmin=0.5, vmax=10.5)
cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=custom_cmap), cax=cax, orientation='horizontal')

# set cb labels
ticks = range(1, 11)
rom_num = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
cb.set_ticks(ticks)
cb.set_ticklabels(rom_num)

# Add colorbar label
titlestr = 'Macroseismic Intensity'
cb.set_label(titlestr, fontsize=16)

# Save the figure
plt.savefig('_'.join((evid.replace('-', ''), place.split(',')[0].replace(' ', '_'), 'gridded_mmi_data_gridded.jpg')), format='jpg', bbox_inches='tight', dpi=300)
plt.show()
