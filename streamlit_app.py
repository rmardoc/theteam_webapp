import streamlit as st
#from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
from sheets import sheets
from chat import render_chat
from gamerules import gamerules
from postgres_createtable import sqlgetrooms
import json
import random
from sqlalchemy.sql import text
import settings


# TODO: 
# - creare una guida all'uso
# - testare nuovo chat widget
# - lingua inglese





def sqlroomwriter(room, action, newname=""):
    """
    Gestisce operazioni sulla tabella rooms.
    
    Parametri:
    - room: nel caso di 'create' e 'remove' è il nome della stanza;
            nel caso di 'rename' è il nome attuale della stanza.
    - action: azione da eseguire, deve essere 'create', 'remove' o 'rename'.
    - newname: nuovo nome della stanza (richiesto per 'rename').
    """
    assert action in ['create', 'remove', 'rename']
    if action == "create":
        with settings.conn.session as s:
            s.execute(
                text('INSERT INTO rooms (RoomName) VALUES (:roomname);'),
                params={'roomname': room}
            )
            s.commit()

    elif action =="remove":
        dfrooms = sqlgetrooms()
        roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
        with settings.conn.session as s:
            # Prima rimuovi i personaggi e i messaggi collegati alla stanza
            s.execute(
                text('DELETE FROM pg WHERE roomID = :roomid;'),
                params={'roomid': roomid}
            )
            s.execute(
                text('DELETE FROM messages WHERE roomID = :roomid;'),
                params={'roomid': roomid}
            )
            # Ora rimuovi la stanza
            s.execute(
                text('DELETE FROM rooms WHERE RoomName = :roomname;'),
                params={'roomname': room}
            )
            s.commit()

    elif action =="rename":
        # Assicurati che il nuovo nome sia fornito
        if not newname:
            raise ValueError("Per l'azione 'rename' è necessario specificare il nuovo nome tramite il parametro newname")
        with settings.conn.session as s:
            s.execute(
                text('UPDATE rooms SET RoomName = :newname WHERE RoomName = :roomname;'),
                params={'newname': newname, 'roomname': room}
            )
            s.commit()




def getdownloadroomdata(room):
    """Scarica tutte le informazioni relative a una stanza, inclusi i personaggi e i messaggi."""
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
    # Scarica i dettagli della stanza
    room_data = settings.conn.query('SELECT * FROM rooms WHERE roomid = :roomid ;', 
                                params={'roomid': roomid}, 
                                ttl="0m")
    # Scarica tutti i personaggi della stanza
    pg_data = settings.conn.query('SELECT * FROM pg WHERE roomid = :roomid ;', 
                                params={'roomid': roomid}, 
                                ttl="0m")
    # Scarica tutti i messaggi della stanza
    msg_data = settings.conn.query('SELECT * FROM messages WHERE roomid = :roomid ;', 
                                params={'roomid': roomid}, 
                                ttl="0m")
    msg_data['time'] = msg_data['time'].astype(str)
    result = {
        "rooms": room_data.to_dict(orient="records") ,
        "characters": pg_data.to_dict(orient="records"),
        "messages": msg_data.to_dict(orient="records")
    }

    return result


def sqlimportroom(room, roomdata):
    """Importa una stanza dal JSON nel database"""       
    # Inserisci la stanza nel database
    with settings.conn.session as s:
        s.execute(text('INSERT INTO rooms (roomname) VALUES (:roomname) RETURNING roomid;'),
                          params={'roomname': room} )
        s.commit()
        print(f"inserita stanza {room}")
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()

    with settings.conn.session as s:
        # Inserisci i personaggi associati
        if len(roomdata["characters"]) >= 1: 
            for character in roomdata["characters"]:
                character["roomid"] = roomid
                character.pop("pgid")  # rimuovo il pgid perché potrebbe esistere già, devo crearne uno nuvo
                valuesstring = ', '.join(f":{col}" for col in list(character.keys()) ) 
                query= f" INSERT INTO pg ({', '.join(list(character.keys()))}) VALUES ({valuesstring});"
                s.execute(text(query), params=character)

        # Inserisci i messaggi associati
        if len( roomdata["messages"]) >= 1:
            for message in roomdata["messages"]:
                message["roomid"] = roomid
                s.execute(text('INSERT INTO messages (nickname, text, time, roomid) VALUES (:nickname, :text, :time, :roomid);'),
                          params=message )
        s.commit()
    

