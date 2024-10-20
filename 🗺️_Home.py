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
from functions import logIn,logOut,tab_popup,tooltip_html



# ---LAYOUT---
st.set_page_config(
    page_title="Bunkers",
    initial_sidebar_state="collapsed",
    page_icon="🦇",
    layout="wide",
    
)

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


# st.logo(IMAGE,  link=None, icon_image=IMAGE_2)

#--- UI ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_bunkers_features = conn.read(ttl=ttl,worksheet="bunkers_features")
df_bunkers_observations = conn.read(ttl=ttl,worksheet="bunkers_observations")
df_references = conn.read(ttl=ttl_references,worksheet="df_users")

if "login" not in st.session_state:
    logIn(df_references)
    st.stop()

with st.sidebar:
    logOut()
    st.divider()

# try:
try:
    table_dictionary = tab_popup(df_bunkers_observations)
    df_bunkers_features["Last survey"] = df_bunkers_features.apply(lambda x: "Uninhabited" if table_dictionary[x['id_bunker']].iloc[-1,:].sum() == 0
                                               else "Inhabited",axis=1) 
    df_bunkers_features["icon_data"] = df_bunkers_features.apply(lambda x: "icons/bunker_empty.png" 
                                                                 if x['Last survey']=='Uninhabited'
                                                                 (else "icons/bunker_full.png" if x['Last survey']=='Inhabited'
                                                                 else 'icons/bunker_no_data.png'), 
                                                                 axis=1)
except: 
    pass
    
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



folium.LayerControl().add_to(map)    

for i in range(len(df_bunkers_features)):

    html_tooltip = tooltip_html(i,df_bunkers_features)
    tooltip = folium.Tooltip(folium.Html(html_tooltip, script=True))

    try:
        html_popup = table_dictionary[df_bunkers_features.iloc[i]['id_bunker']].astype('int').replace({0:'-'}).to_html(
            classes="table table-striped table-hover table-condensed table-responsive"
        )
        popup = folium.Popup(html_popup, max_width=700)
    except:
        popup = 'NO DATA'
    
    fouctie_loop = functie_dictionary[df_bunkers_features.iloc[i]['Last survey']]

    folium.Marker([df_bunkers_features.iloc[i]['lat'], df_bunkers_features.iloc[i]['lng']],
                  popup=popup,
                  tooltip=html_tooltip,
                  icon=folium.features.CustomIcon(df_bunkers_features.iloc[i]["icon_data"], icon_size=ICON_SIZE)
                 ).add_to(fouctie_loop)

output_2 = st_folium(map,returned_objects=["last_active_drawing"],width=OUTPUT_width, height=OUTPUT_height,
             feature_group_to_add=list(functie_dictionary.values()))

try:
    try:
        id = str(output_2["last_active_drawing"]['geometry']['coordinates'][0])+str(output_2["last_active_drawing"]['geometry']['coordinates'][1])
        name = f"{id}"
    except:
        id = str(output_2["last_active_drawing"]['geometry']['coordinates'][0][0][0])+str(output_2["last_active_drawing"]['geometry']['coordinates'][0][0][1])
        name = f"{id}"

    with st.sidebar:
        #---FOR THE PICTURE---
        try:
            res = drive.get(name).read()                
            with st.expander("Zie media"):
                try:
                    st.image(res)
                except:
                    st.video(res)
            if st.button("Waarneming bijwerken",use_container_width=True):
                update_item()

            with st.form("entry_form", clear_on_submit=True,border=False):
                submitted = st.form_submit_button(":red[**Verwijder waarneming**]",use_container_width=True)
                if submitted:
                    # if waarnemer ==  df_point.set_index("key").loc[id,"waarnemer"]:
                    db.delete(id)
                    drive.delete(name)
                    st.success('Waarneming verwijderd', icon="✅")
                    st.page_link("🗺️_Home.py", label="vernieuwen", icon="🔄",use_container_width=True)
                        # else:
                        #     st.warning('Je kunt deze observatie niet uitwissen. Een andere gebruiker heeft het gemarkeerd.', icon="⚠️")
         #---FOR THE PICTURE---               
        except:
            # st.info('Geen foto opgeslagen voor deze waarneming')

            # if st.button("Waarneming bijwerken",use_container_width=True):
            #     update_item()

            
            with st.form("entry_form", clear_on_submit=True,border=False):
                submitted = st.form_submit_button(":red[**Verwijder waarneming**]",use_container_width=True)
                if submitted:
                    df = conn.read(ttl=0,worksheet="bunkers_features")
                    df_filter = df[df["key"]==id]
                    df_drop = df[~df.apply(tuple, axis=1).isin(df_filter.apply(tuple, axis=1))]
                    conn.update(worksheet='bunkers_features',data=df_drop)
                    st.success('Waarneming verwijderd', icon="✅") 
                    st.page_link("🗺️_Home.py", label="Vernieuwen", icon="🔄",use_container_width=True)

except:
    st.stop()

    
# except:
#     st.image("https://media.istockphoto.com/photos/open-empty-cardboard-box-on-a-white-background-picture-id172167710?k=6&m=172167710&s=612x612&w=0&h=Z4fueCweh9q-X_VBRAPCYSalyaAnXG3ioErb8oJSVek=")
#     st.stop()
