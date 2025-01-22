import streamlit as st
import pandas as pd

import datetime
from datetime import datetime, timedelta, date

import folium
from folium.plugins import Draw, Fullscreen, LocateControl, GroupedLayerControl
from streamlit_folium import st_folium

from supabase import create_client, Client

from credentials import *



supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def tab_popup(df_bunkers_observations):
    table_dictionary = {}
    for id in df_bunkers_observations.id_bunker.unique():
        try:
            df_table = df_bunkers_observations[df_bunkers_observations.id_bunker==id]
            df_table['date'] = pd.to_datetime(df_table['date'],format="%Y-%m-%d").dt.date
            df_table.set_index("date",inplace=True)
            df_table.sort_index(inplace=True)
            df_table['opmerking'] = df_table['opmerking'].fillna(value='-')
            df_table.dropna(axis=1, how='all',inplace=True)
            df_table.fillna(0, inplace=True)
            table_dictionary[id] = df_table
        except:
            continue

    return table_dictionary


def logIn(df_references):
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
        st.rerun()

def insert_bunker_fearures(last_survey,id_bunker,bunker_name,lat,lng,class_hybernate,kraamverblijjkast,surrounding,type_bunker,
                           batbox_shape,number_chambers,number_entrance,opmerking):
    
    data = {'Last survey':last_survey,"id_bunker":id_bunker,'bunker_name':bunker_name, "lat":lat,"lng":lng,"class_hybernate":class_hybernate,
             'kraamverblijjkast':kraamverblijjkast,"surrounding":surrounding,"type_bunker":type_bunker,
             "batbox_shape":batbox_shape,"number_chambers":number_chambers,"number_entrance":number_entrance,"opmerking":opmerking,
             }
    
    return supabase.table("bunkers_features").insert(data).execute()      
  
def map():
    
    m = folium.Map(zoom_start=8,tiles=None)

    Draw(draw_options={'circle': False,'rectangle': False,'circlemarker': False, 'polyline': False, 'polygon': False},
         position="topright").add_to(m)
    Fullscreen(position="topright").add_to(m)
    LocateControl(auto_start=False,position="topright").add_to(m)
    folium.TileLayer('OpenStreetMap',overlay=False,show=True,name="Stratenkaart").add_to(m)
    folium.TileLayer(tiles="Cartodb Positron",overlay=False,show=False,name="Witte contrastkaart").add_to(m)
    folium.TileLayer(tiles='https://api.mapbox.com/styles/v1/jeggino/cm2vtvb2l000w01qz9wet0mv9/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiamVnZ2lubyIsImEiOiJjbHdscmRkZHAxMTl1MmlyeTJpb3Z2eHdzIn0.N9TRN7xxTikk235dVs1YeQ',
                     attr='XXX Mapbox Attribution',overlay=False,show=False,name="Satellietkaart").add_to(m)
    

    folium.LayerControl().add_to(m)
    output = st_folium(m, returned_objects=["all_drawings"],width=OUTPUT_width, height=OUTPUT_height)
    output["features"] = output.pop("all_drawings")
    
    return  output

        




@st.dialog(" ",width="large")
def popup_table(id_bunker,output,df_bunkers_features,table_dictionary): 
    df_popup = df_bunkers_features[df_bunkers_features['id_bunker']==id_bunker].reset_index(drop=True)
    df_popup['opmerking'] = df_popup['opmerking'].fillna(value='Geen opmerking')
    df_popup['bunker_name'] = df_popup['bunker_name'].fillna(value='Geen opmerking')
    
    if df_popup['class_hybernate'].loc[0] == 'Bunker':
        st.title(f':blue[**{df_popup['bunker_name'].loc[0].upper()}**]')
        st.header('Bunkerkenmerken',divider='grey')
        st.write(f'**Aantal kamers:** {int(df_popup['number_chambers'].loc[0])}')
        st.write(f'**Omgeving:** {df_popup['surrounding'].loc[0]}')
        st.write(f'**Soort bunker:** {df_popup['type_bunker'].loc[0]}')
        st.write(f'**Aantal ingangen:** {int(df_popup['number_entrance'].loc[0])}')
        try:
            with st.expander("Klik om foto's te zien", expanded=False, icon="📷"):
                st.image(f'icons/images/{id_bunker}.jpg')
        except:
            pass
    else:
        st.header('Vleermuiskast kenmerken',divider='grey')
        st.write(f'**Vorm:** {df_popup['batbox_shape'].loc[0]}')
        st.write(f'**Kraamverblijjkast:** {df_popup['kraamverblijjkast'].loc[0]}')
        
    st.header('Opmerking',divider='grey')
    st.write(f'{df_popup['opmerking'].loc[0]}')

    try:
    # st.header('Gevonden soorten',divider='grey')

    # if len(table_dictionary[id_bunker].iloc[:,4:-1].columns) ==0:
    #     st.write("Nog geen soort gevonden")
    # else:
    #     table_dictionary[id_bunker]
    #     for species in table_dictionary[id_bunker].iloc[:,6:].columns:
    #         st.write(f'*{species}*')
    #         table_dictionary[id_bunker].iloc[:,6:]
    #         df = table_dictionary[id_bunker].iloc[:,6:]
    #         df 
    #         st.write(f"""
    #         Het maximale aantal individuen werd bereikt :blue-background[**{int(df[species].max())}**], 
    #         gedocumenteerd op datum :blue-background[**{df[df[species]==df[species].max()].index[0]}**].
    #         """)
        
        st.header('Onderzoeken',divider='grey')
    
        table_dictionary[id_bunker].iloc[:,5:] = table_dictionary[id_bunker].iloc[:,5:].astype('int').replace({0:'-'})
        if df_popup['class_hybernate'].loc[0] == 'Bunker':
            table_dictionary[id_bunker]['opmerking'].fillna('-', inplace = True)
            st.dataframe(table_dictionary[id_bunker].iloc[:,1:])
        elif df_popup['class_hybernate'].loc[0] == 'Vleermuiskast':
            df_survey = table_dictionary[id_bunker].drop(['temperature','humidity'],axis=1)
            df_survey['opmerking'].fillna('-', inplace = True)
            st.dataframe(df_survey.iloc[:,1:])
    except:
        st.write('Geen data')

