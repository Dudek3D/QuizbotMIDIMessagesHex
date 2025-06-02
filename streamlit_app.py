import streamlit as st
import json
import os
import sys
from openai import OpenAI

# Importazioni moduli interni
sys.path.append(os.path.join(os.path.dirname(__file__), 'management'))
from AccountManager import AccountManager as amc
am=amc()

def printl(tuple):
    print(tuple[1])
    print("con esito: "+str(tuple[0]))
    return tuple

# Chiave API OpenAI
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Inizializza stato
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "view" not in st.session_state:
    st.session_state.view = "welcome"  # welcome | login | register

# Funzione interfaccia di accesso
def login_view():
    st.header("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if printl(am.verify_login(username, password))[0]:
            st.session_state.logged_in = True
            st.success("Login effettuato!")
        else:
            st.error("Credenziali non valide")

# Funzione interfaccia di registrazione
def register_view():
    st.header("📝 Registrazione")
    username = st.text_input("Nuovo Username")
    password = st.text_input("Nuova Password", type="password")
    email = st.text_input("Email")
    activation_key = st.text_input("Chiave di attivazione")
    if st.button("Registrati"):
        if printl(am.create_account(username, password, email, activation_key))[0]:
            st.success("Account creato! Ora puoi fare il login.")
            st.session_state.view = "login"
        else:
            st.error("Chiave di attivazione non valida o utente esistente.")

# Finestra iniziale
if not st.session_state.logged_in:
    st.title("🎹 MIDI Message Quiz (hex) - Accesso")
    st.write("Benvenuto! Fai login oppure registrati per iniziare.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.session_state.view = "login"
    with col2:
        if st.button("Registrati"):
            st.session_state.view = "register"

    if st.session_state.view == "login":
        login_view()
    elif st.session_state.view == "register":
        register_view()

    st.stop()

# SEZIONE ATTIVA SOLO DOPO IL LOGIN

# Titolo e descrizione
st.title("🎹 MIDI Message Quiz (hex)")
st.write(
    "[ENG] This is a chatbot that uses OpenAI's GPT-3.5 model to generate 10 questions asking you random MIDI messages written in hexadecimal code.  \n"
    "[ITA] Questo è un chatbot che utilizza il modello GPT-3.5 di OpenAI per generare 10 domande riguardo messaggi MIDI casuali scritti in codice esadecimale."
)

# Stato chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizza messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input chat
if prompt := st.chat_input("Scrivi un messaggio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
