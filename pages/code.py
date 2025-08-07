

import streamlit as st 


st.header("Usage")

st.code("""
import streamlit as st 

from utils import shareable 




# Wrap your code within a function, use type annotations 
def main(counter : int = 1, selected : str = 'Cat', **kwargs):
    
    import streamlit as st 

    st.write("This is the shareable page.")

    if st.button('Increment Counter'):
        counter += 1

    st.write("Counter: " + str(counter))
    
    # Key must be differnet from variable name
    selected = st.selectbox('Select an option', ['Cat', 'Dog', 'Fish'], key='selected_selector')
    
    st.write("Selection: " + selected)


    st.page_link(page = 'other.py', label='Go to Other Page')



shareable(
    main,
    'Shareable Example',
)
""")

with st.expander("Wrapper code",expanded = False):
    
    with open('utils.py') as f:
        text = f.readlines()

    st.code("".join(text))