@st.dialog("Room deletion")
def confirm_roomdeletion(room):
    st.write(f"Deleting room '**{room}**'. All this room's data (Characters and Messages) will be lost")
    if st.button("Confirm deletion"):
        sqlroomwriter(room=room, action='remove')
        st.rerun()
    

@st.dialog("Create a New Room")
def confirm_roomadd():
    def addroom(room_data):
        if (st.session_state.new_room_name in list(sqlgetrooms()["roomname"]) ):
            st.error(f"Invalid name. The name {st.session_state.new_room_name} is already present") 
            st.stop()
        elif not room_data:
            #with server_state_lock["rooms"]:
            #    server_state["rooms"][st.session_state.new_room_name] = room_data
            sqlroomwriter(room=st.session_state.new_room_name, action='create')
            st.rerun()
        else: 
            sqlimportroom(room=st.session_state.new_room_name, roomdata=room_data)
            #st.session_state.dfrooms = sqlgetrooms()
            st.rerun()
    uploaded_file = st.file_uploader("**[OPTIONAL]** Re-upload room (from JSON file) ", accept_multiple_files=False,type="json")
    #st.markdown("To create a new empty room just name it")
    if uploaded_file is not None:
        room_data = json.load(uploaded_file)
    else: 
        room_data= {}
    if st.text_input("New room name: ", key="new_room_name", placeholder="room name", 
                  on_change=addroom , kwargs=dict(room_data=room_data)):
        st.rerun()


@st.dialog("Rename Room")
def confirm_roomrename(room):
    def renameroom():
        rename_newname = st.session_state.rename_new_room_name
        if (rename_newname in list(sqlgetrooms()["roomname"]) ):
            st.error(f"Invalid name. The name {rename_newname} is already present") 
            st.stop()
        else:
            sqlroomwriter(room=room, action='rename', newname=st.session_state.rename_new_room_name)
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

    settings.init()

    def randomize_nickname():
        with open("data/animals.json") as f:
            animals = json.load(f)
        with open("data/adjectives.json") as f:
            adjectives = json.load(f)
        name = f"{random.choice(adjectives)}_{random.choice(animals)}"
        return name

    ## loading variables
    st.session_state.dfrooms = sqlgetrooms()

    
 
    ## sidebar
    with st.sidebar.container(border=False):
        if st.session_state.dfrooms['roomname'].empty:
            st.sidebar.write("No rooms available, create one.") 
            st.session_state.selectedroom = ""
        else: 
            st.sidebar.markdown("#### Select Room:")
            st.session_state.selectedroom = st.sidebar.radio("Select room", st.session_state.dfrooms['roomname'], key="room",label_visibility="collapsed")

        mngroom_col1, mngroom_col2, mngroom_col3 = st.sidebar.columns([33,33,33])
        with mngroom_col1:
            if st.button(":material/add_box: \n\n Add ", help= "Add new room", use_container_width=True):
                confirm_roomadd()    
        with mngroom_col2:
            if st.button(":material/delete: Delete",help="Delete selected room", use_container_width=True, disabled=st.session_state.dfrooms['roomname'].empty):
                confirm_roomdeletion(st.session_state.selectedroom)
        with mngroom_col3:
            if st.button(":material/replay: Rename",help="Rename selected room", use_container_width=True, disabled=st.session_state.dfrooms['roomname'].empty):
                confirm_roomrename(st.session_state.selectedroom)
        if not st.session_state.dfrooms['roomname'].empty:
            downloadjson_helpmsg='''
                Download selected room.  
                Rooms will be automatically removed from  
                the website when server go in sleep mode   
                after 30 min of inactivity. Download your  
                room so you can reupload it later.
                '''
            st.sidebar.download_button(":material/download: Download room", use_container_width=True,
                              help=downloadjson_helpmsg, 
                              file_name=f"theteam-rpg_room_{st.session_state.selectedroom}.json",mime="application/json", 
                              data=json.dumps( getdownloadroomdata(st.session_state.selectedroom) ) 
                              )
    

            
    
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
    
    if st.session_state.dfrooms['roomname'].empty:
        st.stop()
    

    
    
    
    ## mainframe check nickname or stop rendering
    if not nickname:
        st.warning("Set your nick name on the left.")
        st.stop()
    
    

    with st.container(border=True):
        sheets(st.session_state.selectedroom)

    gamerules()


    with st.container(border=True):
        render_chat(room= st.session_state.selectedroom, nickname= nickname)
    

    
    
    
    
    
    
    
    






if __name__ == "__main__":
    main()