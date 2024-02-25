import streamlit as st
from llm_chains import load_normal_chain
def load_chain():
    return load_normal_chain()  

def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ""


def set_send_input():
    st.session_state.send_input = True
    clear_input_field()


def main():
    st.title("Chat Bot Application")
    st.subheader("Hello, Welcome to our Chat Bot Application. How can I help you?")
    chat_container = st.container()

    if "send_input" not in st.session_state:
        st.session_state.send_input = False
        st.session_state.user_question = ""

    user_input = st.text_input(
        "Type your message here", key="user_input", on_change=set_send_input
    )

    send_button = st.button("Send", key="send_button", on_click=clear_input_field)

    if send_button or st.session_state.send_input:
        if st.session_state.user_question != "":
            llm_response = "This is a response from the LLM model"
            with chat_container:
                st.chat_message("user").write(st.session_state.user_question)
                st.chat_message("ai").write("here is an answer")


if __name__ == "__main__":
    main()