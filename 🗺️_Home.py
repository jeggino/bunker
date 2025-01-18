import streamlit as st
from supabase import create_client, Client
import pandas as pd
import random

import folium
from folium.plugins import Draw, Fullscreen, LocateControl, GroupedLayerControl
from streamlit_folium import st_folium
from branca.element import Template, MacroElement

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

from functions import logIn,logOut,tab_popup,popup_table

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


st.logo(IMAGE,  link=None, size="large",icon_image=IMAGE)

# --- DATASETS ---
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

rows_users = supabase.table("df_users").select("*").execute()
df_references = pd.DataFrame(rows_users.data)

rows_bunkers_features = supabase.table("bunkers_features").select("*").execute()
df_bunkers_features = pd.DataFrame(rows_bunkers_features.data)

rows_bunkers_observations = supabase.table("bunkers_observations").select("*").execute()
df_bunkers_observations = pd.DataFrame(rows_bunkers_observations.data).drop('key',axis=1)

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

map = folium.Map(tiles=None,position=[df_bunkers_features['lat'].mean(),df_bunkers_features['lng'].mean],zoom_start=8)
LocateControl(auto_start=False,position="topright").add_to(map)
Fullscreen(position="topright").add_to(map)

macro = MacroElement()
macro._template = Template(legend_template)

map.get_root().add_child(macro)

functie_dictionary = {}
functie_len = df_bunkers_features['Last survey'].unique()

for functie in functie_len:
    functie_dictionary[functie] = folium.FeatureGroup(name=functie)    

for feature_group in functie_dictionary.keys():
    map.add_child(functie_dictionary[feature_group])

folium.TileLayer('OpenStreetMap',overlay=False,show=True,name="Stratenkaart").add_to(map)
folium.TileLayer(tiles="Cartodb Positron",overlay=False,show=False,name="Witte contrastkaart").add_to(map)
folium.TileLayer(tiles='https://api.mapbox.com/styles/v1/jeggino/cm2vtvb2l000w01qz9wet0mv9/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ',
                 attr='XXX Mapbox Attribution',overlay=False,show=False,name="Satellietkaart").add_to(map)

folium.LayerControl().add_to(map)    

for i in range(len(df_bunkers_features)):
    
    fouctie_loop = functie_dictionary[df_bunkers_features.iloc[i]['Last survey']]

    if df_bunkers_features.iloc[i]['class_hybernate'] == 'Bunker': 
        icon_shape=""
        icon=''
        if df_bunkers_features.iloc[i]['type_bunker'] == 'Niet toegankelijk':
            border_width=4
        else:
            border_width=0
        
    elif df_bunkers_features.iloc[i]['class_hybernate'] == 'Vleermuiskast':
        icon_shape="circle"
        icon=''
        if df_bunkers_features.iloc[i]['kraamverblijjkast'] == 'Ja':
            border_width=4
        else:
            border_width=0
    
    if df_bunkers_features.iloc[i]['Last survey'] == "Niet bewoond in laatste onderzoek":
        color='orange'
    elif df_bunkers_features.iloc[i]['Last survey'] == "Bewoond in laatste onderzoek":
        color='red'
    elif df_bunkers_features.iloc[i]['Last survey'] == "Nooit bewoond tijdens het onderzoek":
        color='green'
    elif df_bunkers_features.iloc[i]['Last survey'] == "Geen data":
        color='yellow'

    folium.Marker([df_bunkers_features.iloc[i]['lat'], df_bunkers_features.iloc[i]['lng']],
                  icon=folium.plugins.BeautifyIcon(icon_shape=icon_shape,
                                                   border_width=border_width,
                                                   icon=icon,
                                   background_color=color,
                                   border_color='black'
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
        table_dictionary[id].iloc[:,6:]
        popup_table(id,output,df_bunkers_features,table_dictionary)
        
        

except:
    pass

