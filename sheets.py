import streamlit as st
import random

def sheets():
    st.title("Scheda Personaggio")

    col1, col2, col3, col4 , col5= st.columns([50,2, 60,2,40])

    with col1:
        st.subheader("Tratti")
        for i in range(6):
            
            col1_1, col1_2, col1_3 = st.columns([8,1,1])
            with col1_1:
                trait = st.text_input(f"Tratto {i+1}", label_visibility="collapsed")
            with col1_2:
                st.checkbox("", key=f"trait_{i}_1")
            with col1_3:
                st.checkbox("", key=f"trait_{i}_2")

    with col2:
        pass
    with col3:
        st.subheader("Risorse")
        for i in range(6):
            col2_1, col2_2, col2_3, col2_4 , col2_5 = st.columns([7,1,1,1,1])
            with col2_1:
                resource = st.text_input(f"Risorsa {i+1}", label_visibility="collapsed")
            with col2_2:
                st.checkbox("", key=f"resource_{i}_1")
            with col2_3:
                st.checkbox("", key=f"resource_{i}_2")
            with col2_4:
                st.checkbox("", key=f"resource_{i}_3")
            with col2_5:
                st.checkbox("", key=f"resource_{i}_4")

    with col4:
        pass

    with col5:
        st.subheader("Rischiare")
        col3a_1, col3a_2 = st.columns([9,1],vertical_alignment="center")
        with col3a_1:
            st.markdown("rischiare")
        with col3a_2:
            st.checkbox("Rischiare",key="rischiare",label_visibility="collapsed")
        st.subheader("Ferite")
        for i in range(3):
            col3b_1, col3b_2 = st.columns([9,1])
            with col3b_1: 
                st.text_input(f"Ferita {i+1}",label_visibility="collapsed")
            with col3b_2:
                st.checkbox("", key=f"wound_{i}")

    col4, col5, col6, col7, col8 = st.columns([50,2,60,2,40])

    with col4:
        st.subheader("Obiettivo")
        st.text_area("Obiettivo",label_visibility="collapsed")

    with col5:
        pass
    with col6:
        st.subheader("Legami")
        col5_1, col5_2, col5_2b, col5_3, col5_4 = st.columns([55,9,1,55,9])
        col5_5, col5_6, col5_6b, col5_7, col5_8 = st.columns([55,9,1,55,9])

        with col5_1:
            st.text_input(f"Legame 1",label_visibility="collapsed")
        with col5_2:
            st.checkbox("", key=f"bond_1")
        with col5_2b:
            pass
        with col5_3:
            st.text_input(f"Legame 2",label_visibility="collapsed")
        with col5_4:
            st.checkbox("", key=f"bond_2")
        with col5_5:
            st.text_input(f"Legame 3",label_visibility="collapsed")
        with col5_6:
            st.checkbox("", key=f"bond_3")
        with col5_6b:
            pass
        with col5_7:
            st.text_input(f"Legame 4",label_visibility="collapsed")
        with col5_8:
            st.checkbox("", key=f"bond_4")


    with col7:
        pass

    with col8:
        st.subheader(" ")
        col6_1, col6_2 = st.columns([3,7],vertical_alignment="center")
        col6_3, col6_4 = st.columns([3,7],vertical_alignment="center")
        with col6_1:
            st.write("PX")
        with col6_2:
            st.text_input("PX",label_visibility="collapsed")
        with col6_3:
            st.write("Jolly")
        with col6_4: 
            st.text_input("Jolly",label_visibility="collapsed")


    if st.button("Tira il dado"):
        result = random.randint(1, 6)
        st.write(f"Risultato del tiro: {result}")

    # https://www.restack.io/docs/streamlit-knowledge-streamlit-column-background-color
    


if __name__ == "__main__":
    main()