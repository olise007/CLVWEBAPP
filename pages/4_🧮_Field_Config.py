import streamlit as st 
import json
import numpy as np
import pandas as pd
from model.clvcalculator import clvcalculator

import threading

def background_job():
    clvcalc = clvcalculator()
    check_mysql_conn = clvcalc.check_mysql_trans()
    if check_mysql_conn:
        clvcalc.refresh_model_data()
    print('Hello from the background thread')


st.set_page_config(
    page_title="Source Config- Customer Life Time Value APP",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.header("Table Field Configurations Page")

with open('./config/field_info.json', 'r') as fieldinfo:
            field_info = json.load(fieldinfo)

clvcalc = clvcalculator()
check_mysql_conn = clvcalc.check_mysql_trans()
if check_mysql_conn:
    table_schemas = clvcalc.get_mysql_table_schema()
    tabledf = pd.DataFrame(table_schemas)
    tabledf = tabledf[0].copy()
else:
    tabledf = []

def get_field_index(field_name):
    if type(tabledf) != list:
        index = list(np.where(tabledf == field_info[field_name]))
        index = np.array(index).astype(int)
        index = index.item()
    else:
        index = 0
    return index

with st.form(key="field_config"):
    st.write("Data Field Settings")
    customerid = st.selectbox(label="CustomerID Field", options=tabledf, index=get_field_index('CustomerID'))
    unitprice = st.selectbox(label="UnitPrice Field", options=tabledf, index=get_field_index('UnitPrice'))
    quantity = st.selectbox(label="Quantity Field", options=tabledf, index=get_field_index('Quantity'))
    invoicedate = st.selectbox(label="Invoice Date Field", options=tabledf, index=get_field_index('InvoiceDate'))
    invoiceno = st.selectbox(label="InvoiceNo Field", options=tabledf, index=get_field_index('InvoiceNo'))

    save_config = st.form_submit_button(label="Save Settings")
    pull_new_data = st.form_submit_button(label="Pull Data From Source")
            
if save_config:
    try:

        field_vars = {
            "CustomerID":customerid,
            "UnitPrice":unitprice,
            "Quantity":quantity,
            "InvoiceDate":invoicedate,
            "InvoiceNo":invoiceno
        }

        
        clvcalc = clvcalculator()       
        check_mysql_conn = clvcalc.check_mysql_trans()
        if check_mysql_conn:
            if field_vars['CustomerID']:
                fieldjson = json.dumps(field_vars, indent=4)
                with open('./config/field_info.json', 'w') as fieldinfo:
                    fieldinfo.write(fieldjson)
                fieldinfo.close()
            st.success("Configuration Settings have been saved..")
        else:
            st.error("Could Not Validate MySQL connection parameters")
    except:
        st.error("Could not save Configurations..")

if pull_new_data:
    clvcalc = clvcalculator()       
    check_mysql_conn = clvcalc.check_mysql_trans()
    if check_mysql_conn:
        # Start the background thread
        x = threading.Thread(target=background_job)
        x.start()
        # Clear Clearing
        st.experimental_memo.clear()
        st.success("Data Is being Pulled from specified source")
    else:
        st.error("Could Not Pull Data From Source")