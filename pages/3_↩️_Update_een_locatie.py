import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random

import folium
from folium.plugins import Draw, Fullscreen, LocateControl, GroupedLayerControl
from streamlit_folium import st_folium
import datetime
from datetime import datetime, timedelta, date
import random

import ast

from credentials import *


#---LAYOUT---
st.set_page_config(
    page_title="Bunkers & Kasten",
    initial_sidebar_state="collapsed",
    page_icon="🦇",
    layout="wide",  
)

from functions import logIn,logOut,tab_popup,update_item

st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] svg {
        height: 0rem;
        width: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, .viewerBadge_text__1JaDK{ display: none; } #MainMenu{ visibility: hidden; } footer { visibility: hidden; } header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True)


st.markdown("""
<style>
    div.block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; margin-top: 0rem; margin-bottom: 0rem;}
</style>
""" , unsafe_allow_html=True)


st.logo(IMAGE_2,  link=None, icon_image=IMAGE_2)

# --- DATASETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_bunkers_features = conn.read(ttl=ttl,worksheet="bunkers_features")
df_bunkers_observations = conn.read(ttl=ttl,worksheet="bunkers_observations")
df_references = conn.read(ttl=ttl_references,worksheet="df_users")

#--- App ---
if "login" not in st.session_state:
    logIn(df_references)
    st.stop()

with st.sidebar:
    logOut()
    st.divider()

table_dictionary = tab_popup(df_bunkers_observations)


dict_presences = {}

for id in df_bunkers_observations.id_bunker.unique():
    try:
        
        if (table_dictionary[id].iloc[-1,4:-1].sum() == 0) & (table_dictionary[id].iloc[:-1,4:-1].sum().sum() > 0):
            dict_presences[id] = "Niet bewoond in laatste onderzoek"
        elif table_dictionary[id].iloc[-1,4:-1].sum() > 0:
            dict_presences[id] = "Bewoond in laatste onderzoek"
        elif len(table_dictionary[id].iloc[:,4:-1].sum()) == 0:
            dict_presences[id] = "Nooit bewoond tijdens het onderzoek"
            
    except:
        continue
        
df_bunkers_features["Last survey"] = df_bunkers_features["id_bunker"].map(dict_presences).fillna("Geen data")

map = folium.Map(tiles=None,position=[df_bunkers_features['lat'].mean(),df_bunkers_features['lng'].mean],)
LocateControl(auto_start=True,position="topright").add_to(map)
Fullscreen(position="topright").add_to(map)

functie_dictionary = {}
functie_len = df_bunkers_features['Last survey'].unique()

for functie in functie_len:
    functie_dictionary[functie] = folium.FeatureGroup(name=functie)    

for feature_group in functie_dictionary.keys():
    map.add_child(functie_dictionary[feature_group])

folium.TileLayer('OpenStreetMap',overlay=False,show=True,name="Streets").add_to(map)
folium.TileLayer(tiles="Cartodb Positron",overlay=False,show=False,name="Light").add_to(map)
folium.TileLayer('Cartodb dark_matter',overlay=False,show=False,name="Dark").add_to(map)
folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',attr='Google_map',overlay=False,show=False,name="Satellite").add_to(map)

folium.LayerControl().add_to(map)    

for i in range(len(df_bunkers_features)):
    
    fouctie_loop = functie_dictionary[df_bunkers_features.iloc[i]['Last survey']]

    if df_bunkers_features.iloc[i]['class_hybernate'] == 'Bunker': 
        icon="square"
    elif df_bunkers_features.iloc[i]['class_hybernate'] == 'Vleermuiskast':
        icon="circle"
    
    if df_bunkers_features.iloc[i]['Last survey'] == "Niet bewoond in laatste onderzoek":
        color='orange'
    elif df_bunkers_features.iloc[i]['Last survey'] == "Bewoond in laatste onderzoek":
        color='red'
    elif df_bunkers_features.iloc[i]['Last survey'] == "Nooit bewoond tijdens het onderzoek":
        color='green'
    elif df_bunkers_features.iloc[i]['Last survey'] == "Geen data":
        color='yellow'

    folium.Marker([df_bunkers_features.iloc[i]['lat'], df_bunkers_features.iloc[i]['lng']],
                  icon=folium.plugins.BeautifyIcon(icon_shape=icon,
                                                   border_width=5,
                                                   icon='',
                                   background_color=color,
                                   border_color=color
                                  )
                 ).add_to(fouctie_loop)

output = st_folium(map,returned_objects=["last_object_clicked"],width=OUTPUT_width, height=OUTPUT_height,
             feature_group_to_add=list(functie_dictionary.values()))


try:
    if len(output["last_object_clicked"]) != 0:
      coordinates = output["last_object_clicked"]
             
      lng = coordinates["lng"]
      lat = coordinates['lat']
      
      id = str(lng)+str(lat)
      
      with st.sidebar:
          if st.button("Waarneming bijwerken",use_container_width=True):
              update_item(id)
  
          with st.form("entry_form", clear_on_submit=True,border=False):
              submitted = st.form_submit_button(":red[**Verwijder waarneming**]",use_container_width=True)
              if submitted:
                  df_filter = df_bunkers_features[df_bunkers_features["id_bunker"]==id]
                  df_drop = df_bunkers_features[~df_bunkers_features.apply(tuple, axis=1).isin(df_filter.apply(tuple, axis=1))]
                  conn.update(worksheet='bunkers_features',data=df_drop)
                  st.success('Waarneming verwijderd', icon="✅") 
                  st.page_link("🗺️_Home.py", label="Vernieuwen", icon="🔄",use_container_width=True)

except:
    pass
