import streamlit as st

def init():
    global conn
    conn = st.connection("postgresql", type="sql")
