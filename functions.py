import streamlit as st
import pandas as pd

import datetime
from datetime import datetime, timedelta, date

import folium
from folium.plugins import Draw, Fullscreen, LocateControl, GroupedLayerControl
from streamlit_folium import st_folium

from credentials import *

def tooltip_html(row,df):
    
    i = row

    id_bunker=df['id_bunker'].iloc[i]
    status=df['Last survey'].iloc[i]
    var_1=df['var_1'].iloc[i]
    var_2=df['var_2'].iloc[i]
    var_3=df['var_3'].iloc[i]
    var_4=df['var_4'].iloc[i]

       

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

def tab_popup(df_bunkers_observations):
    table_dictionary = {}
    for id in df_bunkers_observations.id_bunker.unique():
        df_table = df_bunkers_observations[df_bunkers_observations.id_bunker==id]
        df_table['Date'] = pd.to_datetime(df_table['Date'],format="%d-%m-%Y")
        df_table.set_index("Date",inplace=True)
        df_table = df_table.iloc[:,1:]
        df_table.sort_index(inplace=True)
        df_table.dropna(axis=1, how='all',inplace=True)
        df_table.fillna(0, inplace=True)
        table_dictionary[id] = df_table

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

def insert_bunker_fearures(id_bunker,waarnemer,datum,lat,lng,surrounding,type_bunker,number_chambers,temperature,humidity,opmerking,df):
    
    data = [{"id_bunker":id_bunker, "waarnemer":waarnemer,"datum":datum,"lat":lat,"lng":lng,"surrounding":surrounding,"type_bunker":type_bunker,
             "number_chambers":number_chambers,"temperature":temperature,"humidity":humidity,
             "opmerking":opmerking,
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
    

    
    output = st_folium(m, returned_objects=["all_drawings"],width=OUTPUT_width, height=OUTPUT_height)
    output["features"] = output.pop("all_drawings")
    
    return  output

        
@st.dialog(" ")
def input_data(output,df):

    waarnemer = st.session_state.login['name']     
    datum = st.date_input("Datum","today")       
   
    st.divider()

    surrounding = st.selectbox("Functie", SURROUNDING_OPTIONS)
    type_bunker = st.selectbox("Functie", TYPE_BUNKER_OPTIONS)
    number_chambers = st.number_input("Number of chambers", min_value=1)
    temperature = st.number_input("Temperature", min_value=15)
    humidity = st.number_input("Humidity", min_value=1)
    opmerking = st.text_input("", placeholder="Vul hier een opmerking in ...")
    
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
            insert_bunker_fearures(id_bunker,waarnemer,str(datum),lat,lng,surrounding,type_bunker,number_chambers,temperature,humidity,opmerking,df)

            st.success('Gegevens opgeslagen!', icon="✅")       
            st.rerun()
  
        st.switch_page("🗺️_Home.py")
