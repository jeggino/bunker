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


@st.dialog(" ",width="large")
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
            st.dataframe(table_dictionary[id_bunker].iloc[:,1:],column_config={'temperature':"Temperatuur (C°)",
                                                                               'humidity':"Vochtigheid (%)",
                                                                              'opmerking':'Opmerking',
                                                                               'waarnemer':'Waarnemer'})
        elif df_popup['class_hybernate'].loc[0] == 'Vleermuiskast':
            df_survey = table_dictionary[id_bunker].drop(['temperature','humidity'],axis=1)
            st.dataframe(df_survey.iloc[:,1:],column_config={'temperature':"Temperatuur (C°)",
                                                             'humidity':"Vochtigheid (%)",
                                                             'opmerking':'Opmerking',
                                                             'waarnemer':'Waarnemer'})
    except:
        st.write('Geen data')

