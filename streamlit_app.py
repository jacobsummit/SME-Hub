
import streamlit as st
import pandas as pd
import requests
import tempfile
# from st_pages import Page, show_pages, add_page_title
from AnalyticsClient import AnalyticsClient
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout='wide', page_icon="mountain", page_title="SME Hub")


@st.cache_data(ttl=3600)
def access_api():
    code = st.secrets["code"]
    client_id = st.secrets["client_id"]
    client_secret = st.secrets["client_secret"]
    redirect_uri = "https://jacobsummit-sme-hub-streamlit-app-z2fgzo.streamlit.app/"
    refresh_token = st.secrets["refresh-token"]
    token_refresh = requests.post(f"https://accounts.zoho.com/oauth/v2/token?refresh_token={refresh_token}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=refresh_token")
    
    access_token = token_refresh.json()["access_token"]
    ac = AnalyticsClient(client_id, client_secret, refresh_token)
    return ac

@st.cache_data
def load_data():
    workspace_id = "2388301000001369040"
    view_id = "2388301000003333001"
    tmpf = tempfile.NamedTemporaryFile(delete=False)
    bulk = access_api().get_bulk_instance(st.secrets["org_id"], workspace_id)
    result = bulk.export_data(view_id, "csv", tmpf.name)
    df = pd.read_csv(tmpf)
    return df




with st.sidebar:

    with st.form(key='my_form'):
        fullName = st.text_input(label = "Full Name", placeholder="enter name")

df = load_data()

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

df = df[keepCols]
df.columns = newCols 

cols = df.columns.tolist()
cols = cols[5:]+cols[:5]
df = df[cols]

df["Questions We Need Answered"] = df["Questions We Need Answered"].str.replace("?", "?\n", regex=True)
# df["Interested?"] = ""

mask = df[["Project Name","Summary", "Industry","Questions We Need Answered"]].notnull().all(axis=1)
df = df[mask]


custom_css = {
    ".ag-header-cell-text":{"color":"#fff","font-size":"15px !important"},
    ".ag-header":{"background":"linear-gradient(90deg, rgba(218,120,34,1) 0%, rgba(163,31,36,1) 100%);"},
    ".ag-header-row":{"height":"100px"},
    ".ag-cell-wrap-text":{"word-break":"break-word"},
    ".ag-root-wrapper":{"border-radius":"1em"},
    ".stAgGrid":{"box-shadow":  "5px 5px 5px grey"},
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

gb = GridOptionsBuilder.from_dataframe(df)
gb.sideBar = {'toolPanels': ["filter"]}
gb.configure_default_column(sizeColumnsToFit=True, enablePivot=False, enableValue=True, enableRowGroup=True, suppressColumnsToolPanel=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)

gb.configure_column("Project Name", headerTooltip="The name of the technology")
gb.configure_column("Summary", headerTooltip="A brief statement including details about the technology")
gb.configure_column("Industry", headerTooltip="The industry that the technology belongs to")
gb.configure_column("1", headerTooltip="Initial Analysis")
gb.configure_column("2", headerTooltip="Technical Analysis")
gb.configure_column("3", headerTooltip="Market Analysis")
gb.configure_column("4", headerTooltip="Technical Validation")
gb.configure_column("5", headerTooltip="Market Validation")
gb.configure_column("6", headerTooltip="Final Review and Decision")
gb.configure_column("Questions We Need Answered", headerTooltip="A list of a few questions we have about the project")

gb.configure_columns(["Summary","Project Name","Questions We Need Answered","Industry"],wrapText = True,autoHeight = True, flex=1)
gb.configure_columns(["1", "2", "3", "4", "5", "6"],maxWidth=50, resizable=False, cellStyle=cellstyle_jscode,wrapText = True)
gb.configure_columns(["Project ID","Project Owner", "Project Owner Email", "SVS acct. mgr.", "AM Email"],hide=True)
go = gb.build()

ag = AgGrid(df, height=500, gridOptions=go, theme="streamlit",fit_columns_on_grid_load=False,allow_unsafe_jscode=True,custom_css=custom_css,header_checkbox_selection_filtered_only=True,use_checkbox=True,update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED)


v = ag['selected_rows']
if v:
    v = pd.DataFrame(v)
    if st.button("Send Email to Express Interest"):
        send_email(message)
    st.write('## Selected Projects:')
    
    for i in range(len(v)):
        st.write(f"### {v.iloc[i,7]}")
        st.write(v.iloc[i,8])
    