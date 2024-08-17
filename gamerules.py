import streamlit as st
import random
from streamlit_server_state import server_state, server_state_lock
from streamlit_extras.stylable_container import stylable_container
from chat import add_message
import markdown

    

def gamerules():

    rules_column1 = """ 
        ##### Giocatore:
        Tiri: Diff = 1 Successo; Diff + 5 = 2 Successi.
        - **Azione di Affrontare:**
            1° Successo = infliggi 1 Danno o smarca 1 SlotImpresa
            2° Successo = infliggi +1 Danno/Slot o ottieni 1 Jolly
        - **Azione di Focus:**
            Domanda al GM : Cosa c'è qui che posso usare a nostro vantaggio?  
            1 Successo = 1 Jolly ; 2 Successi = 2 Jolly
        .
        - **Jolly Boost:**
            Dopo il Tiro di un Alleato spendi 1 Jolly per dargli un +2 
        - **Jolly Combo:** 
            Dopo una tua azione, metti 1 Jolly sul tavolo. Se il prossimo alleato agisce sfruttando la tua azione prende +2 per ogni Jolly sul tavolo (max +4)
        .
        ##### Riposo:
        Una volta al giorno, in un Momento Tranquillo decidi se spendere:
        - 1 PX - **Riposare:** riposando per qualche ora ripristini tutti gli usi dei Tratti 
        - 3 PX - **Curare:** 1 Ferita di un alleato.
        - 1 PX - **Attrezzarsi:** otteni due slot di Risorse (max 4) se il GM approva. 
        - 1 PX - **Cambiare:** sostituisci un Tratto.
        - 6 PX - **Migliorare:** +1 uso di 1 Tratto (max 2)
        - 0 PX - **Legare:** Fai una domanda ad un alleato e ascolti la risposta, entrambi segnate un Legame.
        .
        ##### Stringi i denti:
        Descrivi come una Ferita ti intralcia nell'Azione e Tira con malus -2.  Successo: cancella la ferita. 
        """
    rules_column1b = """ 
        ##### GIOCATORE:
        Tiri: 1d10 [+1d6 per Tratti] [+1d6 per Risorse]
        [+1d6 per Rischiare] [-2 per Ferite (vedi 'Stringi i denti')]  
        I dadi esplodono, scegli il migliore.
        
        Difficoltà: da 7 a 12  
        Risultato: Diff = 1 Successo; Diff + 5 = 2 Successi.
        
        - **Azione di Affrontare:**  
          1° Successo = infliggi 1 Danno o smarca 1 SlotImpresa  
          2° Successo = infliggi +1 Danno/Slot o ottieni 1 Jolly  
        - **Azione di Focus:**  
          Ottenere un vantaggio, informazioni o tempismo contro la minaccia.  
          Domanda al GM : Cosa c'è qui che posso usare a nostro vantaggio?  
          1 Successo = 1 Jolly ; 2 Successi = 2 Jolly  
        - **Jolly Boost:**  
          Dopo il Tiro di un Alleato spendi 1 Jolly per dargli un +2  
        - **Jolly Combo:**  
          Dopo una tua azione, metti 1 Jolly sul tavolo e descrivi come prepari
          il terreno. Se il prossimo alleato agisce sfruttando la tua azione,
          prende +2 per ogni Jolly sul tavolo (max +4)
        
        ##### RIPOSO:
        Una volta al giorno, in un Momento Tranquillo decidi se spendere:
        - 1 PX - **Riposare:** riposa per qualche ora, ripristini tutti gli usi dei Tratti
        - 3 PX - **Curare:** 1 Ferita di un alleato.
        - 1 PX - **Attrezzarsi:** otteni due slot di Risorse (max 6) se il GM approva.
        - 1 PX - **Cambiare:** sostituisci un Tratto.
        - 6 PX - **Migliorare:** +1 uso di 1 Tratto (max 2)
        - 0 PX - **Legare:** Fai una domanda ad un alleato e ascolti la risposta,
        entrambi segnate un Legame.
        """
    rules_column2 = """
        ##### Legami:
        Smarca uno e prendi il controllo di quell'Alleato per un'azione come se avesse speso un Tratto ed una Risorsa (quindi +2d6)

        ##### Fine Sessione:
        - **Esperienza:** Ottieni 1 PX , +1PX per ogni risposta positiva: 
            1. Hai messo in luce un tuo Tratto Primario o il tuo Obiettivo?
            2. Ti sei messo in pericolo per il bene del Team?
            3. E' cambiato il tuo rapporto con un alleato? Come?  
        
        - **Chi sei per noi:** Assegna un Tratto ad un alleato (che lo sostituisce ad uno dei propri)

        ##### GM:
          - **Pericolo:** Tu o un alleato agite subito per evitare un pericolo o subirete 1 Ferita.  
          - **Debuff:** Perdi tutti o alcuni utilizzi di uno o più Risorse Consumabili.
          - **Complicazione:** + problemi sulla scena: cambia luogo o tipo di sfida, aumenta numero o pericolosità dei nemici, alcune azioni sono più difficili, appaiono nuovi pericoli. 
          - **Conclusione amara:** la scena si chiude in un modo diverso (peggiore) di quello sperato. 
          - **Scelta difficile:** il GM offre al Giocatore una scelta difficile fra 2 diverse Mosse del GM.

        > Scarica il gioco completo gratuitamente (o con una donazione) da qui: https://richardmardoc.itch.io/theteam
        """    
    rules_column2b = """
    
        ##### STRINGI:
        Descrivi come una Ferita ti intralcia nell'Azione e Tira con malus -2.
        Successo: cancella la ferita.

        ##### LEGAMI:
        Smarca uno e prendi il controllo di quell'Alleato per un'azione come se
        avesse speso un Tratto ed una Risorsa (quindi +2d6). Se l'altro
        Giocatore approva l'azione, entrambi ottenete +1 Jolly
        
        ##### FINE SESSIONE:
        - **Esperienza:** Ottieni 1 PX , +1PX per ogni risposta positiva:
          1. Hai messo in luce il tuo Tratto Primario o il tuo Obiettivo?
          2. Ti sei messo in pericolo per il bene del Team?
          3. E' cambiato il tuo rapporto con un alleato? Come?
        - **Chi sei per noi:** Assegna un Tratto ad un alleato (che lo sostituisce ad
        uno dei propri)
        
        ##### GM:
        - **Pericolo:** Tu o un alleato agite subito per evitare un pericolo o subirete 1 Ferita.
        - **Debuff:** Perdi tutti o alcuni utilizzi di uno o più Risorse Consumabili.
        - **Complicazione:** + problemi sulla scena: Cambia luogo o tipo di sfida.
        Aumenta numero o pericolosità dei nemici o la difficoltà di alcuni
        approcci. Compaiono nuovi pericoli, verità scomode o opportunità ad
        un costo. Gli alleati potrebbero dividersi o perdere tempo.
        - **Conclusione amara:** la scena si chiude in un modo diverso
        (peggiore) di quello sperato.
        - **Scelta difficile:** il GM offre al Giocatore una scelta difficile fra 2
        diverse Mosse del GM.

        > Scarica il gioco completo gratuitamente (o con una donazione) da qui: https://richardmardoc.itch.io/theteam
        """
    
    with st.expander("Game rules"):
        with stylable_container(
            key="container_with_greenbgcolor",
            css_styles="""
                {
                    vertical-align: top;
                    text-align: left;
                    background-color: #E4F2EC;
                    padding-left: 5px;
                    line-height: 0.9;
                    text-size-adjust: 50%;
                    font-size:12px;
                    border-radius: 10px
                }
                """,
        ):
            rules_col1, rules_col2 = st.columns([5,5])
            with rules_col1:
                #with stylable_container(
                #    key="container_with_greenbgcolor",
                #    css_styles="""
                #        {
                #            vertical-align: top;
                #            text-align: left;
                #            background-color: #E4F2EC;
                #            padding-left: 5px;
                #            line-height: 0.8;
                #            text-size-adjust: 10%;
                #            font-size:12px;
                #            border-radius: 10px
                #        }
                #        """,
                #):
                    #st.markdown('<span style="font-size: 8px;">',unsafe_allow_html=True)
                    #st.markdown('<div style="font-size: 8px;"> '+markdown.markdown(rules_column1)+' </div>', unsafe_allow_html=True)
                    #st.markdown('<style> body{font-size: 8px;} html{font-size: 8px;} </style> ', unsafe_allow_html=True)
                    #st.markdown(rules_column1, unsafe_allow_html=True)
                st.markdown(rules_column1b)
                    #st.markdown('</span>',unsafe_allow_html=True)
                    #st.markdown("""<style>.big-font {color:red;font-size:8px;}</style><div class='big-font'>""", unsafe_allow_html=True)
                    #st.markdown("""<style>.big-font {color:red;font-size:13px;}</style>""", unsafe_allow_html=True)
                    #st.markdown("""<div class='big-font'>"""+markdown.markdown(rules_column1)+"""</div>""",unsafe_allow_html=True)
                    #st.markdown("""</div>""", unsafe_allow_html=True)
                    #st.markdown('<style>h6{font-size:13px;line-height:0.8;margin-top:-15px;margin-bottom:-20px;}</style>', unsafe_allow_html=True) 
                    #st.markdown(rules_column1_h6)
            with rules_col2:
                st.markdown(rules_column2b)






if __name__ == "__main__":
    main()