import streamlit as st
from groq import Groq


if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ API Key")
    st.stop()


st.set_page_config(page_title="FloatChat AI", page_icon="O", layout="centered")


def get_client() -> Groq:
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def get_response(prompt: str) -> tuple[str, bool]:
    try:
        client = get_client()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant. "
                        "Give clear, concise, accurate answers."
                    ),
                },
                *st.session_state.messages,
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return completion.choices[0].message.content or "No response returned.", False
    except Exception as e:
        return str(e), True


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_chat() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message.get("is_error"):
                st.error(message["content"])
            else:
                st.markdown(message["content"])


init_session_state()

st.title("FloatChat AI")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

render_chat()

prompt = st.chat_input("Ask something...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, is_error = get_response(prompt)
            if is_error:
                st.error(response)
            else:
                st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response, "is_error": is_error}
    )
