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
                           batbox_shape,number_chambers,number_entrance,opmerking,df):
    
    data = [{'Last survey':last_survey,"id_bunker":id_bunker,'bunker_name':bunker_name, "lat":lat,"lng":lng,"class_hybernate":class_hybernate,
             'kraamverblijjkast':kraamverblijjkast,"surrounding":surrounding,"type_bunker":type_bunker,
             "batbox_shape":batbox_shape,"number_chambers":number_chambers,"number_entrance":number_entrance,"opmerking":opmerking,
             }]
    df_new = pd.DataFrame(data)
    df_updated = pd.concat([df,df_new],ignore_index=True)
    
    return conn.update(worksheet="bunkers_features",data=df_updated)      
  
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

        
@st.dialog(" ")
def input_data(output,df):   
    
    class_hybernate = st.selectbox("", CLASS_HYBERNATE_OPTIONS) 
    if class_hybernate == 'Bunker':
        bunker_name = st.text_input("Bunker naam", placeholder="Vul hier ...")
        surrounding = st.selectbox("Type omgeving", SURROUNDING_OPTIONS)
        type_bunker = st.selectbox("Soort bunker", TYPE_BUNKER_OPTIONS)
        number_chambers = st.number_input("Aantal kamers", min_value=1)
        number_entrance = st.number_input("Aantal ingangen", min_value=1)
        batbox_shape = None
        kraamverblijjkast = None
    else:
        batbox_shape = st.selectbox("Vorm", BATBOX_SHAPE_OPTIONS)
        kraamverblijjkast = st.selectbox("Kraamverblijjkast", BATBOX_KRAAMVEBLIJFKAST_OPTION)
        surrounding = None
        type_bunker = None
        number_chambers = None
        number_entrance = None
        bunker_name =None
    opmerking = st.text_input("", placeholder="Vul hier een opmerking in ...")
    last_survey = 'Geen data'
    
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
            insert_bunker_fearures(last_survey,id_bunker,bunker_name,lat,lng,class_hybernate,kraamverblijjkast,surrounding,type_bunker,
                                   batbox_shape,number_chambers,number_entrance,opmerking,df)

            st.success('Gegevens opgeslagen!', icon="✅")       
  
        st.switch_page("🗺️_Home.py")

@st.dialog(" ")
def input_insert_bats(output,df,df_features):
    
    coordinates = output["last_object_clicked"]
    lng = coordinates["lng"]
    lat = coordinates['lat']
    id_bunker = str(lng)+str(lat)
    
    waarnemer = st.session_state.login['name']
    date = st.date_input("Datum")

    if df_features[df_features['id_bunker']==id_bunker].reset_index()['class_hybernate'].values[0]=='Bunker':
        if st.checkbox("Geef aan of u temperatuur- en vochtigheidsparameters hebt"):
            temperature = st.number_input("Temperatuur (C°)",value=8)
            humidity = st.number_input("Vochtigheid (%)", min_value=1,max_value=100,value=40)
        else:
            temperature = '-'
            humidity = '-'
    else:
        temperature = '-'
        humidity = '-'
        
    sp = st.multiselect("Kies welke soort er was", BAT_NAMES)
    
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

        data = [{"id_bunker":id_bunker} | data_dict | {'opmerking':opmerking}]
        df_new = pd.DataFrame(data)
        df_updated = pd.concat([df,df_new],ignore_index=True)
        conn.update(worksheet="bunkers_observations",data=df_updated)

        st.success('Gegevens opgeslagen!', icon="✅")       
  
        st.switch_page("🗺️_Home.py")

