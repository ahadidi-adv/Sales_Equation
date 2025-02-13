import streamlit as st
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.logo("Africa.png", icon_image="Logo.png")

st.write("# Calibrage et optimisation des visites commerciales 🎯")
st.image("Africa.png", use_container_width=True)
st.image("vector.jpg", use_container_width=True)
