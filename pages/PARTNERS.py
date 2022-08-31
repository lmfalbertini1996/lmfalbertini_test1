
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
    url3 = '[RESEARCH](http://icei.it/)'
    st.markdown(url3, unsafe_allow_html=True)

st.write("""***""")
