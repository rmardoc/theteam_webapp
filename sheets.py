import streamlit as st
import random
from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
from chat import add_message
#from io import StringIO
import base64

@st.dialog("Character deletion")
def confirm_PGdeletion(room, pgname):
    st.write(f"Deleting Character {pgname} from room {room}. Character data will be lost")
    if st.button("Confirm deletion"):
        with server_state_lock["rooms"]:
            del server_state["rooms"][room]["pg"][pgname]
        st.rerun()

@st.dialog("Add Character")
def confirm_PGadd(room):
    def addPG():
        with server_state_lock["rooms"]:
            server_state["rooms"][room]["pg"][st.session_state.new_PG_name] = { }
    if st.text_input("Create new Character:", key="new_PG_name", placeholder="Name", on_change=addPG):
        st.rerun()

@st.dialog("Rename Character")
def confirm_PGrename(room,pgname):
    def renamePG():
        rename_newPGname = st.session_state.rename_new_PG_name
        pglist = server_state["rooms"][room]["pg"].keys()
        if (rename_newPGname == pgname) or (rename_newPGname in pglist):
            st.error(f"Invalid name. The name {rename_newPGname} is already present") 
            st.stop()
        else:
            with server_state_lock["rooms"]:
                server_state["rooms"][room]["pg"][rename_newPGname] = server_state["rooms"][room]["pg"][pgname]
                server_state["rooms"][room]["pg"].pop(pgname)
    if st.text_input(f"Renaming Character {pgname} in room {room}:", key="rename_new_PG_name", placeholder="New Character name", on_change=renamePG):
        st.rerun()

@st.dialog("Upload Character Image")
def confirm_PGimage(room,pgname):
    def uploadPGimage(inputimage):
        with server_state_lock["rooms"]:
            server_state["rooms"][room]["pg"][pgname]["trait_pgimage"] = inputimage
        st.rerun()
    uploaded_image = st.file_uploader("Upload image",type=['png','jpg'],accept_multiple_files=False)
    if uploaded_image:
        stringio_image = base64.b64encode(uploaded_image.read()).decode()
        uploadPGimage(stringio_image)


        

def create_container_with_color(id, color="#E4F2EC"):
    # todo: instead of color you can send in any css
    plh = st.container()
    html_code = """<div id = 'my_div_outer'></div>"""
    st.markdown(html_code, unsafe_allow_html=True)
    with plh:
        inner_html_code = """<div id = 'my_div_inner_%s'></div>""" % id
        plh.markdown(inner_html_code, unsafe_allow_html=True)
    ## applying style
    chat_plh_style = """
        <style>
            div[data-testid='stVerticalBlock']:has(div#my_div_inner_%s):not(:has(div#my_div_outer)) {
                background-color: %s;
                border-radius: 10px;
                padding: 2px;height:2px
            };
        </style>
        """
    chat_plh_style = chat_plh_style % (id, color)
    st.markdown(chat_plh_style, unsafe_allow_html=True)
    return plh

def theteamdiceroller(d6s,woundbet):
    def expldice(dice):
        somma=0
        results=[]
        while True:
            res = random.randint(1,dice)
            somma=somma+res
            results.append(res)
            if res != dice : break
        return somma,results
    def getbestres(lista):
        bestres=0
        lista_summed = [ sum(sublist)  for sublist in lista]
        for elem in lista_summed:
            if ( elem > bestres): 
                bestres = elem
        return bestres

    globalsum=0
    globalresults=[]
    somma , results = expldice(10)
    globalsum += somma
    globalresults.append(results)

    for elem in range(d6s): 
        somma, results = expldice(6)
        globalsum += somma
        globalresults.append(results)
    
    #st.write(f"globalresults: {globalresults}")
    globalresults_str = f"{globalresults}"
    globalbestres = getbestres(globalresults)
    if woundbet:
        globalsum = globalsum -2 
        globalresults_str+=" -2"
        globalbestres = globalbestres -2 
    return globalbestres, globalresults_str



