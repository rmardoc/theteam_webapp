import streamlit as st
from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
from sheets import sheets
from chat import chat
from gamerules import gamerules
import json
import random



# TODO: 
# - creare una guida all'uso
# - testare nuovo chat widget
# - lingua inglese
# - export ed import delle room in JSON format


@st.dialog("Room deletion")
def confirm_roomdeletion(room):
    st.write(f"Deleting room {room}. Room data will be lost")
    if st.button("Confirm deletion"):
        with server_state_lock["rooms"]:
            del server_state["rooms"][room]
        st.rerun()

@st.dialog("Create a New Room")
def confirm_roomadd():
    def addroom(room_data):
        with server_state_lock["rooms"]:
            server_state["rooms"][st.session_state.new_room_name] = room_data
        #st.rerun()
    uploaded_file = st.file_uploader("**[OPTIONAL]** Re-upload room (from JSON file) ", accept_multiple_files=False,type="json")
    #st.markdown("To create a new empty room just name it")
    if uploaded_file is not None:
        room_data = json.load(uploaded_file)
    else: 
        room_data= { 'messages': [] , 'pg': {} }
    if st.text_input("New room name: ", key="new_room_name", placeholder="room name", 
                  on_change=addroom , kwargs=dict(room_data=room_data)):
        st.rerun()


@st.dialog("Rename Room")
def confirm_roomrename(room):
    def renameroom():
        rename_newname = st.session_state.rename_new_room_name
        rooms = server_state["rooms"].keys()
        if (rename_newname == room) or (rename_newname in rooms):
            st.error(f"Invalid name. The name {rename_newname} is already present") 
            st.stop()
        else:
            with server_state_lock["rooms"]:
                server_state["rooms"][st.session_state.rename_new_room_name] = server_state["rooms"][room] 
                server_state["rooms"].pop(room)
    if st.text_input(f"Renaming room {room} :", key="rename_new_room_name", placeholder="new room name", on_change=renameroom):
        st.rerun()

@st.dialog("Change Nickname")
def confirm_changenickname():
    def changenickname():
        rename_newnickname = st.session_state.new_nickname
        nickname = st.session_state.nickname
        if (rename_newnickname == nickname) :
            st.error(f"Invalid name. The name {rename_newnickname} is already present") 
            st.stop()
        else:
            st.session_state.nickname = rename_newnickname
    if st.text_input(f"Choose new nickname:", key="new_nickname", placeholder="new nickname", on_change=changenickname):
        st.rerun()


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

        if not rooms:
            st.sidebar.write("No rooms available, create one.") 
            room = ""
        else: 
            st.sidebar.markdown("#### Select Room:")
            room = st.sidebar.radio("Select room", rooms, key="room",label_visibility="collapsed")
            #if st.sidebar.button("Delete selected Room",use_container_width=True):
            #    confirm_roomdeletion(room)

        #with st.sidebar.form("CreateRoom", border=False):
        #    def on_create():
        #        new_room_name = st.session_state.new_room_name
        #        if new_room_name :
        #            with server_state_lock["rooms"]:
        #                server_state["rooms"][new_room_name] = { 'messages': [] , 'pg': {} }
        #    newroom_col1 , newroom_col2, = st.columns([2,3])
        #    with newroom_col1:
        #        st.text_input("Room name", label_visibility="collapsed", placeholder="room name", key="new_room_name")
        #    with newroom_col2:
        #        st.form_submit_button(":material/add_box: New room", on_click=on_create)
        #def on_create_room():
        #    new_room_name = st.session_state.new_room_name
        #    if new_room_name :
        #        with server_state_lock["rooms"]:
        #            server_state["rooms"][new_room_name] = { 'messages': [] , 'pg': {} }
        
        mngroom_col1, mngroom_col2, mngroom_col3 = st.sidebar.columns([33,33,33])
        with mngroom_col1:
            #with st.popover(":material/add_box: "):
            #    with st.form("CreateRoom", border=False):
            #        st.text_input("Room name", label_visibility="collapsed", placeholder="room name", key="new_room_name")
            #        st.form_submit_button("Create", on_click=on_create_room)
            if st.button(":material/add_box: \n\n Add ", help= "Add new room", use_container_width=True):
                confirm_roomadd()    
        with mngroom_col2:
            if st.button(":material/delete: Delete",help="Delete selected room", use_container_width=True, disabled=not rooms):
                confirm_roomdeletion(room)
        with mngroom_col3:
            if st.button(":material/replay: Rename",help="Rename selected room", use_container_width=True, disabled=not rooms):
                confirm_roomrename(room)
        #mngroom_col1b, mngroom_col2b = st.sidebar.columns([5,5])
        #with mngroom_col1b:
        if rooms:
            downloadjson_helpmsg='''
                Download selected room.  
                Rooms will be automatically removed from  
                the website when server reboots after few  
                days of inactivity. Download your room so  
                you can reupload it later.
                '''
            st.sidebar.download_button(":material/download: Download room", use_container_width=True,
                              help=downloadjson_helpmsg, 
                              file_name=f"theteam-rpg_room_{room}.json",mime="application/json", 
                              data=json.dumps(server_state["rooms"][room]))

   
            
    
    st.sidebar.divider()
    
    if "nickname" in st.session_state:
        nickname = st.session_state.nickname
    else:
        nickname = randomize_nickname()
        st.session_state.nickname = nickname

    nick_col1, nick_col2 = st.sidebar.columns([8,2],vertical_alignment="center")
    with nick_col1:
        st.markdown(f"**Nickname:** {nickname}")
    with nick_col2:
        if st.button(":material/account_circle:",help="Change nickname", use_container_width=False):
            confirm_changenickname()
    #with st.sidebar.form("ChangeName", border=False):
    #    def on_create():
    #        st.session_state.nickname = st.session_state.new_nickname
    #    st.markdown(f"Nickname : {nickname}")
    #    newnick_col1 , newnick_col2, = st.columns([2,3])
    #    with newnick_col1:
    #        st.text_input("New Nickname", label_visibility="collapsed", placeholder="new nickname", key="new_nickname")
    #    with newnick_col2:
    #        st.form_submit_button("Change Nickname", on_click=on_create)

    #st.sidebar.text_input("Nick name", key=f"newnickname")
    #nickname = st.session_state.nickname 

    st.sidebar.divider()
    st.sidebar.markdown("#### The Team")
    st.sidebar.markdown("Scarica il gioco completo gratuitamente (o con una donazione) da qui: https://richardmardoc.itch.io/theteam")





    st.markdown(
        """
        <style>
        button {
            height: auto;
            padding-top: 1px ;
            padding-bottom: 1px ;
            margin: 1px 1px 1px 1px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
    
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

    gamerules()


    with st.container(border=True):
        chat(room= room, nickname= nickname)
    

    
    
    
    
    
    
    
    






if __name__ == "__main__":
    main()