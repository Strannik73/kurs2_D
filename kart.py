import folium
from jinja2 import Template
import pandas as pd
import requests

url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
world_geo = requests.get(url).json()

df = pd.DataFrame({
    'country': [feature['properties']['name'] for feature in world_geo['features']],
    'value': range(len(world_geo['features']))
})

m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles='OpenStreetMap',
    world_copy_jump=True
)

folium.GeoJson(
    world_geo,
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 0.5
        }
).add_to(m)


m.add_child(folium.LatLngPopup())

m.save('world1.html')
