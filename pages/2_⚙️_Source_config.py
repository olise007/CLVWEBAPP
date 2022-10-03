import streamlit as st 
import json
from model.clvcalculator import clvcalculator

st.set_page_config(
    page_title="Source Config- Customer Life Time Value APP",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.header("MySQL Source Configurations Page")

with open('./config/mysql_source.json', 'r') as sourceinfo:
    mysql_config = json.load(sourceinfo)


with st.form(key="source_config"):
    st.write("MySql Database Connection Settings")
    mysql_host = st.text_input(label="Database Host", value=mysql_config['host'])
    mysql_port = st.text_input(label="Database Port", value=mysql_config['port'])
    mysql_db_name = st.text_input(label="Database Name", value=mysql_config['database'])
    mysql_db_user = st.text_input(label="Database Username", value=mysql_config['user'])
    mysql_db_password = st.text_input(label="Database Password", value=mysql_config['password'])
    mysql_db_table = st.text_input(label="Source Data Table Name", value=mysql_config['table'])

    save_config = st.form_submit_button(label="Save Settings")
            
if save_config:
    try:
        mysql_vars = {
            "host":mysql_host,
            "port":mysql_port,
            "database":mysql_db_name,
            "user":mysql_db_user,
            "password":mysql_db_password,
            "table":mysql_db_table
        }

        mysqljson = json.dumps(mysql_vars, indent=4)
        with open('./config/mysql_source.json', 'w') as sourceinfo:
            sourceinfo.write(mysqljson)
        sourceinfo.close()

        st.success("Configuration Settings have been saved..")

        clvcalc = clvcalculator()       
        check_mysql_conn = clvcalc.check_mysql_trans()

        if check_mysql_conn:
            st.success("MySQL Source Connection was successfully validated")
        else:
            st.error("Could Not Validate MySQL connection parameters")

    except:
        st.error("Could not save Configurations..")