def render_diceroller(room, pgname):
    def get_pool():
        poolstr="(1d10!"
        d6s=0
        woundbet=False
        for elem in ["bet_trait", "bet_resource", "bet_risk"]:
            if st.session_state[elem]:
                d6s+=1
        if d6s >0:
            poolstr+=f" , {d6s}d6! "
        if st.session_state["bet_wound"]:
            woundbet=True
            poolstr+=")K - 2"
        else: 
            poolstr+=")K"
        return poolstr,d6s,woundbet
    
    
    with stylable_container(
        key="container_with_redbgcolor",
        css_styles="""
            {
                vertical-align: middle;
                text-align: left;
                background-color: #DEBACA;
                padding-left: 5px;
                line-height: 0.3;
                border-radius: 10px
            }
            """,
    ):

        dicerol_col1, dicerol_col2 = st.columns([17,84], vertical_alignment="center")
        with dicerol_col1:
            tiradado = st.button("Tira i dadi")
        with dicerol_col2:
            poolstr, d6s, woundbet = get_pool()
            st.markdown(f"Stai tirando {poolstr}")
            if tiradado:
                result, resdices_str = theteamdiceroller(d6s=d6s, woundbet=woundbet) 
                st.markdown(f"**Risultato:**  :arrow_forward: :orange-background[{result}]  :arrow_backward: ; **Dadi:** {resdices_str}")
                add_message(room=room,message_packet={ "nickname": st.session_state.nickname, 
                                                       "text": f"**{pgname}** rolled {result} ; Dices: {resdices_str}" }
                    )








sheet_helpmessage="""
   - **Box bianchi:** Riempi i box grigi e checkbox bianchi per compilare la scheda. 
     Rimarranno salvati sul tuo PG in questa stanza per qualche giorno, fino al 
     riavvio del server (vedi "Download room" sulla sinistra)  
     **Creazione**: Inizi l'avventura con 6 Tratti (con un utilizzo ciascuno), 
     1 Risorsa con 2 utilizzi, e 1 Obiettivo. Inizi ogni sessione con 3 Jolly.
   - **Box rossi:** Selezionali quando componi la pool per il tiro di dado.
     (vedrai che la pool si comporrà in automatico).
     Clicca sul pulsante "Tira i dadi" quando sei pronto/a.
     Il risultato comparirà anche in chat. """



