
import streamlit as st
import altair as alt
import webbrowser
from PIL import Image

st.title("PARTNERS")

st.write("""***""")

st.write("""
        ## FONDAZIONE CARIPLO
         """)

st.write("""
       "For 30 years, Fondazione Cariplo has been promoting the life of communities, supporting those who operate in the area and are closest to people's needs. The distances within our communities are increasing, making them more fragmented and fragile. Today more than ever, however, there is a need to shorten these distances in order to have strong and inclusive communities, to support people's lives and to have strong institutions capable of reconciling different needs and directing resources and choices towards a better future for all and in which all can recognise themselves"
               """)

url4 = 'https://www.fondazionecariplo.it/'
if st.button('FONDAZIONE CARIPLO'):
    webbrowser.open_new_tab(url4)
    
st.write("""***""")
    
st.write("""
        # ICEI
         """)

st.write("""
       "We work with people and local communities to improve social and economic conditions and to promote inclusive, fair and sustainable societies with a participatory approach.

We implement cooperation programmes in Italy and across the world, with special attention to environment, in the areas of intercultural citizenship, labour market integration, sustainable agriculture and responsible tourism.

Priority targets across all our focus areas are vulnerable people, in particular youth and women"
               """)

url5 = 'http://icei.it/'
if st.button('ICEI'):
    webbrowser.open_new_tab(url5)
    
st.write("""***""")

st.write("""
        # ENGREEN
         """)

st.write("""
       "Our Mission is to build a long-lasting business relationship based on trust and competency in order to achieve tangible results on energy access, low-carbon technologies and climate change mitigation through innovative business models to de-risk investments"
       """)

url6 = 'https://www.engreensolutions.com/about/'
if st.button('ENGREEN'):
    webbrowser.open_new_tab(url6)
    
    st.write("""***""")
    
    

