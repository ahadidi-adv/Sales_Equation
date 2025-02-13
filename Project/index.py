import streamlit as st


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
footer="

<style> your css code put here</style>

<div class='footer'>

<p>the word you want to tell<a style='display:block;text-align:center;' 

href='https://www.streamlit.io' target='_blank'>your email address put here</a></p>

</div>"

st.markdown(footer, unsafe_allow_html=True)
st.logo("Africa.png", icon_image="Logo.png")

st.write("# Calibrage et optimisation des visites commerciales 🎯")
st.image("Africa.png", use_container_width=True)
st.image("vector.jpg", use_container_width=True)
