import streamlit as st
import pandas as pd
import numpy as np
from model.clvcalculator import clvcalculator
from model.filter_dataframe import filter_dataframe as ft
#from st_aggrid import AgGrid


st.set_option('deprecation.showPyplotGlobalUse', False)

st.set_page_config(
    page_title="Dashboard- Customer Life Time Value APP",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

clvcalc = clvcalculator()

@st.cache(ttl=900)
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

def main():
    check_trans_data = clvcalc.check_transaction_table()

    if check_trans_data:

        page = st.sidebar.selectbox('Select page',[
            'CLV Data',
            'Customer Alive Probability History Path',
            'RFM Distribution',
            'Heterogeneity Distribution',
            'Customer Value Predictions'
            ]) 
        
        match page:
            case 'CLV Data':
                #Data frame Showing CLV Predictions
                dash_contents = load_summary()
                st.header("CLV Summary")
                st.write('''
                This Data frame shows the Customer Life Time Summary of the entire Customers in the data set.
                You can use the filter option to filter data according to any of the columns and specified value
                ''')        
                df = dash_contents['summary_df']
                st.dataframe(ft.filter_dataframe((df)))
        
            case "Customer Alive Probability History Path":
                st.header('''
                Customer Predictions and Probability Histories
                ''')
                st.write('''
                The graph below shows customers probability of being alive. 
                This can be used for for marketing activities, forecasting or more generally churn prevention.
                You can see a customers historical of probability of being alive by selecting the CustomerID below from
                the dropdown menu
                ''')
                #Show History of Being Alive For Customers
                dash_contents = load_summary()
                col1, col2 = st.columns([1,3])
                
                with col1:
                    st.write('Show a customers history of being alive')
                    custID = st.selectbox(label="Select CustomerID", options=dash_contents['df_customers'], index=0)
                    # Every form must have a submit button.
                with col2:
                    fig_hist=clvcalc.hist_of_alive(custID=custID)
                    st.pyplot(fig_hist)
                    st.caption('Customer , '+ str(custID) +',: probability of being alive over time')

            case "RFM Distribution":
                #Show RFM Distributions across cohorts
                st.header("RFM Distribution Chart")
                st.write(''' 
                This chart below shows the distribution of Recency, Frequency and Age among Customers within the data set. 
                To see the data distribution for a certain feature, please select that option from the drop-down menu to the left of the chart below.
                ''')
                one_time_buyers = clvcalc.get_no_one_time_buyers()
                st.write('The current percentage of customers who made purchases only once is: ' + str(one_time_buyers) + '%')
                col1, col2 = st.columns([1,3])
                with col1:
                    dist_option = st.selectbox(
                'Choose metric to show distribution?',
                ('Frequency', 'Recency', 'Age'))
                # Every form must have a submit button.
                with col2:
                    match dist_option:
                        case "Frequency":
                            fig = clvcalc.show_dist('frequency')
                        case "Recency":
                            fig = clvcalc.show_dist('recency')
                        case "Age":
                            fig = clvcalc.show_dist('age')
                    st.pyplot(fig)

            case "Heterogeneity Distribution":
                #Show Heterogeneity Distributions
                st.header('''
                Gamma and Beta distributions Visualizations
                ''')
                st.write('''
                The Gamma distribution tells us about the distribution of the transaction rates of our customer base, 
                while the Beta distribution reflects the distribution of probability-to-deactivate.
                ''')
                col1, col2 = st.columns(2)
                with col1:
                    st.pyplot(fig = clvcalc.show_beta_gamma_dist('beta'))

                with col2:
                    st.pyplot(fig = clvcalc.show_beta_gamma_dist('gamma'))

            case "Customer Value Predictions":
                #Show Segmentation using Histograms
                st.header('''
                Customer value Predictions
                ''')
                st.write('''
                The Histogram show predicted customer values for future transactions across cohorts in the current dataset.
                ''')
                col1, col2 = st.columns([1,3])

                with col1:
                    st.write(''' 
                    Histogram of value segmentation across cohorts
                    ''')
                    value_option = st.selectbox(
                'Choose metric to show distribution?',
                ('10 days', '30 days', '60 days', '90 days'))
                # Every form must have a submit button.
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

main()