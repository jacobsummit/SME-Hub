
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
from IPython.display import HTML
from AnalyticsClient import AnalyticsClient
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


st.set_page_config(layout='wide', page_icon="mountain", page_title="SME Hub")

def completion_color(val):
    if val == 1:
        color = 'green'
    elif val > 0:
        color = 'yellow'
    else: 
        color = 'white'
    
    # color = 'green' if val == 1 elif val > 0 'yellow'
    return f'background-color: {color}'

def text_color(val):
    if val == 1:
        tcolor = 'green'
    elif val > 0:
        tcolor = 'yellow'
    else: 
        tcolor = 'white'
    
    # color = 'green' if val == 1 elif val > 0 'yellow'
    return f'color: {tcolor}'




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

tmpf = tempfile.NamedTemporaryFile(delete=False)

bulk = ac.get_bulk_instance(org_id, workspace_id)
# sqlresult = ac.initate_bulk_export_using_sql()
result = bulk.export_data(view_id, "csv", tmpf.name)
data = pd.read_csv(tmpf, names=["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email", "Project Name", "Summary", "Industry", "TRL (1-9)", "Questions We Need Answered", "1", "2", "3", "4", "5", "6"], header=0, dtype={"Project ID":object})
# df = df.fillna(0)


gb = GridOptionsBuilder.from_dataframe(data)
gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
gb.configure_side_bar() #Add a sidebar
gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
gridOptions = gb.build()

grid_response = AgGrid(
    data,
    gridOptions=gridOptions,
    data_return_mode='AS_INPUT', 
    update_mode='MODEL_CHANGED', 
    fit_columns_on_grid_load=False,
    theme='blue', #Add theme color to the table
    enable_enterprise_modules=True,
    height=350, 
    width='100%',
    reload_data=True
)

data = grid_response['data']
selected = grid_response['selected_rows'] 
df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df




for col in df.columns.values[-6:]:   
    df[col] = round(df[col].str.rstrip('%').astype('float') / 100, 2)
    df[col] = df[col].fillna(0)
    


# buffer = io.StringIO()
# df.info(buf=buffer)
# s = buffer.getvalue()
# st.text(s)


st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
st.dataframe(df.style.applymap(completion_color, subset=["1","2","3","4","5","6"]).applymap(text_color, subset=["1","2","3","4","5","6"]))
