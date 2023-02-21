import streamlit as st
import requests
st.write(st.secrets)

code = st.secrets["code"]
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = "https://jacobsummit-sme-hub-streamlit-app-z2fgzo.streamlit.app/"


response = requests.get(f"https://accounts.zoho.com/oauth/v2/token?code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code")

st.write(response.status_code)