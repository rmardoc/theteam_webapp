import streamlit as st
from streamlit_server_state import server_state, server_state_lock
#from streamlit_extras.stylable_container import stylable_container
from sheets import sheets
from chat import chat
import json
import random



# TODO: 
# - creare una guida all'uso
# - testare nuovo chat widget
# - bottone rename room
# - bottone rename PG 
# - lingua inglese
# - pulsanti fatti ad icona (più intuitivi e minimali)
# - export ed import delle room in JSON format



def main():

    def randomize_nickname():
        with open("data/animals.json") as f:
            animals = json.load(f)
        with open("data/adjectives.json") as f:
            adjectives = json.load(f)
        name = f"{random.choice(adjectives)}_{random.choice(animals)}"
        return name

    ## loading variables
    with server_state_lock["rooms"]:
        if "rooms" not in server_state:
            server_state["rooms"] = {}
    rooms = server_state["rooms"].keys()
    


 
    ## sidebar
    with st.sidebar.container(border=True):
        @st.dialog("Room deletion")
        def confirm_roomdeletion(room):
            st.write(f"Deleting room {room}. Room data will be lost")
            if st.button("Confirm deletion"):
                with server_state_lock["rooms"]:
                    del server_state["rooms"][room]
                st.rerun()

        if not rooms:
            st.sidebar.write("No rooms available, create one.") 
            room = ""
        else: 
            room = st.sidebar.radio("Select room", rooms)
            if st.sidebar.button("Delete selected Room",use_container_width=True):
                confirm_roomdeletion(room)

        with st.sidebar.form("CreateRoom", border=False):
            def on_create():
                new_room_name = st.session_state.new_room_name
                if new_room_name :
                    with server_state_lock["rooms"]:
                        server_state["rooms"][new_room_name] = { 'messages': [] , 'pg': {} }
            newroom_col1 , newroom_col2, = st.columns([2,3])
            with newroom_col1:
                st.text_input("Room name", label_visibility="collapsed", placeholder="room name", key="new_room_name")
            with newroom_col2:
                st.form_submit_button("Create a new room", on_click=on_create)


   
            
    
    st.sidebar.divider()
    
    if "nickname" in st.session_state:
        nickname = st.session_state.nickname
    else:
        nickname = randomize_nickname()
        st.session_state.nickname = nickname

    with st.sidebar.form("ChangeName", border=False):
        def on_create():
            st.session_state.nickname = st.session_state.new_nickname
        st.markdown(f"Nickname : {nickname}")
        newnick_col1 , newnick_col2, = st.columns([2,3])
        with newnick_col1:
            st.text_input("New Nickname", label_visibility="collapsed", placeholder="new nickname", key="new_nickname")
        with newnick_col2:
            st.form_submit_button("Change Nickname", on_click=on_create)

    #st.sidebar.text_input("Nick name", key=f"newnickname")
    #nickname = st.session_state.nickname 
    
    if not room:
        st.stop()
    
    #room_key = f"room_{room}"
    with server_state_lock["rooms"]:
        if room not in server_state["rooms"]:
            server_state["rooms"][room] = { 'messages': [] , 'pg': {} }
    
    
    
    
    
    ## mainframe check nickname or stop rendering
    if not nickname:
        st.warning("Set your nick name on the left.")
        st.stop()
    
    
    
    with st.container(border=True):
        sheets(room)
    
    with st.container(border=True):
        chat(room= room, nickname= nickname)
    
    
    
    
    
    
    
    
    
    






if __name__ == "__main__":
    main()