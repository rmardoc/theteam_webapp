import streamlit as st
#from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
from sheets import sheets
from chat import chat
from gamerules import gamerules

def main():
    st.markdown(
        """
        hello world
        """,
            unsafe_allow_html=True,
        )



if __name__ == "__main__":
    main()