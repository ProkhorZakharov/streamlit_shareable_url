

import streamlit as st 



st.write("This is the other page.")

# go to icon
st.page_link(page = './pages/shareable.py', label='Go to Shareable Page' )

st.write("Counter: " + str( st.session_state.get('counter', None)))

st.write("Selection: " + str(st.session_state.get('selected', None)))
