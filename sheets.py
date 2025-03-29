import streamlit as st
import random
#from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
from chat import sqladdmessages
#from io import StringIO
import base64
from sqlalchemy.sql import text
import settings
from postgres_createtable import sqlgetrooms, sqlgetpgs
import time


def sqlpgwriter(pgname, action, room, update_fields=None ):
    """
    Gestisce operazioni sulla tabella pg.
    
    Parametri:
    - pgname: nel caso di 'create' e 'remove' è il nome del PG 
              nel caso di 'update' è il nome attuale del pg.
    - action: azione da eseguire, deve essere 'create', 'remove' o 'update'.
    - room: il nome della stanza su cui aggiungere il PG
    - kwargs: dizionario contenente i campi da aggiornare sul PG (richiesto per 'update').
    """
    assert action in ['create', 'remove', 'update']
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
    dfpgs  = sqlgetpgs(room )

    if action == "create":
        with settings.conn.session as s:
            s.execute(
                text('INSERT INTO pg (pgname, roomID) VALUES (:pgname, :roomID);'),
                      params={'pgname': pgname, 'roomID': roomid})
            s.commit()
    elif action =="remove":
        pgid   = dfpgs[dfpgs["pgname"] == pgname]["pgid"].item()
        with settings.conn.session as s:
            s.execute(
                text('DELETE FROM pg WHERE pgID = :pgid;'), 
                params={'pgid': pgid} 
            )
            s.commit()
    elif action =="update":
        pgid   = dfpgs[dfpgs["pgname"] == pgname]["pgid"].item()
        # Assicurati che il nuovo nome sia fornito
        if not update_fields:
            raise ValueError("Per l'azione 'update' è necessario fornire almeno un campo da aggiornare.")
        # Verifica che tutte le chiavi in update_fields siano colonne valide
        invalid_columns = [key for key in update_fields if key not in sqlgettablecolumns('pg')]
        if invalid_columns:
            raise ValueError(f"Le seguenti colonne non sono valide: {', '.join(invalid_columns)} . Updtefields: {update_fields} ; acceptedcolumns: {str(sqlgettablecolumns('pg'))}  ")
        
        # esegui l'update
        with settings.conn.session as s:
            set_clause = ', '.join([f"{key} = :{key}" for key in update_fields])
            update_fields['pgid'] = pgid
            #for key, value in update_fields.items():
            query= f"UPDATE pg SET {set_clause} WHERE pgID = :pgid;"
            s.execute(text(query), params=update_fields )
            s.commit()


def sqlgettablecolumns(table):
    """ Ottiene i nomi delle colonne della tabella richiesta eseguendo una query """
    with settings.conn.session as s:
        result = s.execute(text('''
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = :tablename;
            '''), 
            params = {'tablename': table}
        )
        columns = [ elem[0] for elem in result.all() ]
        #columns = [row['column_name'] for row in result]
        return columns

def sqlgetpgdict(room,pgname):
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
    dfpg = settings.conn.query('SELECT * FROM pg WHERE pgname = :pgname AND roomid = :roomid ;', 
                                params={'pgname': pgname, 'roomid': roomid}, 
                                ttl="0m")
    # Verifica che il DataFrame contenga esattamente una riga
    assert dfpg.shape[0] == 1, f"Errore: trovato un numero diverso da uno di PG con pgname = {pgname}."
    # Converti la riga del DataFrame in un dizionario
    pg_dict = dfpg.iloc[0].to_dict()
    return pg_dict

@st.dialog("Character deletion")
def confirm_PGdeletion(room, pgname ):
    st.markdown(f"Deleting Character: '**{pgname}**' from room: '**{room}**'. Character data will be lost")
    if st.button("Confirm deletion"):
        sqlpgwriter(pgname=pgname, action='remove', room=room)
        st.rerun()

@st.dialog("Add Character")
def confirm_PGadd(room ):
    def addPG():
        if (st.session_state.new_PG_name in list(sqlgetpgs(room)["pgname"]) ):
            st.error(f"Invalid name. The name {st.session_state.new_PG_name} is already present") 
            st.stop()
        else:        
            sqlpgwriter(pgname=st.session_state.new_PG_name, action='create', room=room)
    if st.text_input("Create new Character:", key="new_PG_name", placeholder="Name", on_change=addPG):
        st.rerun()

