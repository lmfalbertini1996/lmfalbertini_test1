#import libraries (required for data)

#import panda as pd
import streamlit as st
import altair as alt
import webbrowser
from streamlit_discourse import st_discourse
from PIL import Image

col1, col2, col3 = st.columns([5,5,1])

with col1:
    url1 = '[ABOUT US](http://www.e4g.polimi.it)'
    st.markdown(url1, unsafe_allow_html=True)

with col2:
    url2 = '[PROJECTS](http://www.e4g.polimi.it/?page_id=68)'
    st.markdown(url2, unsafe_allow_html=True)

with col3:
    url3 = '[RESEARCH](http://www.e4g.polimi.it/?page_id=487)'
    st.markdown(url3, unsafe_allow_html=True)

st.write("""***""")

image = Image.open('gisele_logo.png')
st.image(image, use_column_width=True)

st.write("""
        # GISele: Planning of Rural Electrification in Developing Countries
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
        
        The tool is an interactive application able to help stakeholder in the decision making process for electric systems in rural areas. In order to better understand the idea, please download the FAC-SIMILE.
        
        
        """)


with open("Layout.pdf", "rb") as pdf_file:
    PDFbyte = pdf_file.read()

    st.download_button(label="Download FAC-SIMILE",
                       data=PDFbyte,
                       file_name="test.pdf",
                       mime='application/octet-stream')

st.write("""***""")

col1, col2 = st.columns([5,2])
with col1:
    st.write("""

            ##  Ensure access to affordable, reliable, sustainable and modern energy
            
             """)
with col2:
    image = Image.open('SDG7.png')
    st.image(image, use_column_width=True)

st.write("""
    The 2030 Agenda for Sustainable Development has set out 17 Sustainable Development Goals (SDGs) and 169 targets, which jointly constitute a comprehensive plan of action for people, planet, prosperity, peace and partnership.

SDG7 is a first-ever universal goal on energy, with targets on access, efficiency, renewables and means of implementation. Ensuring access to affordable, reliable, sustainable and modern energy for all is crucial for achieving the Sustainable Development Goals, from its role in the eradication of hunger and poverty, through advancements in health, education, inclusive growth, sustainable cities, water supply, infrastructure, industrialization, etc., to combating climate change.

“Energy is the golden thread that connects economic growth, social equity, and environmental sustainability. With access to energy, people can study, go to university, get a job, start a business – and reach their full potential.” Energy is central to nearly every major challenge and opportunity the world faces today – security, climate change, food production, jobs or increasing incomes. Sustainable energy generates opportunity – it transforms lives, economies and the planet. There are tangible health benefits to having access to electricity, and a demonstrable improvement in wellbeing. Energy access therefore constitutes a core component of the sustainable development agenda for energy. The production of useable energy can also be a source for climate change – accounting for around 60% of total global greenhouse gas emissions.

For more info and statistics, please click on the button "SDG 7".
    
    """)

url4 = 'sdgs.un.org/goals/goal7'
if st.button('SDG 7'):
    webbrowser.open_new_tab(url4)

st.write("""***""")

st.write("""
        ## Contact us
Darlain Edeme: darlain.edeme@polimi.it;

Aleksandar Dimovsky: aleksandar.dimovsky@polimi.it;

Lorenzo Maria Filippo Albertini: lorenzomaria.albertini@polimi.it;

Marco Merlo: marco.merlo@polimi.it

###### Politecnico di Milano-Energy Department

###### Via Lambruschini 4, Milano
        
        
***
         """)

add_selectbox = st.sidebar.selectbox(
    "Do you want to contact us?",
    ("Email", "Facebook", "Phone")
)

#add_selectbox = st.sidebar.selectbox(
 #   "What are you looking for ?",
  #  ("DOWNLOAD FACSIMILE", "START")
