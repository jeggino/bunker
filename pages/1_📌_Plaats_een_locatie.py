import streamlit as st

import folium
from folium.plugins import Draw, Fullscreen, LocateControl
from streamlit_folium import st_folium

import pandas as pd
from supabase import create_client, Client

import datetime
from datetime import datetime, timedelta, date

from credentials import *
from functions import insert_bunker_fearures,map,input_data



# ---LAYOUT---
st.set_page_config(
    page_title="Bunkers & Kasten",
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

   

# --- APP ---  
st.logo(IMAGE,  link=None, size="large",icon_image=IMAGE)

try:
    waarnemer = st.session_state.login['name']
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
            
    output_map = map()
    
    try:
        if len(output_map["features"]) != 0:
            input_data(output_map)
    except:
        st.stop()
    
except:
    st.switch_page("🗺️_Home.py")
