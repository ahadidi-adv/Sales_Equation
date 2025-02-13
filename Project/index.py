import streamlit as st


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
footer {
	
	visibility: hidden;
	
	}
footer:after {
	content:'goodbye'; 
	visibility: visible;
	display: block;
	position: relative;
	#background-color: red;
	padding: 5px;
	top: 2px;
}
st.logo("Africa.png", icon_image="Logo.png")

st.write("# Calibrage et optimisation des visites commerciales 🎯")
st.image("Africa.png", use_container_width=True)
st.image("vector.jpg", use_container_width=True)
