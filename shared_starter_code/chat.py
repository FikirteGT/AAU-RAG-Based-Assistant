import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="AAU Assistant", page_icon="🎓")

# 2. Custom CSS for a "React-like" feel
st.markdown("""
    <style>
    .stApp { background-color: #2B0D3F; }
    .stChatMessage { border-radius: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .source-box {
        background-color: #1A0726;
        border-left: 5px solid #007bff;
        padding: 10px;
        margin-top: 2px;
        font-size: 0.85rem;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/0/0f/Addis_Ababa_University_logo.png", width=100)
    st.title("AAU Support")
    st.info("I answer questions based on official Addis Ababa University documents.")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("🎓 AAU General Assistant")

# 4. Conversation Memory Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("View Sources"):
                for s in message["sources"]:
                    st.markdown(f"📄 `{s}`")

# 6. Chat Input Logic
if prompt := st.chat_input("How can I help you today?"):
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Message (Call Backend)
    with st.chat_message("assistant"):
        with st.spinner("Consulting AAU Documents..."):
            try:
                response = requests.post(
                    "http://localhost:8000/ask",
                    json={"question": prompt},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]

                    st.markdown(answer)

                    if sources:
                        with st.expander("View Sources"):
                            for s in sources:
                                st.markdown(f"📄 `{s}`")

                    # Add to memory
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(
                    "Cannot reach the server. Please ensure app.py is running.")
