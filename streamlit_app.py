
import streamlit as st
import json
import requests
import importlib
# zaconnector = importlib.import_module("zoho_analytics_connector")
# from AnalyticsClient import AnalyticsClient
from requests_oauthlib import OAuth2Session

code = st.secrets["code"]
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = "https://jacobsummit-sme-hub-streamlit-app-z2fgzo.streamlit.app/"
refresh_token = st.secrets["refresh-token"]

token_refresh = requests.post(f"https://accounts.zoho.com/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=refresh_token")
# response = requests.post(f"https://accounts.zoho.com/oauth/v2/token?code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code")
access_token = token_refresh.json()["access_token"]

# st.write(access_token)
dataTest = requests.post(f"https://analyticsapi.zoho.com/restapi/v2/workspaces/2388301000001369040/views/2388301000003333001/data")
# dataTest = requests.post(f"https://analyticsapi.zoho.com/api/spencer@summitventurestudio.com/'Zoho CRM + Projects Analytics'/'Pipeline Report for Work with Us Page Darla SVS'")
st.write(dataTest.status_code)


