import streamlit as st
from google import genai

st.title("Geography Chatbot")
st.write("Ask me anything about countries, capitals, cultures, landmarks, and more!")


try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("API Key not found! Please configure GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "display_history" not in st.session_state:
    st.session_state.display_history = []

for message in st.session_state.display_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask a geography question...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.display_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": user_input}]})

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=st.session_state.chat_history,
        )
        answer = response.text

    except Exception as e:
        answer = f"Error: {str(e)}"

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.display_history.append({"role": "assistant", "content": answer})
    st.session_state.chat_history.append({"role": "model", "parts": [{"text": answer}]})

if len(st.session_state.display_history) > 0:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.display_history = []
        st.rerun()

st.write("---")
st.write("Powered by Google Gemini")
