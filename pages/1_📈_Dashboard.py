import streamlit as st
import pandas as pd
import numpy as np
from model.clvcalculator import clvcalculator
from model.filter_dataframe import filter_dataframe as ft

st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(
    page_title="Dashboard- Customer Life Time Value APP",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

clvcalc = clvcalculator()
check_trans_data = clvcalc.check_transaction_table()

if check_trans_data:
    @st.experimental_memo(ttl=900)
    def load_summary():
        df = clvcalc.get_clv_summary()
        copyDf = df.copy()
        copyDf['CustomerID'] = copyDf.index
        df_customers = copyDf['CustomerID'].copy()
        

        dash_dict = {
            "summary_df":df,
            "df_customers":df_customers
        }
        return dash_dict
    
    dash_contents = load_summary()
    #Dataframe Showing CLV Predictions
    st.header("CLV Summary")
    st.write('''
    This Dataframe shows the Customer Life Time Summary of the entire Customers in the data set.
    You can use the filter option to fileter data accourding to any of the columns and specified value
    ''')        
    df = dash_contents['summary_df']
    st.dataframe(ft.filter_dataframe((df)))

    #Show History of Being Alive For Customers
    col1, col2 = st.columns([1,3])
    
    with col1:
        st.write('Show a customers history of being alive')
        custID = st.selectbox(label="Select CustomerID", options=dash_contents['df_customers'], index=0)
    with col2:    
        fig_hist=clvcalc.hist_of_alive(custID=custID)
        st.pyplot(fig_hist)
        st.caption('Customer , '+ str(custID) +',: probability of being alive over time')

    #Show RFM Distributions accross cohorts
    col1, col2 = st.columns([1,3])

    with col1:
        st.write(''' 
        Distribution of Recency, Frequency and Age among Customers.
        ''')
        dist_option = st.selectbox(
    'Choose metric to show distribution?',
    ('Frequency', 'Recency', 'Age'))
    with col2:
        match dist_option:
            case "Frequency":
                fig = clvcalc.show_dist('frequency')
            case "Recency":
                fig = clvcalc.show_dist('recency')
            case "Age":
                fig = clvcalc.show_dist('age')
        st.pyplot(fig)


    #Show Heteroginity Distributions
    st.write('''
        Heteroginity in Dropout Probability is Beta distribution of p: customer's probability of dropping out immediately after a transaction.\n
        Heteroginity in Transaction Rate is Gamma distribution of lambda: customers' propensitiy to purchase
        ''')
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig = clvcalc.show_beta_gamma_dist('beta'))

    with col2:
        st.pyplot(fig = clvcalc.show_beta_gamma_dist('gamma'))



    #Show Segmentation using Historgrams
    col1, col2 = st.columns([1,3])

    with col1:
        st.write(''' 
        Histogram of value segmentation across cohorts
        ''')
        value_option = st.selectbox(
    'Choose metric to show distribution?',
    ('10 days', '30 days', '60 days', '90 days'))
    with col2:
        match value_option:
            case "10 days":
                fig10 = clvcalc.show_value_histogram(days=10)
                st.pyplot(fig10)
            case "30 days":
                fig30 = clvcalc.show_value_histogram(days=30)
                st.pyplot(fig30)
            case "60 days":
                fig60 = clvcalc.show_value_histogram(days=60)
                st.pyplot(fig60)
            case "90 days":
                fig90 = clvcalc.show_value_histogram(days=90)
                st.pyplot(fig90)    
        


else:
    st.error("Could Not Find Data...Data Pull may still be in progress. If this is not completed after a while, please check config settings")
