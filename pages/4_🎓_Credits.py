# Streamlit dependencies
import streamlit as st
from PIL import Image 

image_dir = './images/'
col1, col2 = st.columns(2)
with col1:
    st.header("Imaorise Umobong")
    st.subheader("President")             
    st.image(image_dir + 'Ima.jpeg', width =310)
with col2:
    st.header("Marble Kusanele")
    st.subheader("Vice-President")             
    st.image(image_dir + 'Kusanele.jpeg', width =300)                                   
col3, col4 = st.columns(2)        
with col3:
    st.header("Francis Ikegwu")
    st.subheader("Cloud expert")            
    st.image(image_dir + 'Frank.jpeg', width=300)            
with col4:
    st.header("Vincent")
    st.subheader("Technical Director ")             
    st.image(image_dir + 'Vincent.jpeg', width =300)                      
col5, col6 = st.columns(2)             
with col5:
    st.header("Blessing Ezinne")
    st.subheader("Director Strategies")             
    st.image(image_dir + 'Blessing.jpeg', width =300)
with col6:
    st.header("Peter Otanwa")
    st.subheader("ML_Model Expert ")             
    st.image(image_dir + 'Peter.jpeg', width =300)      
               
st.subheader("For more information")
if st.checkbox('Show contact information'): # data is hidden if box is unchecked
    st.info("olise007@gmail.com, mpofukusanele@gmail.com, frankonero91@gmail.com, chineduvince221@gmail.com,  bleezy068@gmail.com, otanwapeter@gmail.com") 