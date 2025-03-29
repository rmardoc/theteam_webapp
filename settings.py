import streamlit as st

def init():
    global conn
    #app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or "postgresql://postgres:password@localhost:5432/postgres"
    conn = st.connection("herokupostgresql", url = "env:DATABASE_URL", type="sql")
