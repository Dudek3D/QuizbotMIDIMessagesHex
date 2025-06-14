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
    if st.button("Login", key="login_btn"):
        if printl(am.verify_login(username, password))[0]:
            st.session_state.logged_in = True
            st.session_state.username = username
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
    if st.button("Registrati", key="register_btn"):
        if printl(am.create_account(username, password, email, activation_key, st.secrets["EMAIL_KEY"]))[0]:
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
        if st.button("Login", key="switch_to_login"):
            st.session_state.view = "login"
    with col2:
        if st.button("Registrati", key="switch_to_register"):
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

def check_and_decrement(tokens_left):
    if tokens_left <= 0:
        return 0, False, "Non hai abbastanza token per questa operazione."
    return tokens_left - 1, True, "Token aggiornati con successo."

# Input chat
if prompt := st.chat_input("Scrivi un messaggio..."):

    username = st.session_state.get("username", "default_user")  # cambia default_user se necessario
    user_info, _ = printl(am.get_user_info(username))
    tokens_left = user_info[3]
    
    # Controlla token
    new_token_count, used_token, msg_token = check_and_decrement(tokens_left)
    st.info(msg_token)
    printl(am.update_user_tokens(username, new_token_count))
    print(f"Token rimanenti: {new_token_count}\nGenera risposta? {used_token}\nEsito: {msg_token}\n")
    
    if not used_token:
        st.warning("Hai finito i token.")
        st.stop()
    
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