@st.dialog("Rename Character")
def confirm_PGrename(room, pgname  ):
    def renamePG():
        rename_newPGname = st.session_state.rename_new_PG_name
        pglist = list(sqlgetpgs(room)["pgname"])
        if (rename_newPGname in pglist):
            st.error(f"Invalid name. The name {rename_newPGname} is already present") 
            st.stop()
        else:
            sqlpgwriter(pgname=pgname, action='update', room=room, update_fields={"pgname": rename_newPGname})
    if st.text_input(f"Renaming Character {pgname} in room {room}:", key="rename_new_PG_name", placeholder="New Character name", on_change=renamePG):
        st.rerun()

@st.dialog("Upload Character Image")
def confirm_PGimage(pgname, room  ):
    def uploadPGimage(inputimage):
        sqlpgwriter(pgname=pgname, action='update', room=room, update_fields={"trait_pgimage": inputimage})
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

def theteamdiceroller(d10s,woundbet):
    def rolldices(dicesize,dicenumber):
        """
        result lists of rolling 'dicenumber' dices of size 'dicesize'
        es: rolldices(10,3) = [4,2,10]
        """
        reslist = []
        for elem in range(dicenumber):
            res = random.randint(1,dicesize)
            reslist.append( res )
        return reslist

    if d10s > 0 : 
        reslist = rolldices(dicesize=10,dicenumber=d10s)
        bestres = max(reslist)
        reslist_str = f"{reslist}"
    else: 
        reslist = rolldices(dicesize=10,dicenumber=2)
        bestres = min(reslist)
        reslist_str = f"{reslist}"

    if woundbet: 
        bestres = bestres -2 
        reslist_str += " -2"

    return bestres, reslist_str





