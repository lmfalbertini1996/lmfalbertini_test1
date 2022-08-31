
import streamlit as st
import altair as alt
import webbrowser
from PIL import Image

st.title("PARTNERS")

col1, col2, col3 = st.columns([5,5,1])

with col1:
    url1 = '[FONDAZIONE CARIPLO](https://www.fondazionecariplo.it/)'
    st.markdown(url1, unsafe_allow_html=True)

with col2:
    url2 = '[ENGREEN](http://https://www.engreensolutions.com/)'
    st.markdown(url2, unsafe_allow_html=True)

with col3:
    url3 = '[ICEI](http://icei.it/)'
    st.markdown(url3, unsafe_allow_html=True)

st.write("""***""")

st.write("""
        # FONDAZIONE CARIPLO
        ***
         """)

st.write("""
       "For 30 years, Fondazione Cariplo has been promoting the life of communities, supporting those who operate in the area and are closest to people's needs. The distances within our communities are increasing, making them more fragmented and fragile. Today more than ever, however, there is a need to shorten these distances in order to have strong and inclusive communities, to support people's lives and to have strong institutions capable of reconciling different needs and directing resources and choices towards a better future for all and in which all can recognise themselves"
               """)

    url4 = '[FONDAZIONE CARIPLO](https://www.fondazionecariplo.it/)'
    st.markdown(url4, unsafe_allow_html=True)
