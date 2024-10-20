import streamlit as st
import pandas as pd

import datetime
from datetime import datetime, timedelta, date


# --- FUNCTIONS ---
def tooltip_html(row,df):
    
    i = row

    id_bunker=df_bunkers_features['id_bunker'].iloc[i]
    status=df_bunkers_features['Last survey'].iloc[i]
    var_1=df_bunkers_features['var_1'].iloc[i]
    var_2=df_bunkers_features['var_2'].iloc[i]
    var_3=df_bunkers_features['var_3'].iloc[i]
    var_4=df_bunkers_features['var_4'].iloc[i]

       

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
