
import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import tempfile
import io
from AnalyticsClient import AnalyticsClient
from requests_oauthlib import OAuth2Session

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
df = pd.read_csv(tmpf, names=["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email", "Project Name", "Summary", "Industry", "TRL (1-9)", "Questions We Need Answered", "1", "2", "3", "4", "5", "6"], header=0, dtype={"Project ID":object})

for col in df.columns.values[-6:]:
    df[col] = round(df[col].str.rstrip('%').astype('float') / 100, 2)


# buffer = io.StringIO()
# df.info(buf=buffer)
# s = buffer.getvalue()
# st.text(s)

# dfs = df["Project ]

st.write(df.info())
st.dataframe(df)

newCols = ["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email", "Project Name",
           "Summary", "Industry", "1", "2", "3", "4", "5", "6", "Questions We Need Answered"]

styleCols = newCols[8:-1]

# df = df[keepCols]
df.columns = newCols

hundList = [(df[col][df[col] == 100].index[i], df.columns.get_loc(col)) for col in styleCols for i in range(len(df[col][df[col] == 100].index))]
notZList = [(df[col][df[col] > 0].index[i], df.columns.get_loc(col)) for col in styleCols for i in range(len(df[col][df[col] > 0].index))]

df["Questions We Need Answered"] = df["Questions We Need Answered"].str.replace("?", "?<br>", regex=False)



def button_func(row):
    val = f'''<button onclick="window.open('https://smehub.zohocreatorportal.com/#Form:Interest_Form?Project_ID={str(row['Project ID'])}&Project_Name={row['Project Name']}&Project_Owner={row['Project Owner']}&Project_Owner_Email={row["Project Owner Email"]}&AM_Name={row["SVS acct. mgr."]}&AM_Email={row["AM Email"]}')">Help Us <span class="glyphicon glyphicon-new-window"></span></button>'''
    return val

df["Interested? Click Below"] = df.apply(button_func, axis=1)

df.loc[:, styleCols] = ''
df = df.fillna('')


def highlight_cells(x, hundList, notZList):
    df = x.copy()
    # set default color
    df.iloc[:, :] = ''
    # df.iloc[:,:] = 'background-color: green'

    # set particular cell colors

    for val in notZList:
        df.iloc[val] = 'background-color: gold'
    for val in hundList:
        df.iloc[val] = 'background-color: green'

    return df


t = df.style.apply(highlight_cells, axis=None, hundList=hundList, notZList=notZList)
t.hide(axis='index')
t.hide(["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email"], axis=1)

t.set_properties(
    **{'font-family': 'arial', 'padding': '1rem', 'border-radius': 'collapse'}
)
t.set_table_styles(
    [
        {
            'selector': '',
            'props': [('width', '100%'), ('border-radius', '1em'), ('font-size', '10pt'),
                      ('border-collapse', 'collapse'), ('position', 'relative'),
                      ('box-shadow', ' 0 0 20px rgba(0, 0, 0, 0.15)'), ('margin', '25px 10px'), ('overflow', 'clip')]
        },
        {
            'selector': 'th',
            'props': [
                ('font-size', '12pt'),
                ('color', 'white'),
                ('font-family', 'arial'),
                ('position', 'sticky'),
                ('top', '0'),
                ('padding', '12px'),
                ('background', 'linear-gradient(90deg, rgba(218,120,34,1) 0%, rgba(163,31,36,1) 100%);'),
                ('background-attachment', 'fixed'),
                ('z-index', '900')

            ]
        },
        {
            'selector': 'th.pointer',
            'props': [
                ('cursor', 'pointer')]
        },
        {
            'selector': 'tr',
            'props': [('border-bottom', 'thin solid lightgray')]
        },
        {
            'selector': 'tr:nth-child(odd)',
            'props': [('background-color', 'white')]
        },
        {
            'selector': 'tr:nth-child(even)',
            'props': [('background-color', 'f3f3f3')]
        },
        {
            'selector': 'tr:hover',
            'props': [('background-color', 'lightgray')]
        },
        {
            'selector': 'button',
            'props': [('background-color', '#002060'),
                      ('color', 'white'),
                      ('border-radius', '.5em'),
                      ('border', 'none'),
                      ('padding', '5px'),
                      ]
        },
        {
            'selector': 'button:hover',
            'props': [('background-color', 'lightblue')

                      ]
        }

    ], overwrite=False
)

tmph = tempfile.NamedTemporaryFile(delete=False)

HTML(t.to_html(tmph.name, escape=False, index=False))

st.markdown(tmph, unsafe_allow_html=True)