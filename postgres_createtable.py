import streamlit as st
from sqlalchemy.sql import text
import settings
#conn = st.connection("postgresql", type="sql")

def create_tables():
    # Insert some data with conn.session.
    with settings.conn.session as s:
        # Creazione della tabella "messages"
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS messages (
                roomID INTEGER,
                nickname VARCHAR(255) NOT NULL,
                text TEXT NOT NULL,
                time TIMESTAMP NOT NULL
            );
        '''))

        # Creazione della tabella "rooms"
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS rooms (
                roomID SERIAL PRIMARY KEY,
                RoomName VARCHAR(255) NOT NULL
            );
        '''))
        
        # Creazione della tabella "pg"
        
        s.execute(text('''
            CREATE TABLE IF NOT EXISTS pg (
                pgID            SERIAL PRIMARY KEY,
                pgName          VARCHAR(255) NOT NULL,
                roomID          INTEGER      NOT NULL,
                trait_note      TEXT         DEFAULT '',
                trait_tr2_1     BOOLEAN      DEFAULT FALSE,
                trait_res4_2    BOOLEAN      DEFAULT FALSE,
                trait_res5_2    BOOLEAN      DEFAULT FALSE,
                trait_res4_4    BOOLEAN      DEFAULT FALSE,
                trait_res1      TEXT         DEFAULT '',
                trait_res2_2    BOOLEAN      DEFAULT FALSE,
                trait_bon1_1    BOOLEAN      DEFAULT FALSE,
                trait_tr1       TEXT         DEFAULT '',
                trait_res0_2    BOOLEAN      DEFAULT FALSE,
                trait_res5_3    BOOLEAN      DEFAULT FALSE,
                trait_fer0      TEXT         DEFAULT '',
                trait_res2_4    BOOLEAN      DEFAULT FALSE,
                trait_bon4      TEXT         DEFAULT '',
                trait_tr2       TEXT         DEFAULT '',
                trait_px        TEXT         DEFAULT '',
                trait_jolly     INTEGER      DEFAULT 3,
                bet_trait       BOOLEAN      DEFAULT FALSE,
                trait_res2_3    BOOLEAN      DEFAULT FALSE,
                bet_risk        BOOLEAN      DEFAULT FALSE,
                trait_bon4_1    BOOLEAN      DEFAULT FALSE,
                trait_tr3_1     BOOLEAN      DEFAULT FALSE,
                trait_res0_3    BOOLEAN      DEFAULT FALSE,
                trait_res0      TEXT         DEFAULT '',
                trait_tr3_2     BOOLEAN      DEFAULT FALSE,
                trait_res1_3    BOOLEAN      DEFAULT FALSE,
                trait_concept   TEXT         DEFAULT '',
                trait_tr5       TEXT         DEFAULT '',
                trait_tr1_1     BOOLEAN      DEFAULT FALSE,
                bet_wound       BOOLEAN      DEFAULT FALSE,
                trait_obiettivo TEXT         DEFAULT '',
                trait_res1_4    BOOLEAN      DEFAULT FALSE,
                trait_res2_1    BOOLEAN      DEFAULT FALSE,
                trait_res0_1    BOOLEAN      DEFAULT FALSE,
                bet_resource    BOOLEAN      DEFAULT FALSE,
                trait_res5_1    BOOLEAN      DEFAULT FALSE,
                trait_res4      TEXT         DEFAULT '',
                trait_tr0_1     BOOLEAN      DEFAULT FALSE,
                trait_bon1      TEXT         DEFAULT '',
                trait_res3_3    BOOLEAN      DEFAULT FALSE,
                trait_res5_4    BOOLEAN      DEFAULT FALSE,
                trait_res1_2    BOOLEAN      DEFAULT FALSE,
                trait_tr1_2     BOOLEAN      DEFAULT FALSE,
                trait_tr2_2     BOOLEAN      DEFAULT FALSE,
                trait_res3      TEXT         DEFAULT '',
                trait_res4_3    BOOLEAN      DEFAULT FALSE,
                trait_res3_2    BOOLEAN      DEFAULT FALSE,
                trait_res1_1    BOOLEAN      DEFAULT FALSE,
                trait_tr5_1     BOOLEAN      DEFAULT FALSE,
                trait_res3_4    BOOLEAN      DEFAULT FALSE,
                trait_res2      TEXT         DEFAULT '',
                trait_fer2      TEXT         DEFAULT '',
                trait_tr0_2     BOOLEAN      DEFAULT FALSE,
                trait_bon3_1    BOOLEAN      DEFAULT FALSE,
                trait_bon3      TEXT         DEFAULT '',
                trait_res4_1    BOOLEAN      DEFAULT FALSE,
                trait_res5      TEXT         DEFAULT '',
                trait_tr0       TEXT         DEFAULT '',
                trait_tr3       TEXT         DEFAULT '',
                trait_tr4_2     BOOLEAN      DEFAULT FALSE,
                trait_bon2_1    BOOLEAN      DEFAULT FALSE,
                trait_bon2      TEXT         DEFAULT '',
                trait_tr4       TEXT         DEFAULT '',
                trait_tr4_1     BOOLEAN      DEFAULT FALSE,
                trait_fer1      TEXT         DEFAULT '',
                trait_tr5_2     BOOLEAN      DEFAULT FALSE,
                trait_res0_4    BOOLEAN      DEFAULT FALSE,
                trait_res3_1    BOOLEAN      DEFAULT FALSE,
                trait_pgimage   TEXT         DEFAULT ''
            );
        '''))
        
        s.commit()


def sqlgetrooms():
    dfrooms = settings.conn.query('SELECT roomID, RoomName FROM rooms;', ttl="0m")
    return dfrooms

def sqlgetpgs(room ):
    dfrooms = sqlgetrooms()
    roomid = dfrooms[dfrooms["roomname"] == room]["roomid"].item()
    dfpgs = settings.conn.query('SELECT pgID, pgName, roomID FROM pg WHERE roomid = :roomID;', 
                                params={'roomID': roomid}, 
                                ttl="0m")
    return dfpgs.sort_values(by=['pgname'])


if __name__ == "__main__":
    create_tables()
