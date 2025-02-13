import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
html_string='''
<script>
// To break out of iframe and access the parent window
const streamlitDoc = window.parent.document;

// Make the replacement
document.addEventListener("DOMContentLoaded", function(event){
        streamlitDoc.getElementsByTagName("footer")[0].innerHTML = "Provided by <a href='https://yourwebsite.com' target='_blank' class='css-z3au9t egzxvld2'>Your Link Display Text Here</a>";
    });
</script>
'''
components.html(html_string)
st.logo("Africa.png", icon_image="Logo.png")

st.write("# Calibrage et optimisation des visites commerciales 🎯")
st.image("Africa.png", use_container_width=True)
st.image("vector.jpg", use_container_width=True)
