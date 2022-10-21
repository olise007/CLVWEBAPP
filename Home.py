import streamlit as st
st.set_page_config(
    page_title="Customer Life Time Value APP",
    page_icon="📊"
 )

st.markdown('''
# CUSTOMER LIFE TIME VALUE APP (MVP)

This web app plugs into a data source in a MySQL RDS (Relational Database System) as specified in the configuration option on the side menu. 

This app is designed to calculate customer life time value and show insights into transactional data using the BG/NBD Model detailed in [“Counting Your Customers” the Easy Way: An Alternative to the Pareto/NBD Model"](http://brucehardie.com/papers/018/fader_et_al_mksc_05.pdf)



''')
import streamlit as st
from PIL import Image 

image_dir = './images/'        
 

col1 = st.columns(1)
logo1 = Image.open(image_dir + 'clvimage.jpg')
logo1 =logo1.resize ((3000,1500))
st.image(logo1)
st.markdown(" # ***'Staying updated with customer details with the help of CLV app....'*** ")
