import smtplib
import yagmail
import streamlit as st
import streamlit.components.v1 as components

import pandas as pd
import numpy as np
import requests
import tempfile
import re
from AnalyticsClient import AnalyticsClient
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode, ColumnsAutoSizeMode
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
im = Image.open("svsfavicon.png")
head = Image.open("image1.png")

st.set_page_config(layout='wide', page_icon=im, page_title="SME Hub", initial_sidebar_state="collapsed")

@st.cache_data(ttl=3600)
def access_api():
    redirect_uri = "https://jacobsummit-sme-hub-streamlit-app-z2fgzo.streamlit.app/"
    token_refresh = requests.post(f"https://accounts.zoho.com/oauth/v2/token?refresh_token={st.secrets['refresh-token']}&client_id={st.secrets['client_id']}&client_secret={st.secrets['client_secret']}&redirect_uri={redirect_uri}&grant_type=refresh_token")
    # access_token = token_refresh.json()["access_token"]
    ac = AnalyticsClient(st.secrets['client_id'], st.secrets['client_secret'], st.secrets['refresh-token'])
    return ac

@st.cache_data
def load_data():
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    bulk = access_api().get_bulk_instance(st.secrets["org_id"], "2388301000001369040")
    result = bulk.export_data("2388301000003333001", "csv", tmpf.name)
    df = pd.read_csv(tmpf, dtype={"Project ID":str})
    df["Priority Level"] = df["Priority Level"].replace(" ", np.nan)
    for col in df.columns[10:].tolist():
        df[col] = df[col].str.replace("%", "")
        df[col] = df[col].astype("float")
        df[col] = df[col].fillna(0)

    keepCols = ["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email","Priority Level", "Project Name",
                "Summary", "Industry", "1. Eval & Screening", "2. Technical Analysis", "3. Market Analysis",
                "4. Technical Validation", "5. Market Validation", "6. Final Review and Decision",
                "Critical Questions"]
    newCols = ["Project ID", "Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email","Priority Level", "Project Name",
            "Summary", "Industry", "1", "2", "3", "4", "5", "6", "Critical Questions"]

    df = df[keepCols]
    df.columns = newCols 
    cols = df.columns.tolist()
    cols = cols[6:]+cols[:6]
    df = df[cols]
    df = df[(df['Project Name'].str.len()>1) & (df['Summary'].str.len()>1)& (df['Industry'].str.len()>1)& (df['Critical Questions'].str.len()>1)]
    df = df.sort_values("Priority Level", ascending=True,na_position="last")
    # df["Interest"] = False
    return df

def validEmail(email):
    eReg = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(eReg, email): return True
    else: return False

def anaEmail(anav, fullname, useremail):
    fname = anav.iloc[0,12].split(" ")[0]
    contents = f"""Hello {fname}, <br>someone has expressed interest in one or more of your projects! Their information is below.  
    Please contact them as soon as possible!<br><br>"""
    contents += f"Name of the person espressing interest: {fullname}<br>Email of the person expressing interest: {useremail}<br> Below are the project names and URLs they have expressed interest in:<br><br>"
    for tech in range(len(anav)):
        contents += f"<p><b>Project Name:</b> {anav.iloc[tech, 7]}</p>"
        contents += f"<p><b>Project url:</b> <a href='https://projects.zoho.com/portal/summitventurestudiodotcom#project/{anav.iloc[tech, 11]}'>click here</a></p>"
        contents += f"<p><b>Your questions about the tech:</b><br> {anav.iloc[tech, 10].replace('?', '?<br>')}</p><br>"
    return contents

