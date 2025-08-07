

import streamlit as st 

from utils import shareable 





def main(counter : int = 1, selected : str = 'Cat', **kwargs):
    import streamlit as st 

    st.write("This is the shareable page.")

    if st.button('Increment Counter'):
        counter += 1

    st.write("Counter: " + str(counter))


    
    selected = st.selectbox('Select an option', ['Cat', 'Dog', 'Fish'], key='selected_selector')


    st.write("Selection: " + selected)


    st.page_link(page = './pages/other.py', label='Go to Other Page')



shareable(
    main,
    'Shareable Example',
)