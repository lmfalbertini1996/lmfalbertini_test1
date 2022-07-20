#import libraries (required for data)

#import panda as pd
import streamlit as st
import altair as alt
import webbrowser
from PIL import Image

col1, col2, col3 = st.columns([5,5,1])

with col1:
    url = 'www.e4g.polimi.it//'

    if st.button('ABOUT US'):
        webbrowser.open_new_tab(url)
with col2:
    st.button('PROJECTS')
with col3:
    st.button('PARTNERS')

st.write("""***""")

image = Image.open('SDG7.png')
st.image(image, use_column_width=True)

st.write("""
        # GISele: Planning of Rural Electrification in Devloping Countries
        ***
         """)

col1, col2 = st.columns([5,1])

with col1:
    st.write("""
            ## A product by Politecnico di Milano
             """)
with col2:
    image = Image.open('Logo_poli.jpg')
    st.image(image, use_column_width=True)

st.write("""
        GISele (GIS for electrification) is a open source Python-based tool. It has been developed with the goal of improving the planning of rural electrification in developing countries. The tool uses GIS and terrain analysis to model the area under study, groups loads using a density-based clustering algorithm and it uses graph theory to find the least-costly electric network topology that can connect all the people in the area. The ultimate goal is to define the LCOE (Levelized Cost of Electricity) of decentralized and grid connected solutions.
        
        """)

st.write("""***""")

st.header('What are you looking for ?') ## si può cambiare colore ?

col1, col2 = st.columns([5,1])

with col1:
    with open("layout.pdf", "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(label="Download FAC-SIMILE",
                       data=PDFbyte,
                       file_name="test.pdf",
                       mime='application/octet-stream')
with col2:
    st.button('START NOW')

st.write("""***""")

add_selectbox = st.sidebar.selectbox(
    "Do you want to contact us?",
    ("Email", "Facebook", "Phone")
)

#add_selectbox = st.sidebar.selectbox(
 #   "What are you looking for ?",
  #  ("DOWNLOAD FACSIMILE", "START")