def amEmail(amv, fullname, useremail):
    fname = amv.iloc[0,14].split(" ")[0]
    contents = f"""Hello {fname}, <br>Someone has expressed interest in one or more projects that you are the account manager for! Their information is below.  
    The analyst assigned to each of these projects has been notified, feel free to follow up with them about their efforts!!<br><br>"""
    contents += f"Name of the person espressing interest: {fullname}<br>Email of the person expressing interest: {useremail}<br> Below are the project names and URLs they have expressed interest in:<br><br>"

    for tech in range(len(amv)):
        contents += f"<p><b>Project Name:</b> {amv.iloc[tech, 7]}</p>"
        contents += f"<p><b>Analyst Name:</b> {amv.iloc[tech, 12]}</p>"
        contents += f"<p><b>Project url:</b> <a href='https://projects.zoho.com/portal/summitventurestudiodotcom#project/{amv.iloc[tech, 11]}'>click here</a></p>"
        contents += f"<p><b>Analyst's questions about the tech:</b><br> {amv.iloc[tech, 10].replace('?', '?<br>')}</p><br>"
    return contents


def extEmail(v, fullname):
    fname = fullname.split(" ")[0]
    contents = f"""Hello {fname}, <br>thank you for expressing interest in some of our projects at Summit Venture Studio.  
    The team members for each of these projects should reach out to you soon.<br><br>"""
    for tech in range(len(v)):
        contents += f"<h3>Project Name: {v.iloc[tech, 7]}</h3>"
        contents += f"<p>Project description: {v.iloc[tech, 8]}</p><br>"
    return contents

def emailer(useremail, contents, subject):
    with yagmail.SMTP(st.secrets["sender"], st.secrets["sender-pass"]) as yag:
        yag.send(to=useremail, contents=contents, subject=subject)
        yagmail.SMTP.close(yag)






def updateDf(rowid, val):

    df.loc[df["Project ID"] == rowid, ["Interest"]] = val

# def get_state(rowid):
#     if rowid in [x["id"] for x in st.session_state.projs]:
#         st.session_state.projs[]

def proj_changed(rowid, val):
    if rowid not in st.session_state.projs:
        st.session_state.projs.append(rowid)
    else:
        st.session_state.projs.remove(rowid)
    name = df[df["Project ID"] == rowid]["Project Name"].values[0]
    components.html(f"""
    <script>
    Array.from(window.parent.document.querySelectorAll('div[data-testid="stExpander"] div[role="button"] p')).find(el => el.innerText === '{name}').classList.toggle('olabel');
    </script>
    """)
    

if "projs" not in st.session_state:
    st.session_state.projs = []

df = load_data()
df["Total Progress"] = round(df["1"]/6+df["2"]/6+df["3"]/6+df["4"]/6+df["5"]/6+df["6"]/6).astype(int)
# st.dataframe(df)
# st.sidebar.write(df.columns)


with st.expander("Filter", True):
    indFil = st.multiselect("Select All Industries you are Interested in", df["Industry"].unique(),default=df["Industry"].unique())
with st.expander("Sort", True):
    sortCol1, sortCol2,sortCol3 = st.columns((1,1,2))
    with sortCol1:
        sortCol = st.selectbox("Sort by", ["Priority Level","Project Name","Industry","Total Progress"])
    with sortCol2:
        st.write()
        sortAsc = st.checkbox("Sort by Ascending",value=True)

df = df.sort_values(sortCol,ascending=sortAsc)
filtDf = df[df["Industry"].isin(indFil)]


st.header("Our Projects:")
for row in filtDf.index:
    with st.expander(f"**{filtDf.loc[row,'Project Name']}**"):   
        st.write(f"**Project Summary:** {filtDf.loc[row,'Summary']}")
        st.write(f"**Our Questions:**\n\n {filtDf.loc[row,'Critical Questions']}".replace('?','?\n'))
        st.write(f"**Priority Level:** {filtDf.loc[row,'Priority Level']}")
        st.write(f"**Total Progress:** {filtDf.loc[row,'Total Progress']}%")
        # st.write(filtDf.loc[row,'Project ID'])
        st.checkbox("Check box if Interested", value=filtDf.loc[row,"Project ID"] in st.session_state.projs, key=filtDf.loc[row,"Project ID"], on_change=proj_changed, args=(filtDf.loc[row,"Project ID"], True))
        # updateDict(df.loc[row,"Project ID"], st.checkbox("Check if Interested", key=df.loc[row,"Project ID"]))

