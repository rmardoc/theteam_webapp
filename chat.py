import streamlit as st
from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container


def add_message(room, message_packet):
    with server_state_lock["rooms"]:
        server_state["rooms"][room]['messages'].append( message_packet )

def chat(room, nickname):

    #room_key = f"room_{room}"
    
    ## main frame functions
    def on_message_input():
        new_message_text = st.session_state[message_input_key]
        if not new_message_text:
            return
        new_message_packet = {
            "nickname": nickname,
            "text": new_message_text,
        }
        add_message(room= room, message_packet= new_message_packet)
    
    
    
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
                message_input_key = f"message_input_{room}"
                st.text_input("Message", label_visibility="collapsed", key=message_input_key )
            with chat_col2:
                st.form_submit_button("Send", on_click=on_message_input)
            
    
        st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
        for elem in  reversed(server_state["rooms"][room]['messages'] ): 
            st.markdown(f"**[{elem['nickname']}]** : {elem['text']}")
        st.markdown('</div>', unsafe_allow_html=True)




if __name__ == "__main__":
    main()


