import streamlit as st 


pages = [
    st.Page('./pages/shareable.py', title = 'Shareable'),
    st.Page('./pages/other.py', title = 'Other')   ,
    st.Page('./pages/code.py', title = 'Code')
]

st.navigation(pages).run()