# with st.expander("See Your interests here"):
#     st.write("test")
#     for i in df.index:
#         intCol1, intCol2 = st.columns((1,1))
#         with intCol1:
#             # st.write(i.iloc[0,-1])
#             pass
#         with intCol2:
#             st.write()
#             # st.button("Click to Remove", key="x"+i, on_click=updateDict(i, False))

# st.session_state.projs
# st.write()

col1, col2 = st.columns((1,1))
with col1:
    # st.write('<- See sidebar for table usage (sorting, filtering, more information)')
    # st.write("Check boxes for projects you are interested in, then enter your information below. A team member will reach out to you in regards to these projects.")
    with st.expander("Enter your Information",True):
        with st.form("email_form"):
            fullName = st.text_input(label = "Full Name", placeholder="Enter Full Name")
            userEmail = st.text_input(label = "Email", placeholder="Enter Email")
            email_submit = st.form_submit_button("Submit")

st.markdown("""<style>
.myclass .olabel {
    color: orange;
}

</style>""", unsafe_allow_html=True)


jsTest = ""

# for name in filtDf["Project Name"]:
#     cssColor = 'myclass olabel'
#     jsTest += f"""Array.from(window.parent.document.querySelectorAll('div[data-testid="stExpander"] div[role="button"] p')).find(el => el.innerText === '{name}').classList.toggle('{cssColor}');"""
for name in [df[df["Project ID"] == x]["Project Name"].values[0] for x in df["Project ID"] if x in st.session_state.projs]:
    jsTest += f"""Array.from(window.parent.document.querySelectorAll('div[data-testid="stExpander"] div[role="button"] p')).find(el => el.innerText === '{name}').classList.toggle('olabel');"""

components.html(f"""
<script>
{jsTest}
</script>
""")
st.write(jsTest)

#  custom_css = {
#     ".ag-header-cell-text":{"color":"#fff","font-size":"15px !important"},
#     ".ag-header":{"background":"linear-gradient(90deg, rgba(218,120,34,1) 0%, rgba(163,31,36,1) 100%);"},
#     ".ag-header-row":{"height":"60px"},
#     ".ag-cell-wrap-text":{"word-break":"break-word"},
#     ".ag-root-wrapper":{"border-radius":"1em"},
#     ".stAgGrid":{"box-shadow":  "5px 5px 5px grey"},
# }

# cellstyle_jscode = JsCode("""
# function(params){
#     if (params.value == '100') {
#         return {
#             'color': 'green', 
#             'backgroundColor': 'green',
#             'display':'block',
#         }
#     }
#     else if (params.value > '0') {
#         return{
#             'color': 'gold',
#             'backgroundColor': 'gold',
#         }
#     }
#     if (params.value == '0') {
#         return{
#             'color': 'white',
#             'backgroundColor': 'green', 
#             'display':'none'
#         }
#     }
# }
# """)




# with col2:
#     st.markdown("""<style>
    
# .green-square {
# position: relative;
# display: inline-block;
# width: 20px;
# height: 20px;
# background-color: green;

# float: right;
# }
# .yellow-square {
# background-color: gold;
# }</style><br><br><br>
# <div class="green-square"></div>
# <span style="float:right; position: relative; right:10px;">Complete: </span>
# <br/>
# <div class="green-square yellow-square"></div>
# <span style="float:right; position: relative; right:10px">In Process: </span>""",unsafe_allow_html=True)

