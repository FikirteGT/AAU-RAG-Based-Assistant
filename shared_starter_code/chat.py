import streamlit as st
import requests

st.set_page_config(page_title="AAU Assistant")
st.title("AAU General Assistant")

question = st.text_input("Ask a question about Addis Ababa University")

if st.button("Ask"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/ask",
                    json={"question": question},
                    timeout=30  # Added timeout
                )

                # Check if the request was successful
                if response.status_code == 200:
                    data = response.json()
                    st.subheader("Answer")
                    st.write(data["answer"])

                    st.subheader("Sources")
                    for s in data["sources"]:
                        st.caption(f"Source: {s}")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Is app.py running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