def render_diceroller(room , pgname ):
    def get_pool():
        d10s=0
        woundbet=False
        for elem in ["bet_trait", "bet_resource"]:
            if st.session_state[elem]:
                d10s+=1
        for elem in ["bet_risk"]:
            if st.session_state[elem]:
                d10s+=1
        poolstr=f"( {d10s}d10 "
        if st.session_state["bet_wound"]:
            woundbet=True
            poolstr+=")K - 2"
        else: 
            poolstr+=")K"
        return poolstr,d10s,woundbet
    
    
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
            poolstr, d10s, woundbet = get_pool()
            st.markdown(f"Stai tirando {poolstr}")
            if tiradado:
                result, resdices_str = theteamdiceroller(d10s=d10s, woundbet=woundbet) 
                st.markdown(f"**Risultato:**  :arrow_forward: :orange-background[{result}]  :arrow_backward: ; **Dadi:** {resdices_str}")
                sqladdmessages(room=room,message_packet={ "nickname": st.session_state.nickname, 
                                                       "text": f"**{pgname}** rolled {result} ; Dices: {resdices_str}",
                                                       "time": time.strftime("%Y%m%d %H:%M:%S")}
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



def render_sheet(room, pgname ):

    global pgdict 
    pgdict = sqlgetpgdict(room,pgname)

    def gettraitvalue(traitkey, pgdict= pgdict):
        assert traitkey in pgdict.keys(), f"Error: {traitkey} does not exists for pg {pgname}"
        return pgdict[traitkey]
    
    def updatetraitvalue(traitkey):
        pgdict[traitkey] = st.session_state[traitkey]
        sqlpgwriter(pgname=pgname, action='update', room=room, update_fields={traitkey: st.session_state[traitkey]})



    pgname_col1, pgname_col2 = st.columns([70,30])
    with pgname_col1:
        st.markdown(f"### Sheet {pgname}", help=sheet_helpmessage)
            
        pgname_col1_2a, pgname_col1_2b = st.columns([2,8], vertical_alignment="center")
        with pgname_col1_2a: 
            st.markdown("Concept:")
        with pgname_col1_2b:
            st.text_input(f"Concept:", key=f"trait_concept", label_visibility="collapsed", 
                                      value= gettraitvalue(f"trait_concept"),
                                      on_change= updatetraitvalue, 
                                      kwargs={'traitkey': "trait_concept"} )
        
    with pgname_col2:
        pgname_col2_1a, pgname_col2_1b = st.columns([65,35])
        with pgname_col2_1a: 
            if gettraitvalue("trait_pgimage") != "":
                pgimage = gettraitvalue("trait_pgimage")
                #st.image(server_state["rooms"][room]["pg"][pgname]["pgimage"], width=220 )
                st.markdown(f"""<img src="data:png;base64,{pgimage}" width='120' height='120' VSPACE="1">""", unsafe_allow_html=True)
            else: 
                pass
        with pgname_col2_1b: 
            if st.button(":material/add_photo_alternate: ", help="Upload an image "):
                confirm_PGimage(pgname=pgname, room=room)

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
                st.checkbox("+1d10", label_visibility="visible", key="bet_trait", help="+1d10 al tiro (se smarchi un utilizzo o spendi 1 Jolly)",
                            value= gettraitvalue(f"bet_trait") , on_change= updatetraitvalue, kwargs={'traitkey': f"bet_trait"})
        for i in range(6):
            
            col1_1, col1_2, col1_3 = st.columns([8,1,1])
            with col1_1:
                trait = st.text_input(f"Tratto {i}", key=f"trait_tr{i}", label_visibility="collapsed", 
                                      value= gettraitvalue(f"trait_tr{i}"),
                                      on_change= updatetraitvalue,
                                      kwargs={'traitkey': f"trait_tr{i}"} )
            with col1_2:
                st.checkbox(" ", label_visibility="collapsed", key=f"trait_tr{i}_1", 
                            value= gettraitvalue(f"trait_tr{i}_1") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_tr{i}_1"})
            with col1_3:
                st.checkbox(" ", label_visibility="collapsed", key=f"trait_tr{i}_2", 
                            value= gettraitvalue(f"trait_tr{i}_2") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_tr{i}_2"})

    with col2:
        pass
    with col3:
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
                st.checkbox("+1d10", label_visibility="visible", key="bet_resource", help="+1d10 al tiro (se smarchi un utilizzo)",
                            value= gettraitvalue(f"bet_resource") , on_change= updatetraitvalue, kwargs={'traitkey': "bet_resource"})
        for i in range(6):
            col2_1, col2_2, col2_3, col2_4 , col2_5 = st.columns([7,1,1,1,1])
            with col2_1:
                resource = st.text_input(f"Risorsa {i}", key=f"trait_res{i}", label_visibility="collapsed", 
                                         value= gettraitvalue(f"trait_res{i}"),
                                         on_change= updatetraitvalue,
                                         kwargs={'traitkey': f"trait_res{i}"})
            with col2_2:
                st.checkbox(" ", key=f"trait_res{i}_1", label_visibility="collapsed",
                            value= gettraitvalue(f"trait_res{i}_1") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_res{i}_1"})
            with col2_3:
                st.checkbox(" ", key=f"trait_res{i}_2", label_visibility="collapsed", 
                            value= gettraitvalue(f"trait_res{i}_2") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_res{i}_2"})
            with col2_4:
                st.checkbox(" ", key=f"trait_res{i}_3", label_visibility="collapsed",
                            value= gettraitvalue(f"trait_res{i}_3") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_res{i}_3"})
            with col2_5:
                st.checkbox(" ", key=f"trait_res{i}_4", label_visibility="collapsed",
                            value= gettraitvalue(f"trait_res{i}_4") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_res{i}_4"})

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
                st.checkbox("+1d10 ", label_visibility="visible", key="bet_risk", help="+1d10 al tiro (se fallisci subisci 1 Ferita, se hai successo ottieni +1 Jolly)",
                            value= gettraitvalue(f"bet_risk") , on_change= updatetraitvalue, kwargs={'traitkey': "bet_risk"})

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
                            value= gettraitvalue(f"bet_wound") , on_change= updatetraitvalue, kwargs={'traitkey': "bet_wound"})
        for i in range(3):
            col3b_1, col3b_2 = st.columns([9,1])
            with col3b_1: 
                st.text_input(f"Ferita {i}", key=f"trait_fer{i}", label_visibility="collapsed",
                              value= gettraitvalue(f"trait_fer{i}") , on_change= updatetraitvalue, kwargs={'traitkey': f"trait_fer{i}"})
            with col3b_2:
                st.checkbox(" ", key=f"wound_{i}")

    col4, col5, col6, col7, col8 = st.columns([50,2,60,2,40])

    with col4:
        st.subheader("Obiettivo")
        st.text_area("Obiettivo",key=f"trait_obiettivo" , label_visibility="collapsed",
                     value= gettraitvalue(f"trait_obiettivo") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_obiettivo"})

    with col5:
        pass
    with col6:
        st.subheader("Legami")
        col5_1, col5_2, col5_2b, col5_3, col5_4 = st.columns([55,9,1,55,9])
        col5_5, col5_6, col5_6b, col5_7, col5_8 = st.columns([55,9,1,55,9])

        with col5_1:
            st.text_input(f"Legame 1", key=f"trait_bon1", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon1") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon1"})
        with col5_2:
            st.checkbox(" ", key=f"trait_bon1_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon1_1") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon1_1"})
        with col5_2b:
            pass
        with col5_3:
            st.text_input(f"Legame 2", key=f"trait_bon2", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon2") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon2"})
        with col5_4:
            st.checkbox(" ", key=f"trait_bon2_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon2_1") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon2_1"})
        with col5_5:
            st.text_input(f"Legame 3", key=f"trait_bon3", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon3") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon3"})
        with col5_6:
            st.checkbox(" ", key=f"trait_bon3_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon3_1") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon3_1"})
        with col5_6b:
            pass
        with col5_7:
            st.text_input(f"Legame 4", key=f"trait_bon4", label_visibility="collapsed",
                          value= gettraitvalue(f"trait_bon4") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon4"})
        with col5_8:
            st.checkbox(" ", key=f"trait_bon4_1",label_visibility="collapsed",
                        value= gettraitvalue(f"trait_bon4_1") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_bon4_1"})


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
                          value= gettraitvalue(f"trait_px") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_px"})
        with col6_4:
            pass
        with col6_5:
            st.markdown("**Jolly**")
        with col6_6: 
            st.text_input("Jolly",key="trait_jolly",label_visibility="collapsed",
                          value= gettraitvalue(f"trait_jolly") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_jolly"})


    # https://www.restack.io/docs/streamlit-knowledge-streamlit-column-background-color
    

    with st.expander("Notes"):
        st.text_area("Note",key=f"trait_note" , label_visibility="collapsed",
                 value= gettraitvalue(f"trait_note") , on_change= updatetraitvalue, kwargs={'traitkey': "trait_note"})

    render_diceroller(room=room, pgname=pgname)



def sheets(room):


     
    with st.container(border=True):


        pclist_col1, pclist_col2 , pclist_col3, pclist_col4 = st.columns([55,15,15,15])
        with pclist_col1:
            pglist = list(sqlgetpgs(room)["pgname"])


            if not pglist:
                st.write("No PCs available, create one.") 
                st.session_state.selectedpgname = None
            else: 
                # Se la chiave non esiste ancora, la inizializziamo
                if "selectedpgname" not in st.session_state:
                    st.session_state.selectedpgname = pglist[0]
                selected_character  = st.radio("Select Character", pglist,
                                               index= pglist.index(st.session_state["selectedpgname"]) if st.session_state["selectedpgname"] in pglist else 0)
                # Controlliamo se l'utente ha scelto un PG diverso
                if selected_character != st.session_state.selectedpgname:
                    st.session_state.selectedpgname = selected_character
                    st.rerun()  # Ricarica la pagina solo se ho cambiato PG da visualizzare
                
                #st.rerun()

        with pclist_col2:
            if st.button(":material/person_add: \n\nAdd ", help= "Add new Character", use_container_width=True):
                confirm_PGadd(room)    
        with pclist_col3:
            if st.button(":material/person_cancel: \n\nDelete",help="Delete selected Character", use_container_width=True,disabled= not pglist):
                confirm_PGdeletion(room,st.session_state.selectedpgname)
        with pclist_col4:
            if st.button(":material/person_edit: \n\nRename",help="Rename selected Character", use_container_width=True, disabled= not pglist):
                confirm_PGrename(room,st.session_state.selectedpgname)




    if st.session_state.selectedpgname:
        render_sheet(room, pgname=st.session_state.selectedpgname)
    









if __name__ == "__main__":
    main()