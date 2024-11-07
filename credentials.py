import streamlit as st

# --- DIMENSIONS ---
OUTPUT_width = '95%'
OUTPUT_height = 550

# --- DATASET CACHE ---
ttl = 0
ttl_references = '10m'

# --- SIDEBAR ---
# IMAGE = "image/logo.png"
IMAGE_2 ="icons/menu.jpg"

CLASS_HYBERNATE_OPTIONS = ['Bunker','Vleermuiskast']

SURROUNDING_OPTIONS = ['In de duinen', 'Loofbos', 'Naaldbos/groenblijvend bos']

BATBOX_SHAPE_OPTIONS = ['Platte kast', 'Ronde kast']

BATBOX_KRAAMVEBLIJFKAST_OPTION = ['Ja','Nee']

TYPE_BUNKER_OPTIONS = ['Open','Niet toegankelijk']

BAT_NAMES = ['Gewone dwergvleermuis','Ruige dwergvleermuis', 'Laatvlieger','Rosse vleermuis',
             'Gewone grootoorvleermuis','Meervleermuis','Watervleermuis','...Andere(n)']

# Create the legend template as an HTML element
legend_template = """
{% macro html(this, kwargs) %}
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index: 9999; background-color: rgba(255, 255, 255, 0.7);
     border-radius: 6px; padding: 10px; font-size: 10.5px; left: 20px; top: 320px;'>     
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><strong>Funtie</strong></li>
    <li><span style='background: yellow; opacity: 0.75;'></span>Geen data</li>
    <li><span style='background: green; opacity: 0.75;'></span>Nooit bewoond tijdens het onderzoek</li>
    <li><span style='background: orange; opacity: 0.75;'></span>Niet bewoond in laatste onderzoek</li>
    <li><span style='background: red; opacity: 0.75;'></span>Bewoond in laatste onderzoek</li>
    <li><strong>Typen</strong></li>
    <li><span class="fa fa-circle" style="color:grey" opacity: 0.75;'></span>Vleermuiskast</li>
    <li><span class="fa-solid fa-square" style="color:grey" opacity: 0.75;'></span>Bunker (Open)</li>
    <li><span class="fa-regular fa-square" style="color:grey" opacity: 0.75;'></span>Bunker (Niet toegankelijk)</li>
  </ul>
</div>
</div> 
<style type='text/css'>
  .maplegend .legend-scale ul {margin: 0; padding: 0; color: #0f0f0f;}
  .maplegend .legend-scale ul li {list-style: none; line-height: 18px; margin-bottom: 1.5px;}
  .maplegend ul.legend-labels li span {float: left; height: 16px; width: 16px; margin-right: 4.5px;}
</style>
{% endmacro %}
"""
