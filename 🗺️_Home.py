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



# ---LAYOUT---
st.set_page_config(
    page_title="Bunkers",
    initial_sidebar_state="collapsed",
    page_icon="📝",
    layout="wide",
    
)

#---DATASET---
ttl = '10m'
ttl_references = '10m'
conn = st.connection("gsheets", type=GSheetsConnection)
df_point = conn.read(ttl=ttl,worksheet="bunkers")
df_references = conn.read(ttl=ttl_references,worksheet="df_users")


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



reduce_header_height_style = """
<style>
    div.block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; margin-top: 0rem; margin-bottom: 0rem;}
</style>
""" 

st.markdown(reduce_header_height_style, unsafe_allow_html=True)



# --- DIMENSIONS ---
OUTPUT_width = 1190
OUTPUT_height = 450
ICON_SIZE = (60,35)


# --- FUNCTIONS ---
def tooltip_html(row):
    
    i = row

    id_bunker=df_points['id_bunker'].iloc[i]
    status=df_points['Last survey'].iloc[i]
    var_1=df_points['var_1'].iloc[i]
    var_2=df_points['var_2'].iloc[i]
    var_3=df_points['var_3'].iloc[i]
    var_4=df_points['var_4'].iloc[i]

       

    left_col_color = "#19a7bd"
    right_col_color = "#f2f0d3"
    
    html = """<!DOCTYPE html>
    <html>
    <table style="height: 126px; width: 300;">
    <tbody>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Bunker</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(id_bunker) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Last survey</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(status) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Variable 1</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(var_1) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Variable 2</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(var_2) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Variable 3</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(var_3) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Variable 4</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(var_4) + """
    </tr>
    </tbody>
    </table>
    </html>
    """
    return html


def logIn():
    name = st.text_input("Vul uw gebruikersnaam in, alstublieft",value=None)  
    password = st.text_input("Vul uw wachtwoord in, alstublieft")
    try:
        if name == None:
            st.stop()
        
        index = df_references[df_references['username']==name].index[0]
        true_password = df_references.loc[index,"password"]

    except:
        st.warning("De gebruikersnaam is niet correct.")
        st.stop()
                             
    if st.button("logIn"):
        if password == true_password:
            st.session_state.login = {"name": name, "password": password}
            st.rerun()

        else:
            st.markdown(f"Sorry {name.split()[0]}, het wachtwoord is niet correct.")

        
def logOut():
    if st.button("logOut",use_container_width=True):
        del st.session_state.login
        del st.session_state.project     
        st.rerun()

        

#---APP---
IMAGE = "image/logo.png"
IMAGE_2 ="image/menu.jpg"
st.logo(IMAGE,  link=None, icon_image=IMAGE_2)


if "login" not in st.session_state:
    logIn()
    st.stop()




with st.sidebar:
    logOut()
    st.divider()

try:
    try:        
        df_2["datum"] = pd.to_datetime(df_2["datum"]).dt.date
    
    
        st.sidebar.subheader("Filter op",divider=False)
        d = st.sidebar.slider("Datum", min_value=df_2.datum.min(),max_value=df_2.datum.max(),value=(df_2.datum.min(), df_2.datum.max()),format="DD-MM-YYYY")
        
        df_2 = df_2[(df_2['datum']>=d[0]) & (df_2['datum']<=d[1])]
    except:
        pass
        
    if st.session_state.project['opdracht'] in ["Vleermuizen","Vogels",'Vogels-Overig']:
        species_filter_option = df_2["sp"].unique()
        species_filter = st.sidebar.multiselect("Sorten",species_filter_option,species_filter_option)
        df_2 = df_2[df_2['sp'].isin(species_filter)]

    st.sidebar.divider()
    
    df_2["icon_data"] = df_2.apply(lambda x: None if x["geometry_type"] in ["LineString","Polygon"] 
                                   else (icon_dictionary[x["soortgroup"]][x["sp"]][x["functie"]] if x["soortgroup"] in ['Vogels','Vleermuizen',"Vogels-Overig"] 
                                         else icon_dictionary[x["soortgroup"]][x["functie"]]), 
                                   axis=1)
    
    df_2 = df_2.reset_index(drop=True)
    map = folium.Map(tiles=None)
    LocateControl(auto_start=False,position="topleft").add_to(map)
    Fullscreen(position="topleft").add_to(map)
    
    functie_dictionary = {}
    functie_len = df_2['functie'].unique()
    
    for functie in functie_len:
        functie_dictionary[functie] = folium.FeatureGroup(name=functie)    

    # functie_dictionary["geometry"] = folium.FeatureGroup(name="geometry")
    
    for feature_group in functie_dictionary.keys():
        map.add_child(functie_dictionary[feature_group])

    folium.TileLayer('OpenStreetMap',overlay=False,show=True,name="Streets").add_to(map)
    folium.TileLayer(tiles="Cartodb Positron",overlay=False,show=False,name="Light").add_to(map)
    folium.TileLayer('Cartodb dark_matter',overlay=False,show=False,name="Dark").add_to(map)
    
    
    
    folium.LayerControl().add_to(map)    

    for i in range(len(df_2)):

        if df_2.iloc[i]['geometry_type'] == "Point":

            if (df_2.iloc[i]['sp']=="Huismus") & (df_2.iloc[i]['functie'] in ["mogelijke nestlocatie","nestlocatie"]):
                ICON_SIZE_2 = ICON_SIZE_huismus

            elif df_2.iloc[i]['functie'] == "Waarneming rat doorgegeven, geen actie op ondernomen":
                ICON_SIZE_2 = ICON_SIZE_rat_maybe

            elif (df_2.iloc[i]['sp'] in ['Ruige dwergvleermuis', 'Laatvlieger','Rosse vleermuis','Meervleermuis','Watervleermuis']):
                ICON_SIZE_2 = ICON_SIZE_BAX_EXTRA

            if (df_2.iloc[i]['sp']=="...Andere(n)") & (df_2.iloc[i]['functie'] in ["mogelijke nestlocatie","nestlocatie",'geen / onbekend']):
                ICON_SIZE_2 = ICON_SIZE_BIRD

            elif (df_2.iloc[i]['sp'] in ['...Andere(n)']):
                ICON_SIZE_2 = ICON_SIZE_ANDER

            else:                
                ICON_SIZE_2 = ICON_SIZE
                

            html = popup_html(i)
            popup = folium.Popup(folium.Html(html, script=True), max_width=300)
            fouctie_loop = functie_dictionary[df_2.iloc[i]['functie']]
    
            folium.Marker([df_2.iloc[i]['lat'], df_2.iloc[i]['lng']],
                          popup=popup,
                          icon=folium.features.CustomIcon(df_2.iloc[i]["icon_data"], icon_size=ICON_SIZE_2)
                         ).add_to(fouctie_loop)
                


        elif df_2.iloc[i]['geometry_type'] == "Polygon":
            html = popup_polygons(i)
            popup = folium.Popup(folium.Html(html, script=True), max_width=300)
            fouctie_loop = functie_dictionary[df_2.iloc[i]['functie']]
            location = df_2.iloc[i]['coordinates']
            location = ast.literal_eval(location)
            location = [i[::-1] for i in location[0]]
                        
            if df_2.iloc[i]['functie']=="Paringsgebied":
                fill_color="red"

            else:
                fill_color="green"
                
            folium.Polygon(location,fill_color=fill_color,weight=0,fill_opacity=0.5,
                          popup=popup
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

                if st.button("Waarneming bijwerken",use_container_width=True):
                    update_item()

                
                with st.form("entry_form", clear_on_submit=True,border=False):
                    submitted = st.form_submit_button(":red[**Verwijder waarneming**]",use_container_width=True)
                    if submitted:
                        df = conn.read(ttl=0,worksheet="df_observations")
                        df_filter = df[df["key"]==id]
                        df_drop = df[~df.apply(tuple, axis=1).isin(df_filter.apply(tuple, axis=1))]
                        conn.update(worksheet='df_observations',data=df_drop)
                        st.success('Waarneming verwijderd', icon="✅") 
                        st.page_link("🗺️_Home.py", label="Vernieuwen", icon="🔄",use_container_width=True)

    except:
        st.stop()

except:
    st.image("https://media.istockphoto.com/photos/open-empty-cardboard-box-on-a-white-background-picture-id172167710?k=6&m=172167710&s=612x612&w=0&h=Z4fueCweh9q-X_VBRAPCYSalyaAnXG3ioErb8oJSVek=")
    st.stop()
