import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("🎹 MIDI Message Quiz (hex)")
st.write(
    "[ENG] This is a chatbot that uses OpenAI's GPT-3.5 model to generate 10 questions asking you random MIDI messages written in hexadecimal code."
    "[ITA] Questo è un chatbot che utilizza il modello GPT-3.5 di OpenAI per generare 10 domande riguardo messaggi MIDI casuali scritti in codice esadecimale."
)

api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message.
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API.
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
