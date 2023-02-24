
import streamlit as st
import pandas as pd
import numpy as np
import bs4
import re
import os
from datetime import datetime
import json
import requests
import tempfile
import io
from st_pages import Page, show_pages, add_page_title
from IPython.display import HTML
from AnalyticsClient import AnalyticsClient
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout='wide', page_icon="mountain", page_title="SME Hub")


def button_func(row):
    val = f'''<button onclick="window.open('https://smehub.zohocreatorportal.com/#Form:Interest_Form?Project_ID={str(row['Project ID'])}&Project_Name={row['Project Name']}&Project_Owner={row['Project Owner']}&Project_Owner_Email={row["Project Owner Email"]}&AM_Name={row["SVS acct. mgr."]}&AM_Email={row["AM Email"]}')">Help Us <span class="glyphicon glyphicon-new-window"></span></button>'''
    return val



code = st.secrets["code"]
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
org_id = st.secrets["org_id"]
workspace_id = "2388301000001369040"
view_id = "2388301000003333001"
redirect_uri = "https://jacobsummit-sme-hub-streamlit-app-z2fgzo.streamlit.app/"
refresh_token = st.secrets["refresh-token"]

token_refresh = requests.post(f"https://accounts.zoho.com/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=refresh_token")
# response = requests.post(f"https://accounts.zoho.com/oauth/v2/token?code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code")
access_token = token_refresh.json()["access_token"]


ac = AnalyticsClient(client_id, client_secret, refresh_token)
# sqlresult = ac.initate_bulk_export_using_sql()


@st.cache_data
def load_data():
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    bulk = ac.get_bulk_instance(org_id, workspace_id)
    result = bulk.export_data(view_id, "csv", tmpf.name)
    df = pd.read_csv(tmpf)
    return df
# df = df.fillna(0)

df = load_data()


if st.button("test button"):
    st.session_state['interest'] = df.iloc[1,:]
    switch_page("test")

for col in df.columns[9:].tolist():
    df[col] = df[col].str.replace("%", "")
    df[col] = df[col].astype("float")
    df[col] = df[col].fillna(0)

keepCols = ["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email", "Project Name",
            "Summary", "Industry", "1. Eval & Screening", "2. Technical Analysis", "3. Market Analysis",
            "4. Technical Validation", "5. Market Validation", "6. Final Review and Decision",
            "Questions We Need Answered"]
newCols = ["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email", "Project Name",
           "Summary", "Industry", "1", "2", "3", "4", "5", "6", "Questions We Need Answered"]

# styleCols = newCols[8:-1]

df = df[keepCols]
df.columns = newCols 

# hundList = [(df[col][df[col] == 100].index[i], df.columns.get_loc(col)) for col in styleCols for i in range(len(df[col][df[col] == 100].index))]
# notZList = [(df[col][df[col] > 0].index[i], df.columns.get_loc(col)) for col in styleCols for i in range(len(df[col][df[col] > 0].index))]

df["Questions We Need Answered"] = df["Questions We Need Answered"].str.replace("?", "?\n", regex=True)
# df["Interested? Click Below"] = df.apply(button_func, axis=1)



industries = list(df['Industry'].unique())


industry_choice = st.sidebar.multiselect('Choose Industries:',industries, default=industries)


custom_css = {
    ".ag-header-cell-text":{"color":"#fff","font-size":"15px !important"},
    ".ag-header":{"background":"linear-gradient(90deg, rgba(218,120,34,1) 0%, rgba(163,31,36,1) 100%);"},
    ".ag-cell-wrap-text":{"word-break":"break-word"},
    ".ag-root-wrapper":{"border-radius":"1em"},
    ".ag-grid-container":{"box-shadow":  "0 0 20px rgba(0, 0, 0, 0.15)"}
}



cellstyle_jscode = JsCode("""
function(params){
    if (params.value == '100') {
        return {
            'color': 'green', 
            'backgroundColor': 'green',
            'display':'block',
        }
    }
    else if (params.value > '0') {
        return{
            'color': 'gold',
            'backgroundColor': 'gold',
        }
    }
    if (params.value == '0') {
        return{
            'color': 'white',
            'backgroundColor': 'green',
            'display':'none'
        }
    }
}
""")

df = df[df['Industry'].isin(industry_choice)]

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(sizeColumnsToFit=True)
gb.configure_columns(["Summary","Project Name","Questions We Need Answered"],wrapText = True,autoHeight = True, flex=1)
gb.configure_columns(["1", "2", "3", "4", "5", "6"],maxWidth=60, resizable=False, cellStyle=cellstyle_jscode,wrapText = True)
gb.configure_columns(["Project ID","Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email"],hide=True)
go = gb.build()


AgGrid(df, height=1000, gridOptions=go, theme="streamlit",allow_unsafe_jscode=True, custom_css=custom_css)
# st.dataframe(df)