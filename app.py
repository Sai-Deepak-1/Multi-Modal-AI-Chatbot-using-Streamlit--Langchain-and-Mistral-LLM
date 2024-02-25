import streamlit as st
from llm_chains import load_normal_chain
from langchain.memory import StreamlitChatMessageHistory
import yaml
import os
from utils import save_chat_history_json

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def load_chain(chat_history):
    return load_normal_chain(chat_history)


def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ""


def save_chat_history():
    if st.session_state.history != []:
        save_chat_history_json(
            st.session_state.history, config["chat_history_path"] + "random" + ". json"
        )
        # save_chat_history_json(st.session_state.historyl, config["chat_history_path"] + st.session_state.session_key + ". json")


def set_send_input():
    st.session_state.send_input = True
    clear_input_field()


def main():
    st.title("Multimodal Local Chat App")
    chat_container = st.container()
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])

    if "send_input" not in st.session_state:
        st.session_state.send_input = False
        st.session_state.user_question = ""

    st.sidebar.selectbox("Chat Session", chat_sessions, key="session_key")

    chat_history = StreamlitChatMessageHistory(key="history")
    llm_chain = load_chain(chat_history)

    user_input = st.text_input(
        "Type your message here", key="user_input", on_change=set_send_input
    )
    send_button = st.button("Send", key="send_button")

    if send_button or st.session_state.send_input:
        if st.session_state.user_question != "":
            with chat_container:
                llm_response = llm_chain.run(st.session_state.user_question)
                st.session_state.user_question = ""

    if chat_history.messages != []:
        with chat_container:
            st.write("Chat History:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)
    # print(chat_history.messages[0].dict())
    save_chat_history()


if __name__ == "__main__":
    main()