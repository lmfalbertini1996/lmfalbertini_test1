#import libraries (required for data)

#import panda as pd
import streamlit as st
import altair as alt
import webbrowser
#from streamlit_discourse import st_discourse
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
    
st.title("PARTNERS")

col1, col2 = st.columns([5,2])
with col1:

    st.write("""
            ##  FONDAZIONE CARIPLO
                         """)
with col2:
    image = Image.open('FONDAZIONECARIPLO.png')
    st.image(image, use_column_width=True)

st.write("""
       "For 30 years, Fondazione Cariplo has been promoting the life of communities, supporting those who operate in the area and are closest to people's needs. The distances within our communities are increasing, making them more fragmented and fragile. Today more than ever, however, there is a need to shorten these distances in order to have strong and inclusive communities, to support people's lives and to have strong institutions capable of reconciling different needs and directing resources and choices towards a better future for all and in which all can recognise themselves"
               """)

url4 = 'https://www.fondazionecariplo.it/'
if st.button('FONDAZIONE CARIPLO'):
    webbrowser.open_new_tab(url4)
    
st.write("""***""")
  
col1, col2 = st.columns([5,2])
with col1:
    st.write("""
            ##  ICEI
            
             """)
with col2:
    image = Image.open('ICEI.png')
    st.image(image, use_column_width=True)

st.write("""
       "We work with people and local communities to improve social and economic conditions and to promote inclusive, fair and sustainable societies with a participatory approach.
We implement cooperation programmes in Italy and across the world, with special attention to environment, in the areas of intercultural citizenship, labour market integration, sustainable agriculture and responsible tourism.
Priority targets across all our focus areas are vulnerable people, in particular youth and women"
               """)

url5 = 'http://icei.it/'
if st.button('ICEI'):
    webbrowser.open_new_tab(url5)
    
st.write("""***""")

col1, col2 = st.columns([5,2])
with col1:
    st.write("""
            ##  ENGREEN
            
             """)
with col2:
    image = Image.open('ENGREEN.png')
    st.image(image, use_column_width=True)

st.write("""
       "Our Mission is to build a long-lasting business relationship based on trust and competency in order to achieve tangible results on energy access, low-carbon technologies and climate change mitigation through innovative business models to de-risk investments"
       """)

url6 = 'https://www.engreensolutions.com/about/'
if st.button('ENGREEN'):
    webbrowser.open_new_tab(url6)
    
st.write("""***""")

#discourse_url = "discuss.streamlit.io"
#topic_id = 8061

#st_discourse(discourse_url, topic_id)

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
