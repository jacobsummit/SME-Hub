from __future__ import with_statement
from ReportClient import ReportClient
import sys

import streamlit as st
import json
import requests
import oauthlib


code = st.secrets["code"]
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = "https://jacobsummit-sme-hub-streamlit-app-z2fgzo.streamlit.app/"
refresh_token = st.secrets["refresh-token"]

token_refresh = requests.post(f"https://accounts.zoho.com/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=refresh_token")
# response = requests.post(f"https://accounts.zoho.com/oauth/v2/token?code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code")
access_token = token_refresh.json()["access_token"]

# st.write(access_token)
dataTest = requests.get(f"https://analyticsapi.zoho.com/api/jacob@summitventurestudio.com")
# dataTest = requests.post(f"https://analyticsapi.zoho.com/api/spencer@summitventurestudio.com/'Zoho CRM + Projects Analytics'/'Pipeline Report for Work with Us Page Darla SVS'")
# st.write(requests.get('https://github.com').status_code)


# client = oauthlib.oauth1.Client(client_id, client_secret=client_secret)



# class Sample:

#     LOGINEMAILID="Email Address"
#     CLIENTID="************"
#     CLIENTSECRET="************"
#     REFRESHTOKEN="************"
#     DATABASENAME="Employee"
#     TABLENAME="Employee"
#     rc = None
#     rc = ReportClient(REFRESHTOKEN, CLIENTID, CLIENTSECRET)

#     def exportdata(self,rc):
#         uri = rc.getURI(self.LOGINEMAILID,self.DATABASENAME,self.TABLENAME)
#         fileobj = open("/home/sample.csv","rw+")
#         rc.exportData(uri,"CSV",fileobj)
#         fileobj.close()

# obj = Sample()
# obj.exportdata(obj.rc)