@st.dialog(" ")
def popup_table(id_bunker,output,df_bunkers_features,table_dictionary): 
    df_popup = df_bunkers_features[df_bunkers_features['id_bunker']==id_bunker].reset_index(drop=True)
    df_popup['opmerking'] = df_popup['opmerking'].fillna(value='Geen opmerking')
    df_popup['bunker_name'] = df_popup['bunker_name'].fillna(value='Geen opmerking')
    
    if df_popup['class_hybernate'].loc[0] == 'Bunker':
        st.title(f':blue[**{df_popup['bunker_name'].loc[0].upper()}**]')
        st.header('Bunkerkenmerken',divider='grey')
        col_1,col_2 = st.columns(2)
        with col_1:
            st.write(f'**Aantal kamers:** {int(df_popup['number_chambers'].loc[0])}')
            st.write(f'**Omgeving:** {df_popup['surrounding'].loc[0]}')
            st.write(f'**Soort bunker:** {df_popup['type_bunker'].loc[0]}')
            st.write(f'**Aantal ingangen:** {int(df_popup['number_entrance'].loc[0])}')
        with col_2:
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
        st.header('Gevonden soorten',divider='grey')
    
        if len(table_dictionary[id_bunker].iloc[:,4:-1].columns) ==0:
            st.write("Nog geen soort gevonden")
        else:
            for species in table_dictionary[id_bunker].iloc[:,4:-1].columns:
                st.write(f'*{species}*')
                df = table_dictionary[id_bunker].iloc[:,4:-1]
                st.write(f"""
                Het maximale aantal individuen werd bereikt :blue-background[**{int(df[species].max())}**], 
                gedocumenteerd op datum :blue-background[**{df[df[species]==df[species].max()].index[0]}**].
                """)
            
        st.header('Onderzoeken',divider='grey')
    
        table_dictionary[id_bunker].iloc[:,4:-1] = table_dictionary[id_bunker].iloc[:,4:-1].astype('int').replace({0:'-'})
        table_dictionary[id_bunker].iloc[:,-1] = table_dictionary[id_bunker].iloc[:,-1].replace({0:'-'})
        if df_popup['class_hybernate'].loc[0] == 'Bunker':
            st.dataframe(table_dictionary[id_bunker].iloc[:,1:])
        elif df_popup['class_hybernate'].loc[0] == 'Vleermuiskast':
            df_survey = table_dictionary[id_bunker].drop(['temperature','humidity'],axis=1)
            st.dataframe(df_survey.iloc[:,1:])
    except:
        st.write('Geen data')

@st.dialog(" ")
def update_item(id):

  df = conn.read(ttl=0,worksheet="bunkers_features")
  df_filter = df[df["id_bunker"]==id].reset_index(drop=True)
  df_drop = df[~df.apply(tuple, axis=1).isin(df_filter.apply(tuple, axis=1))]

  id_bunker = df_filter['id_bunker'][0]
  id_bunker_name = df_filter['bunker_name'][0]
  id_lat = df_filter['lat'][0]
  id_lng = df_filter['lng'][0]
  id_class_hybernate = df_filter['class_hybernate'][0]
  id_surrounding = df_filter['surrounding'][0]
  id_type_bunker = df_filter['type_bunker'][0]
  id_number_chambers = df_filter['number_chambers'][0]
  id_opmerking = df_filter['opmerking'][0]
  id_number_entrance = df_filter['number_entrance'][0]
  id_batbox_shape = df_filter['batbox_shape'][0]
  id_kraamverblijjkast = df_filter['kraamverblijjkast'][0]

  if id_class_hybernate == 'Bunker':
      bunker_name = st.text_input("Bunker naam", value=id_bunker_name,placeholder="Vul hier een naam ...")
      surrounding = st.selectbox("Type omgeving", SURROUNDING_OPTIONS,index=SURROUNDING_OPTIONS.index(id_surrounding))
      type_bunker = st.selectbox("Soort bunker", TYPE_BUNKER_OPTIONS,index=TYPE_BUNKER_OPTIONS.index(id_type_bunker))
      number_chambers = st.number_input("Aantal kamers", min_value=1,value=int(id_number_chambers))
      number_entrance = st.number_input("Aantal ingangen", min_value=1,value=int(id_number_entrance))
      batbox_shape = None
      kraamverblijjkast = None

  else:
      batbox_shape = st.selectbox("Vorm", BATBOX_SHAPE_OPTIONS,index=BATBOX_SHAPE_OPTIONS.index(id_batbox_shape))
      kraamverblijjkast = st.selectbox("Kraamverblijjkast", BATBOX_KRAAMVEBLIJFKAST_OPTION,index=BATBOX_KRAAMVEBLIJFKAST_OPTION.index(id_kraamverblijjkast))
      surrounding = None
      type_bunker = None
      number_chambers = None
      number_entrance = None
      bunker_name = None

  opmerking = st.text_input("", value=id_opmerking,placeholder="Vul hier een opmerking in ...")
  last_survey = 'Geen data'

  if st.button("**Update**",use_container_width=True):
    conn.update(worksheet='bunkers_features',data=df_drop)
    df_old = conn.read(ttl=0,worksheet="bunkers_features")
  
    data = [{'Last survey':last_survey,"id_bunker":id_bunker, 'bunker_name':bunker_name,"lat":id_lat,"lng":id_lng,"class_hybernate":id_class_hybernate,
    'kraamverblijjkast':kraamverblijjkast,"surrounding":surrounding,"type_bunker":type_bunker,
    "batbox_shape":batbox_shape,"number_chambers":number_chambers,"number_entrance":number_entrance,"opmerking":opmerking,
    }]
  
    df_new = pd.DataFrame(data)
    df_updated = pd.concat([df_old,df_new],ignore_index=True)
    conn.update(worksheet='bunkers_features',data=df_updated)

    st.switch_page("🗺️_Home.py")
    
