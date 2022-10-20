import streamlit as st
st.set_page_config(
    page_title="Customer Life Time Value APP",
    page_icon="🗒️"
 )

st.markdown('''
# CUSTOMER LIFE TIME VALUE APP (MVP)

## Usage

To use this webapp, first input the connection parameters to your remote data source holding the transactions data you wish to process.
 You can do this by inputting connection settings on the MySQL Source Configurations Page using the "Source Config" menu. 
 Some of the configuration parameters to be set are;
 
 - Database Host: - This is the hostname or ipaddress of the MySQL Server containing the data to be processed
 - Database Port: - The port open on the MySQL Server in order to connect and pull data.
 - Database Name: - The name of the database holding the transactional data
 - Database Username:- This is the username to be used to connect to the MySQL server
 - Database Password: - Password to be used to connect to the database server.
 - Source Data Table Name:- The name of the table in the database holding the transactions data on which to perform computations and analytics

Once you have setup the connection parameters on the MySQL server config page, you should then move to the Table Field Configurations Page using the "Field Config" menu, select and save the approprite column name from the table schema matching the requried field name displayed in the form. After saving, click the button "Pull Data From Source" to begin preliminary data pulling and cleaning for analytics.

At the point you can navigate to the dashboard to begin exploring the charts and CLV insights available on the dataset.

## Internal Database Server

To perform calculations on data stored in CSV or other flat file formats, it is required that the data is first loaded into the internal database bundled with this app.
Use the following connection parameters to login remotely, create a database and table and transfers data that the app is required to process;

 - Database host:- localhost (Use host DNS name of the Web App when connecting to this internal server remotely)
 - Database port:- 3306
 - Database username:- clvwebapp
 - Database password:- clvwebapp
 - Database name:- user specified (created by user when connected from a remote source or users local machine)
 - Source Data Table Name: - user specified

Remember to replicate the same connection settings used and/or created in the MySQL Source Configurations Page and also properly map the column name to the required fields in the Table Field Configurations Page.

>**Note: that you have to to click on the "Pull Data From Source" button in order to update the computations or analytics done by the app when there is change to the configurations of the datasource or to pull newly updated data from an already specified data source.**

''')