def render_sheet(room, pgname):

    def gettraitvalue(traitkey):
        try: 
            traitvalue = server_state["rooms"][room]["pg"][pgname][traitkey]
        except KeyError: 
            traitvalue = ""
        return traitvalue
    
    def updatetraitvalue():
        for traitkey in st.session_state:
            if traitkey.startswith("trait") or traitkey.startswith("bet"):
                with server_state_lock["rooms"]:
                    server_state["rooms"][room]["pg"][pgname][traitkey] = st.session_state[traitkey]


    pgname_col1, pgname_col2 = st.columns([70,30])
    with pgname_col1:
        st.markdown(f"### Scheda {pgname}", help=sheet_helpmessage)
            
        pgname_col1_2a, pgname_col1_2b = st.columns([2,8], vertical_alignment="center")
        with pgname_col1_2a: 
            st.markdown("Concept:")
        with pgname_col1_2b:
            st.text_input(f"Concept:", key=f"trait_concept", label_visibility="collapsed", 
                                      value= gettraitvalue(f"trait_concept"),
                                      on_change= updatetraitvalue )
        
    with pgname_col2:
        pgname_col2_1a, pgname_col2_1b = st.columns([65,35])
        with pgname_col2_1a: 
            if "trait_pgimage" in server_state["rooms"][room]["pg"][pgname]:
                pgimage = server_state["rooms"][room]["pg"][pgname]["trait_pgimage"]
                #st.image(server_state["rooms"][room]["pg"][pgname]["pgimage"], width=220 )
                st.markdown(f"""<img src="data:png;base64,{pgimage}" width='120' height='120' VSPACE="1">""", unsafe_allow_html=True)
            else: 
                pass
        with pgname_col2_1b: 
            if st.button(":material/add_photo_alternate: ", help="Upload an image "):
                confirm_PGimage(room,pgname)

    st.markdown(" ")
    col1, col2, col3, col4 , col5= st.columns([51,2, 60,2,39])

    with col1:
        col1a_1, col1a_2 = st.columns([48,52], vertical_alignment="center")
        with col1a_1:
            st.markdown("### Tratti")
        with col1a_2:
            with stylable_container(
                key="container_with_redbgcolor",
                css_styles="""
                    {
                        vertical-align: middle;
                        text-align: center;
                        background-color: #DEBACA;
                        padding-left: 5px;
                        border-radius: 10px
                    }
                    """,
            ):
                st.checkbox("+1d6", label_visibility="visible", key="bet_trait", help="+1d6 al tiro (se smarchi un utilizzo o spendi 1 Jolly)",
                            value= gettraitvalue(f"bet_trait") , on_change= updatetraitvalue)
        for i in range(6):
            
            col1_1, col1_2, col1_3 = st.columns([8,1,1])
            with col1_1:
                trait = st.text_input(f"Tratto {i}", key=f"trait_tr{i}", label_visibility="collapsed", 
                                      value= gettraitvalue(f"trait_tr{i}"),
                                      on_change= updatetraitvalue )
            with col1_2:
                st.checkbox("", label_visibility="collapsed", key=f"trait_tr{i}_1", 
                            value= gettraitvalue(f"trait_tr{i}_1") , on_change= updatetraitvalue)
            with col1_3:
                st.checkbox("", label_visibility="collapsed", key=f"trait_tr{i}_2", 
                            value= gettraitvalue(f"trait_tr{i}_2") , on_change= updatetraitvalue)

    with col2:
        pass
    with col3:
        #st.subheader("Risorse")
        col3a_1, col3a_2 = st.columns([5,5], vertical_alignment="center")
        with col3a_1:
            st.markdown("### Risorse")
        with col3a_2:
            with stylable_container(
                key="container_with_redbgcolor",
                css_styles="""
                    {
                        vertical-align: middle;
                        text-align: center;
                        background-color: #DEBACA;
                        padding-left: 5px;
                        border-radius: 10px
                    }
                    """,
            ):
                st.checkbox("+1d6", label_visibility="visible", key="bet_resource", help="+1d6 al tiro (se smarchi un utilizzo)",
                            value= gettraitvalue(f"bet_resource") , on_change= updatetraitvalue)
        for i in range(6):
            col2_1, col2_2, col2_3, col2_4 , col2_5 = st.columns([7,1,1,1,1])
            with col2_1:
                resource = st.text_input(f"Risorsa {i}", key=f"trait_res{i}", label_visibility="collapsed", 
                                         value= gettraitvalue(f"trait_res{i}"),
                                         on_change= updatetraitvalue)
            with col2_2:
                st.checkbox("", key=f"trait_res{i}_1", label_visibility="collapsed",
                            value= gettraitvalue(f"trait_res{i}_1") , on_change= updatetraitvalue)
            with col2_3:
                st.checkbox("", key=f"trait_res{i}_2", label_visibility="collapsed", 
                            value= gettraitvalue(f"trait_res{i}_2") , on_change= updatetraitvalue)
            with col2_4:
                st.checkbox("", key=f"trait_res{i}_3", label_visibility="collapsed",
                            value= gettraitvalue(f"trait_res{i}_3") , on_change= updatetraitvalue)
            with col2_5:
                st.checkbox("", key=f"trait_res{i}_4", label_visibility="collapsed",
                            value= gettraitvalue(f"trait_res{i}_4") , on_change= updatetraitvalue)

    with col4:
        pass

    with col5:
        st.markdown("### Rischiare")
        col5a_1 , col5a_2 = st.columns([2,9])
        with col5a_1:
            pass
        with col5a_2:
            with stylable_container(
                key="container_with_redbgcolor",
                css_styles="""
                    {
                        text-align: center;
                        background-color: #DEBACA;
                        padding-left: 5px;
                        border-radius: 10px
                    }
                    """,
            ):
                st.checkbox("+1d6 ", label_visibility="visible", key="bet_risk", help="+1d6 al tiro (ma se fallisci subisci 1 Ferita)",
                            value= gettraitvalue(f"bet_risk") , on_change= updatetraitvalue)

        st.subheader("Ferite")
        col5b_1 , col5b_2 = st.columns([2,9])
        with col5b_1:
            pass
        with col5b_2:
            with stylable_container(
                key="container_with_redbgcolor",
                css_styles="""
                    {
                        text-align: center;
                        background-color: #DEBACA;
                        padding-left: 5px;
                        border-radius: 10px
                    }
                    """,
            ):
                st.checkbox("-2 ", label_visibility="visible", key="bet_wound", help="-2 al tiro (ma se hai successo cancelli 1 Ferita)",
                            value= gettraitvalue(f"bet_wound") , on_change= updatetraitvalue)
        for i in range(3):
            col3b_1, col3b_2 = st.columns([9,1])
            with col3b_1: 
                st.text_input(f"Ferita {i}", key=f"trait_fer{i}", label_visibility="collapsed",
                              value= gettraitvalue(f"trait_fer{i}") , on_change= updatetraitvalue)
            with col3b_2:
                st.checkbox("", key=f"wound_{i}")

    col4, col5, col6, col7, col8 = st.columns([50,2,60,2,40])

    with col4:
        st.subheader("Obiettivo")
        st.text_area("Obiettivo",key=f"trait_obiettivo" , label_visibility="collapsed",
                     value= gettraitvalue(f"trait_obiettivo") , on_change= updatetraitvalue)

    with col5:
        pass
    with col6:
        st.subheader("Legami")
        col5_1, col5_2, col5_2b, col5_3, col5_4 = st.columns([55,9,1,55,9])
        col5_5, col5_6, col5_6b, col5_7, col5_8 = st.columns([55,9,1,55,9])

        with col5_1:
            st.text_input(f"Legame 1", key=f"trait_bon1", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon1") , on_change= updatetraitvalue)
        with col5_2:
            st.checkbox("", key=f"trait_bon1_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon1_1") , on_change= updatetraitvalue)
        with col5_2b:
            pass
        with col5_3:
            st.text_input(f"Legame 2", key=f"trait_bon2", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon2") , on_change= updatetraitvalue)
        with col5_4:
            st.checkbox("", key=f"trait_bon2_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon2_1") , on_change= updatetraitvalue)
        with col5_5:
            st.text_input(f"Legame 3", key=f"trait_bon3", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon3") , on_change= updatetraitvalue)
        with col5_6:
            st.checkbox("", key=f"trait_bon3_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon3_1") , on_change= updatetraitvalue)
        with col5_6b:
            pass
        with col5_7:
            st.text_input(f"Legame 4", key=f"trait_bon4", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon4") , on_change= updatetraitvalue)
        with col5_8:
            st.checkbox("", key=f"trait_bon4_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon4_1") , on_change= updatetraitvalue)


    with col7:
        pass

    with col8:
        st.subheader(" ")
        col6_1, col6_2, col6_3 = st.columns([10,35,65],vertical_alignment="center")
        col6_4, col6_5, col6_6 = st.columns([10,35,65],vertical_alignment="center")
        with col6_1:
            pass
        with col6_2:
            st.markdown("**PX**")
        with col6_3:
            st.text_input("PX",key="trait_px",label_visibility="collapsed",
                          value= gettraitvalue(f"trait_px") , on_change= updatetraitvalue)
        with col6_4:
            pass
        with col6_5:
            st.markdown("**Jolly**")
        with col6_6: 
            st.text_input("Jolly",key="trait_jolly",label_visibility="collapsed",
                          value= gettraitvalue(f"trait_jolly") , on_change= updatetraitvalue)


    # https://www.restack.io/docs/streamlit-knowledge-streamlit-column-background-color
    

    with st.expander("Notes"):
        st.text_area("Note",key=f"trait_note" , label_visibility="collapsed",
                 value= gettraitvalue(f"trait_note") , on_change= updatetraitvalue)

    render_diceroller(room=room, pgname=pgname)



def sheets(room):

    with st.container(border=True):


        pclist_col1, pclist_col2 , pclist_col3, pclist_col4 = st.columns([55,15,15,15])
        with pclist_col1:
            pglist = server_state["rooms"][room]["pg"].keys()
            if not pglist:
                st.write("No PCs available, create one.") 
                pgname = ""
            else: 
                pgname = st.radio("Select Character", pglist)

        with pclist_col2:
            if st.button(":material/person_add: \n\nAdd ", help= "Add new Character", use_container_width=True):
                confirm_PGadd(room)    
        with pclist_col3:
            if st.button(":material/person_cancel: \n\nDelete",help="Delete selected Character", use_container_width=True,disabled= not pglist):
                confirm_PGdeletion(room,pgname)
        with pclist_col4:
            if st.button(":material/person_edit: \n\nRename",help="Rename selected Character", use_container_width=True, disabled= not pglist):
                confirm_PGrename(room,pgname)




    if pgname:
        render_sheet(room=room, pgname=pgname)
    









if __name__ == "__main__":
    main()