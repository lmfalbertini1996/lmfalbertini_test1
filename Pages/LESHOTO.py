
import streamlit as st
import altair as alt
import webbrowser
from PIL import Image

st.title("Leshoto")

st.markdown('DUMELA')

url4 = 'sdgs.un.org/goals/goal7'
if st.button('SDG 7'):
    webbrowser.open_new_tab(url4)

    open("layout.pdf", "rb") as pdf_file:
    PDFbyte = pdf_file.read()

    st.download_button(label="Download FAC-SIMILE",
                       data=PDFbyte,
                       file_name="test.pdf",
                       mime='application/octet-stream')