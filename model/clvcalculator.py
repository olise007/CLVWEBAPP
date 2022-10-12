import json
import math
import scipy.stats as stats
import streamlit as st
import mysql.connector
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import seaborn as sns
import os.path

from sklearn.metrics import mean_absolute_percentage_error

from btyd import BetaGeoFitter, GammaGammaFitter
from btyd.utils import \
    calibration_and_holdout_data, \
    summary_data_from_transaction_data, \
    calculate_alive_path
from btyd.plotting import \
    plot_frequency_recency_matrix, \
    plot_probability_alive_matrix, \
    plot_period_transactions, \
    plot_history_alive, \
    plot_cumulative_transactions, \
    plot_calibration_purchases_vs_holdout_purchases, \
    plot_transaction_rate_heterogeneity, \
    plot_dropout_rate_heterogeneity

import warnings
warnings.filterwarnings("ignore")
sns.set(rc={'image.cmap': 'coolwarm'})

pd.set_option("display.precision",2)
np.set_printoptions(precision=2, suppress=True)
pd.options.display.float_format = '{:,.0f}'.format

class clvcalculator:

    def __init__(self):
        self.sqlite_db = 'clvsummary.db'
        self.training_file = 'datastore/clvfit.pkl'
        self.pull_limit = 100000
        #Set MySQL server connection details
        with open('./config/mysql_source.json', 'r') as sourceinfo:
            self.mysql_config = json.load(sourceinfo)
        with open('./config/field_info.json', 'r') as fieldinfo:
            self.field_info = json.load(fieldinfo)    
        self.conn = self.init_connection()
        self.sqlite_conn = self.sqlite_connection()
        self.train_data = None
        
    # Initialize connection.
    def init_connection(self):
        host = self.mysql_config['host']
        port = self.mysql_config['port']
        user = self.mysql_config['user']
        password = self.mysql_config['password']
        database = self.mysql_config['database']

        try:
            mydb = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
        except:
            mydb = False

        return mydb


    def check_transaction_table(self):
        conn = self.sqlite_conn
        c = conn.cursor()
                    
        #get the count of tables with the name
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='transactions' ''')

        #if the count is 1, then table exists
        if c.fetchone()[0]==1 : 
            check = True
        else :
            check = False
                    
        #commit the changes to db			
        conn.commit()
        return check
    
    def check_mysql_trans(self):
        table = self.mysql_config['table']
        param = (table)
        if(self.conn):
            conn = self.conn
            c = conn.cursor()
            
            #get the count of tables with the name
            sql = "SELECT COUNT(*)FROM information_schema.tables WHERE table_schema =  DATABASE() AND table_name = "
            sql += "'"+table+"'"
            c.execute(sql)

            #if the count is 1, then table exists
            if c.fetchone()[0]==1 : 
                check = True
            else :
                check = False
                        
            #commit the changes to db			
            conn.commit()
            return check
    
    def get_mysql_table_schema(self):
        table = self.mysql_config['table']
        conn = self.conn
        c = conn.cursor()
        
        #get the count of tables with the name
        sql = "DESCRIBE "
        sql += table
        c.execute(sql)
        tableschema = c.fetchall()
        return tableschema

    
    def get_mysql_source(self, limit, offset):
        table = self.mysql_config['table']
        query = 'SELECT * FROM '+table+' LIMIT ' + str(limit) + ' OFFSET ' + str(offset)
        df = pd.read_sql_query (query, self.conn)
        return df  

    def getdata_source(self, limit, offset):
        field_info = self.field_info
        df = self.get_mysql_source(limit, offset)
        newdf = df[[
            field_info['CustomerID'],
            field_info['UnitPrice'],
            field_info['Quantity'],
            field_info['InvoiceDate'],
            field_info['InvoiceNo']
        ]].copy()
        newdf.rename(columns={
            field_info['CustomerID']:'CustomerID',
            field_info['UnitPrice']:'UnitPrice',
            field_info['Quantity']:'Quantity',
            field_info['InvoiceDate']:'InvoiceDate',
            field_info['InvoiceNo']:'InvoiceNo'
        }, inplace=True)
       
        return newdf  

    def sqlite_connection(self):
        location = './datastore/' + self.sqlite_db
        connection = sqlite3.connect(location)
        return connection

    def remove_transact_table(self):
        cursor = self.sqlite_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS transactions''')
        self.sqlite_conn.commit()
          

    def load_clean_transactions(self, breaktrans=True):
        cursor = self.sqlite_conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS transactions''')
        self.sqlite_conn.commit()  
        #Check Number of Records
        table = self.mysql_config['table']
        conn = self.conn
        c = conn.cursor()
        c.execute("select count(*) from "+table)
        record_count = c.fetchone()[0]

        if(breaktrans == False):
            limit = record_count
        else:
            limit = self.pull_limit
        
        offset = 0

        if(record_count > limit):
            num_iterations = math.ceil(record_count/limit)
        else:
            num_iterations = 1
        
        interation = num_iterations

        while (interation > 0):
            interation = interation - 1
            #Load data from source
            data = self.getdata_source(limit, offset)
            offset += limit
            df0 = data
            #Begin Data Cleaning
            df1 = df0.copy()
            # delete rows in which we cannot identify the customer
            df1 = df1[pd.notnull(df1["CustomerID"])]
            # restrict to transactions with positive quantities
            df1["Quantity"] = df1["Quantity"].astype(np.int64)
            df1 = df1[df1["Quantity"] > 0]
            # datetime to date format
            df1["InvoiceDate"] = pd.to_datetime(df1["InvoiceDate"]).dt.date #normalize()
            #df1.set_index("InvoiceDate", inplace=False)
            # treat CustomerID as a categorical variable
            df1["CustomerID"] = df1["CustomerID"].astype(np.int64).astype(object)
            df1["UnitPrice"] = df1["UnitPrice"].astype(np.float64)
            # delete columns that are not useful
            try:
                d1 = df1.drop(["InvoiceNo"], axis=1, inplace=True)
            except:
                pass
            # revenues = quantity * unitprice
            df1["Revenues"] = df1["Quantity"] * df1["UnitPrice"]
            df1.to_sql('transactions_temp', self.sqlite_conn, if_exists='append', index = False)
        cursor.execute('''ALTER TABLE transactions_temp RENAME TO transactions''')
        self.sqlite_conn.commit()
        return True

    def load_trans_data(self, custID=None):
        conn = self.sqlite_conn

        if (custID==None):
            sql = '''
            SELECT CustomerID, Revenues, UnitPrice, Quantity, InvoiceDate 
            FROM transactions
            '''
        else:
            sql = '''
            SELECT CustomerID, Revenues, UnitPrice, Quantity, InvoiceDate 
            FROM transactions WHERE CustomerID =
            '''
            sql += str(custID)

        df1 = pd.read_sql_query(sql, conn)
        
        return df1

    def load_model_trainer(self, reset=False):
        if (self.train_data != None):
            return self.train_data
        else:
            df1 = self.load_trans_data()
            min_date = df1["InvoiceDate"].min()
            max_date = df1["InvoiceDate"].max()

            df_rft = summary_data_from_transaction_data(
                transactions = df1, 
                customer_id_col = "CustomerID", 
                datetime_col = "InvoiceDate", 
                monetary_value_col = "Revenues", 
                observation_period_end = max_date, 
                freq = "D")
            
            # BG/NBD model
            if (reset == True) and os.path.isfile(self.training_file):
                os.remove(self.training_file)

            #Generate and/or load BG/NBD model
            bgf = BetaGeoFitter(penalizer_coef=1e-06)
            if os.path.isfile(self.training_file):
                bgf.load_model(self.training_file)
            else:    
                bgf.fit(
                    frequency = df_rft["frequency"], 
                    recency = df_rft["recency"], 
                    T = df_rft["T"],   
                    weights = None,  
                    verbose = True,   
                    tol = 1e-06)
                pd.options.display.float_format = '{:,.3f}'.format    
                bgf.save_model(self.training_file)

            ##Return Training Data
            train_dict = {
                "rfm_data":df_rft, #summary RFM Data
                "data_train":bgf, # Training Object from BG/NBD Model
                "trans_data":df1
            }

            self.train_data = train_dict
            return train_dict

    def refresh_model_data(self):
        self.load_clean_transactions()
        self.load_model_trainer(reset=True)
        self.get_clv_summary(storesummary=True)

    def get_clv_summary(self, custID=None, storesummary=False):
        trains = self.load_model_trainer()
        df_rft = trains['rfm_data']
        bgf = trains['data_train']

        prob_alive = bgf.conditional_probability_alive(
        frequency = df_rft["frequency"], 
        recency = df_rft["recency"], 
        T = df_rft["T"])

        df_rft["prob_alive"] = prob_alive

        if(custID != None):
            df_rft_C = df_rft.loc[custID,:]
        else:
            df_rft_C = df_rft
        # helper function: predict each customer's purchases over next t days
        def predict_purch( df, t):
            df["predict_purch_" + str(t)] = \
                    bgf.predict(
                        t, 
                        df["frequency"], 
                        df["recency"], 
                        df["T"])

        def predict_val( df, t):
            df["predict_val_" + str(t)] = df["predict_purch_" + str(t)]*df["prob_alive"]*df["monetary_value"]
        # call helper function: predict each customer's purchases over multiple time periods
        t_FC = [10, 30, 60, 90]
        _ = [predict_purch(df_rft_C, t) for t in t_FC]
        _ = [predict_val(df_rft_C, t) for t in t_FC]

        #Store CLV Summary for Future Use
        if(storesummary == True):
            cursor = self.sqlite_conn.cursor()
            cursor.execute('''DROP TABLE IF EXISTS clvsummary''')
            self.sqlite_conn.commit()
            try:
                df_rft_C.to_sql('clvsummary', self.sqlite_conn, if_exists='fail', index = False)
            except:
                pass

        return df_rft_C
    
    def get_stored_clvsummary(self):
        conn = self.sqlite_conn
        sql = '''
        SELECT * 
        FROM clvsummary
        '''
        df1 = pd.read_sql_query(sql, conn)
        return df1

    def show_dist(self, metric_type=None):
        trains = self.load_model_trainer()
        df_ch = trains['rfm_data']
        max_freq = df_ch["frequency"].quantile(0.98)
        max_rec = df_ch["recency"].max()
        max_T = df_ch["T"].max()

        fig = plt.figure(figsize=(8, 4))

        match metric_type:
            case "frequency":
                ax = sns.distplot(df_ch["frequency"])
                ax.set_xlim(0, max_freq)
                ax.set_title("frequency (days): distribution of the customers");
            case "recency":
                ax = sns.distplot(df_ch["recency"])
                ax.set_xlim(0, max_rec)
                ax.set_title("recency (days): distribution of the customers")
            case "age":
                ax = sns.distplot(df_ch["T"])
                ax.set_xlim(0, max_T)
                ax.set_title("customer age T (days): distribution of the customers")

        return fig

    def show_beta_gamma_dist(self, chart_type=None):
        trains = self.load_model_trainer()
        bgf = trains['data_train']
        match chart_type:
            case "gamma":
                plot_transaction_rate_heterogeneity(model = bgf)  
            case "beta":
                plot_dropout_rate_heterogeneity(model = bgf)
    
    def hist_of_alive(self, custID=None):
        trains = self.load_model_trainer()
        bgf = trains['data_train']
        df1 = self.load_trans_data()
        df1["InvoiceDate"] = pd.to_datetime(df1["InvoiceDate"]) #normalize()
        max_date = df1["InvoiceDate"].max()
        min_date = df1["InvoiceDate"].min()
        span_days = (max_date - min_date).days
        # history of the selected customer: probability over time of being alive
        df1C = df1[df1["CustomerID"] == custID]
        fig = plt.figure(figsize=(20,4))
        plot_history_alive(
                            model = bgf, 
                            t = span_days, 
                            transactions = df1C, 
                            datetime_col = "InvoiceDate");
        return fig

    def show_value_histogram(self, days=None):
        conn = self.sqlite_conn
        sql = '''
        SELECT predict_val_10, predict_val_30, predict_val_60, predict_val_90
        FROM clvsummary
        '''
        rfmdata = pd.read_sql_query(sql, conn)

        fig, ax = plt.subplots(figsize = (12, 7))
        ax = sns.histplot(rfmdata["predict_val_" + str(days)], 
                        kde=False, 
                        binwidth = 2)
        ax.set_title(f'Customer value histogram')
        ax.set_xlabel(r'Customer value estimate for '+ str(days) +' periods ($)')
        ax.set_ylabel(r'Number of customers in each bin')
        ax.set_xlim(-2,20)

        return fig

    