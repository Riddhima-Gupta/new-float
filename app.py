import streamlit as st

from run_app import get_available_floats, get_response


st.set_page_config(page_title="FloatChat AI", page_icon="O", layout="wide")


def get_api_key() -> str | None:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return None

    api_key = str(api_key).strip()
    if not api_key or api_key.startswith("your_"):
        return None
    return api_key


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Ask about Argo float data, temperature, salinity, pressure, "
                    "or request a visualization."
                ),
            }
        ]


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        if message.get("error"):
            st.error(message["error"])
        st.markdown(message["content"])
        if message.get("chart") is not None:
            st.plotly_chart(message["chart"], use_container_width=True)


init_session_state()
api_key = get_api_key()

st.title("FloatChat AI")
st.caption("Single Streamlit app with direct Groq calls")

with st.sidebar:
    st.subheader("Configuration")
    if api_key:
        st.success("Groq API key loaded from Streamlit secrets.")
    else:
        st.warning("Add `GROQ_API_KEY` to `.streamlit/secrets.toml` before sending messages.")

    try:
        floats = get_available_floats()
    except Exception as exc:
        st.error(f"Could not load float metadata: {exc}")
        floats = []

    if floats:
        st.subheader("Available Floats")
        st.write(", ".join(floats[:20]))

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

for message in st.session_state.messages:
    render_message(message)

prompt = st.chat_input("Ask a question about the float dataset...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        assistant_message = {
            "role": "assistant",
            "content": "Missing `GROQ_API_KEY` in Streamlit secrets.",
        }
        with st.chat_message("assistant"):
            st.error(assistant_message["content"])
    else:
        history = st.session_state.messages[:-1]
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = get_response(prompt=prompt, api_key=api_key, history=history)
                    assistant_message = {
                        "role": "assistant",
                        "content": result.get("text", "No response returned."),
                        "chart": result.get("chart"),
                        "error": result.get("error"),
                    }
                    if assistant_message["error"]:
                        st.error(assistant_message["error"])
                    st.markdown(assistant_message["content"])
                    if assistant_message["chart"] is not None:
                        st.plotly_chart(assistant_message["chart"], use_container_width=True)
                except Exception as exc:
                    assistant_message = {
                        "role": "assistant",
                        "content": f"Error: {exc}",
                    }
                    st.error(assistant_message["content"])

    st.session_state.messages.append(assistant_message)
