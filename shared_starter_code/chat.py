import os
import streamlit as st
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AAU Assistant", page_icon="🎓")

# 1. Custom CSS with smooth scrolling
st.markdown("""
<style>
html { scroll-behavior: smooth; }
.stApp { background-color: #2B0D3F; color: white; }
/* Fixed Navigation Style */
.nav-buttons {
    position: fixed;
    bottom: 100px;
    right: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    z-index: 1000;
}
</style>
""", unsafe_allow_html=True)

# ⚓ TOP ANCHOR
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/0/0f/Addis_Ababa_University_logo.png", width=100)
    st.title("AAU Support")

    st.write("---")
    st.write("🔼 **Jump to Beginning**")
    st.markdown('<a href="#top" target="_self"><button style="width:100%; cursor:pointer;">⬆️ Go to Top</button></a>', unsafe_allow_html=True)

    st.write("🔽 **Jump to Latest**")
    st.markdown('<a href="#bottom" target="_self"><button style="width:100%; cursor:pointer;">⬇️ Go to Bottom</button></a>', unsafe_allow_html=True)

    st.write("---")
    if st.button("🗑️ Clear Conversation"):
        requests.post(f"{BACKEND_URL}/clear")
        st.session_state.messages = []
        st.rerun()

st.title("🎓 AAU General Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. CHAT DISPLAY
# (Normal order so scrolling to 'Bottom' feels natural for the newest message)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# ⚓ BOTTOM ANCHOR
st.markdown("<div id='bottom'></div>", unsafe_allow_html=True)

# 3. INPUT HANDLING
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"question": prompt},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["answer"],
                "highlights": data["highlights"]
            })
            st.rerun()
        else:
            st.error("Error: Backend issue.")
    except Exception as e:
        st.error(f"Cannot reach the server: {e}")
