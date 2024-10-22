import streamlit as st
import pandas as pd

import datetime
from datetime import datetime, timedelta, date

import folium
from folium.plugins import Draw, Fullscreen, LocateControl, GroupedLayerControl
from streamlit_folium import st_folium

from streamlit_gsheets import GSheetsConnection

from credentials import *



conn = st.connection("gsheets", type=GSheetsConnection)

def tooltip_html(row,df):
    
    i = row

    surrounding=df['surrounding'].iloc[i]
    type_bunker=df['type_bunker'].iloc[i]
    number_chambers=df['number_chambers'].iloc[i]
    opmerking=df['opmerking'].iloc[i]
    

    left_col_color = "#19a7bd"
    right_col_color = "#f2f0d3"
    
    html = """<!DOCTYPE html>
    <html>
    <table style="height: 126px; width: 300;">
    <tbody>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Surrounding</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(surrounding) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Type of bunker</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(type_bunker) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Number of chambers</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(number_chambers) + """
    </tr>
    <tr>
    <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;">Opmerking</span></td>
    <td style="width: 150px;background-color: """+ right_col_color +""";">{}</td>""".format(opmerking) + """
    </tr>
    </tbody>
    </table>
    </html>
    """
    return html

def tab_popup(df_bunkers_observations):
    table_dictionary = {}
    for id in df_bunkers_observations.id_bunker.unique():
        try:
            df_table = df_bunkers_observations[df_bunkers_observations.id_bunker==id]
            df_table['date'] = pd.to_datetime(df_table['date'],format="%Y-%m-%d")
            df_table.set_index("date",inplace=True)
            df_table.sort_index(inplace=True)
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

def insert_bunker_fearures(last_survey,id_bunker,lat,lng,surrounding,type_bunker,number_chambers,opmerking,df):
    
    data = [{'Last survey':last_survey,"id_bunker":id_bunker, "lat":lat,"lng":lng,"surrounding":surrounding,"type_bunker":type_bunker,
             "number_chambers":number_chambers,"opmerking":opmerking,
             }]
    df_new = pd.DataFrame(data)
    df_updated = pd.concat([df,df_new],ignore_index=True)
    
    return conn.update(worksheet="bunkers_features",data=df_updated)      
  
def map():
    
    m = folium.Map()

    Draw(draw_options={'circle': False,'rectangle': False,'circlemarker': False, 'polyline': False, 'polygon': False},
         position="topright").add_to(m)
    Fullscreen(position="topright").add_to(m)
    LocateControl(auto_start=True,position="topright").add_to(m)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',attr='Google_map',overlay=False,show=False,name="Satellite").add_to(m)
    

    folium.LayerControl().add_to(m)
    output = st_folium(m, returned_objects=["all_drawings"],width=OUTPUT_width, height=OUTPUT_height)
    output["features"] = output.pop("all_drawings")
    
    return  output

        
@st.dialog(" ")
def input_data(output,df):   

    surrounding = st.selectbox("Type of surrounding", SURROUNDING_OPTIONS)
    type_bunker = st.selectbox("Type of bunker", TYPE_BUNKER_OPTIONS)
    number_chambers = st.number_input("Number of chambers", min_value=1)
    opmerking = st.text_input("", placeholder="Vul hier een opmerking in ...")
    last_survey = 'No Data Yet!'
    
    st.divider()
        
    submitted = st.button("**Gegevens opslaan**",use_container_width=True)
    
    if submitted:           

        coordinates = output["features"][0]["geometry"]["coordinates"] 
                       
        lng = coordinates[0]
        lat = coordinates[1]
        
        id_bunker = str(lng)+str(lat)

        if len(output["features"]) > 1:
            st.error("U kunt niet meer dan één waarneming tegelijk uploaden!")
            st.stop()

        else:
            insert_bunker_fearures(last_survey,id_bunker,lat,lng,surrounding,type_bunker,number_chambers,opmerking,df)

            st.success('Gegevens opgeslagen!', icon="✅")       
  
        st.switch_page("🗺️_Home.py")

@st.dialog(" ")
def input_insert_bats(output,df):
    waarnemer = st.session_state.login['name']
    date = st.date_input("Datum")
    temperature = st.number_input("Temperature", min_value=1)
    humidity = st.number_input("humidity", min_value=1)
    sp = st.multiselect("Chose which species was there", BAT_NAMES)
    
    
    if sp:
        dict_species = {}
        for species in sp:
            dict_species[species] = st.number_input(species, min_value=1,key=species)
        data_dict = {'date':date,"waarnemer":waarnemer,"temperature":temperature,"humidity":humidity} | dict_species
        
    else:
        data_dict = {'date':date,"waarnemer":waarnemer,"temperature":temperature,"humidity":humidity}
        
    opmerking = st.text_input("", placeholder="Vul hier een opmerking in ...")    
    
    st.divider()
        
    submitted = st.button("**Gegevens opslaan**",use_container_width=True)
    
    if submitted:           

        coordinates = output["last_object_clicked"]
                       
        lng = coordinates["lng"]
        lat = coordinates['lat']
        
        id_bunker = str(lng)+str(lat)

        data = [{"id_bunker":id_bunker} | data_dict | {'opmerking':opmerking}]
        df_new = pd.DataFrame(data)
        df_updated = pd.concat([df,df_new],ignore_index=True)
        conn.update(worksheet="bunkers_observations",data=df_updated)

        st.success('Gegevens opgeslagen!', icon="✅")       
  
        st.switch_page("🗺️_Home.py")

@st.dialog(" ")
def popup_table(id_bunker,output,df_bunkers_features,table_dictionary): 
    df_popup = df_bunkers_features[df_bunkers_features['id_bunker']==id_bunker].reset_index(drop=True)
    st.write(f'Number of chambers: {df_popup['number_chambers'].loc[0]}')
    st.write(f'Surrounding: {df_popup['surrounding'].loc[0]}')
    st.write(f'Type of bunker: {df_popup['type_bunker'].loc[0]}')
    st.write(f'{df_popup['opmerking'].loc[0]}')
    try:
        table_dictionary[id_bunker].iloc[:,4:] = table_dictionary[id_bunker].iloc[:,4:].replace({0:'-'})
        st.dataframe(table_dictionary[id_bunker])
    except:
        st.write('No Data')
    
