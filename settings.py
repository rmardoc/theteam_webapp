import streamlit as st
import os
#import psycopg2



def init():
    global conn
    #app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or "postgresql://postgres:password@localhost:5432/postgres"
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = st.connection("herokupostgresql", url = DATABASE_URL, type="sql")