# gb = GridOptionsBuilder.from_dataframe(df)
# # gb.configure_side_bar(filters_panel=True, columns_panel=False, defaultToolPanel="filters")
# gb.configure_default_column(sizeColumnsToFit=False, enablePivot=False, enableValue=False, enableRowGroup=True, suppressColumnsToolPanel=True,menuTabs=['filterMenuTab'],enableBrowserTooltips=False,tooltip_show_delay=0)
# gb.configure_selection(selection_mode="multiple", use_checkbox=True)

# gb.configure_column("Project Name", headerTooltip="The name of the technology", width=150)
# gb.configure_column("Summary", headerTooltip="A brief statement including details about the technology")
# gb.configure_column("Industry", headerTooltip="The industry that the technology belongs to", width=130)
# gb.configure_column("1", headerTooltip="Initial Analysis", tooltipShowDelay=0)
# gb.configure_column("2", headerTooltip="Technical Analysis")
# gb.configure_column("3", headerTooltip="Market Analysis")
# gb.configure_column("4", headerTooltip="Technical Validation")
# gb.configure_column("5", headerTooltip="Market Validation")
# gb.configure_column("6", headerTooltip="Final Review and Decision")
# gb.configure_column("Critical Questions", headerTooltip="A list of a few questions we have about the project")

# gb.configure_columns(["Summary","Project Name","Critical Questions","Industry"],wrapText = True,autoHeight = True)
# gb.configure_columns(["1", "2", "3", "4", "5", "6"],maxWidth=48, minWidth=48,resizable=False, cellStyle=cellstyle_jscode)
# gb.configure_columns(["Project ID","Project Owner","Project Owner Email", "SVS acct. mgr.", "AM Email","Priority Level"],hide=True)

# go = gb.build()

# ag = AgGrid(df, height=1000, gridOptions=go, theme="streamlit", enableBrowserTooltips=False,tooltip_show_delay=500000,fit_columns_on_grid_load=True,allow_unsafe_jscode=True,custom_css=custom_css,use_checkbox=True,update_mode=GridUpdateMode.MODEL_CHANGED, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS, enable_quicksearch=True)
# v = pd.DataFrame(ag['selected_rows'])


# if email_submit:
#     if fullName and validEmail(userEmail) and not v.empty:
#         # emailer(userEmail, extEmail(v, fullName), subject)
#         # st.markdown(extEmail(v, fullName), unsafe_allow_html=True)
#         anaList = v["Project Owner Email"].unique().tolist()
#         amList = v["AM Email"].unique().tolist()
#         for ana in anaList:
#             pass
#             # emailer("jacobtminson@gmail.com", anaEmail(v[v["Project Owner Email"]==ana]), "You have a message from SME HUB!")
#             # st.markdown(anaEmail(v[v["Project Owner Email"]==ana], fullName, userEmail), unsafe_allow_html=True)
#         for am in amList:
#             pass
#             # emailer(userEmail, amEmail(v[v["AM Email"]==am], fullName, userEmail), "Message from SME Hub!")
#             # st.markdown(amEmail(v[v["AM Email"]==am], fullName, userEmail), unsafe_allow_html=True)
#         with col2:
#             st.success("Email Successfully Sent!", icon="🎉")
#     with col2:
#         if v.empty: st.error("Please check at least one box.", icon="❗")
#         if not fullName: st.error("Please Enter your Name", icon="❗")
#         if not validEmail(userEmail): st.error("Please Enter a Valid Email Address", icon="❗")

            

# with st.sidebar:
#     st.write("""**Columns 1-6 represent the stages in our analysis process.**
#     \n**Column Definitions:** Hover on the table headers for at least three seconds to get more information.
#     \n**Sorting:** Click on a header to sort alphanumerically
#     \n**Filtering:** Click the three-bar menu for filtering. (If on mobile, press and hold)""")
#     ind_im = Image.open("menu_show.png")
#     st.image(ind_im)

# st.write(f'Number of Selected Projects: {len(v)}')

# for i in range(len(v)):
#     st.write(f"#### {v.iloc[i,7]}")
#     st.write(v.iloc[i,8].replace(".",".\n"))
    