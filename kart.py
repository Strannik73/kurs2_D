import folium
from jinja2 import Template
import pandas as pd
import requests

# Загружаем GeoJSON стран мира
url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
world_geo = requests.get(url).json()

# Делаем простые данные (например, случайные значения)
df = pd.DataFrame({
    'country': [feature['properties']['name'] for feature in world_geo['features']],
    'value': range(len(world_geo['features']))
})

# Создаём карту
m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles='OpenStreetMap'
)

# стили
folium.GeoJson(
    world_geo,
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'black',
        'weight': 0.5
        }
).add_to(m)

class ClickHandler(folium.MacroElement):
    def __init__(self):
        super().__init__()
        self._template = Template("""
        {% macro script(this, kwargs) %}
        
        //карта
        var map = {{this._parent.get_name()}};
        
        //клик
        map.on('click', function(e) {
            
            //координаты
            var lat = e.latlng.lat;
            var lon = e.latlng.lng;

            //отправка к main.py
            fetch('/weather_by_coords', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    lat: lat,
                    lon: lon
                })
            })
            
            //получение ответа
            .then(resp => resp.json())
            
            .then(data => {
                L.popup()
                 .setLatLng(e.latlng)
                 .setContent(
                    "<b>" + data.city + "</b><br>" +
                    " " + data.temp + "°C<br>" +
                    data.descr
                 )
                 .openOn(map);
            })
            
            //ошибка
            .catch(err => {console.error("Ошибка:", err);});
        });
        {% endmacro %}
        """)

# координаты при клике
m.add_child(folium.LatLngPopup())

m.save('world.html')
m