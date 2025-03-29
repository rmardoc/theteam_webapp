import streamlit as st
#from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
import time
import settings
from sqlalchemy.sql import text
from postgres_createtable import sqlgetrooms, sqlgetpgs

def sqlgetmessages(room ):
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
    dfmsgs = settings.conn.query('SELECT roomID, nickname, text, time FROM messages WHERE roomid = :roomID;', 
                                params={'roomID': roomid}, 
                                ttl="0m")
    return dfmsgs


def sqladdmessages(room , message_packet = None):
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
    with settings.conn.session as s:
        s.execute(
            text('INSERT INTO messages (roomID, nickname, text, time) VALUES (:roomID, :nickname, :text, :time );'),
                  params={'roomID': roomid, 
                          'nickname': message_packet['nickname'], 
                          'text': message_packet['text'] , 
                          'time': message_packet['time']})
        s.commit()    
    st.write("")

def render_chat(room , nickname ):

    #room_key = f"room_{room}"
    
    ## main frame functions
    def on_message_input(text, room=room, nickname=nickname):
        #new_message_text = st.session_state[message_input_key]
        if not text:
            return
        new_message_packet = {
            "nickname": nickname,
            "text": text,
            "time": time.strftime("%Y%m%d %H:%M:%S")
        }
        sqladdmessages(room= room, message_packet= new_message_packet)
        st.session_state["messages_updated"] = True  
        #st.session_state.messagesdf = sqlgetmessages(room)
        #st.write("")
        
        
    
    
    
    st.markdown("""
    <style>
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        border-top: 1px solid #ddd;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    .text-input {
        flex: 1;
        padding: 10px;
        margin-right: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .btn {
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .btn-icon {
        background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABTUlEQVQ4T9WTTUoDQRSGn5mYhmDoo4QXgiIo7+BgsiBoeAI8gCH8Av4Cc4gIIZIggJJ4EUtLA+4QvYBxeYi5cmzPvEGJs7A/N2ds7s7DvdnHg7hKp3uDgWGbAot9awNQH4l04aGM2vQBtRNmGEPLQbGFynKsZgmS5cAql4lPjDCTocTXQCTPxOXQDbAkcCJoDqx5ukEu4BlwnfNN3YoUeIlG1cZK3wqCpQrsQRsoxfQZPIvZ8qP2HIn5RbmCB99CAUyIxSAI1J/A5Mj3A9rO4hncPFTMLBqkD35DCPFEYgj+ndlfPQyAizIg6C1AqsFlMxxQ4VAV8Hs1qvDJW+dQtR1pnbYUyN5kQddcfWSu+g3O0mWoBD+Of4EFZyTSvhq8uZPtYFiv/L4isQtmcivgH6Sfhs4wKxDHYNe95QTmSAAAAAElFTkSuQmCC') no-repeat center center;
        background-size: contain;
        width: 24px;
        height 24px;
        border: none;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    
    #st.header(f"Room: {room}")
    
    ## mainframe check nickname or stop rendering
    if not nickname:
        st.warning("Set your nick name on the left.")
        st.stop()
    
    
    
    
    ## mainframe show chat

    
    with stylable_container(
            key="container_with_nouppermargin",
            css_styles="""
                {
                    text-align: left;
                    line-height: 1;
                    margin-top: -25px;
                    margin-bottom: -85px;
                    padding-left: 5px;
                    border-radius: 10px
                }
                """,
        ):
        st.markdown("Chat:")
    
    with st.container(height=300):
        with st.form("chatmessage", clear_on_submit=True, border=False):
            chat_col1 , chat_col2, = st.columns([8,1])
            ## mainframe define message
            with chat_col1:
                #message_input_key = f"message_input_{room}"
                st.text_input("Message", label_visibility="collapsed", key="message_input" )
            with chat_col2:
                if st.form_submit_button("Send"):
                    on_message_input(st.session_state.message_input, room, nickname)
                #st.form_submit_button("Send", on_click=on_message_input, 
                #                      kwargs={'room': room , 'text': st.session_state.message_input, 'nickname' : nickname })
            
    
        st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
        #st.markdown( f"messagestring: {sqlgetmessages(room ).to_string()}" )
        messagesdf = sqlgetmessages(room)
        if not messagesdf.empty:
            #st.markdown(f" messagedf:  {messagesdf}  ")
            for index, elem in messagesdf.sort_values(by=['time'], ascending=False).iterrows():
                #for elem in messagesdf.iterrows(): 
                #pass
                st.markdown(f"{elem['time']} **[{elem['nickname']}]** : {elem['text']}")
        st.markdown('</div>', unsafe_allow_html=True)




##TODO: try stateful chat: https://arnaudmiribel.github.io/streamlit-extras/extras/stateful_chat/

if __name__ == "__main__":
    main()


