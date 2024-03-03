import streamlit as st
from llm_chains import load_normal_chain
from langchain.memory import StreamlitChatMessageHistory
from streamlit_mic_recorder import mic_recorder
from audio_handler import transcribe_audio
from image_handler import handle_image
from image_handler import handle_image
import yaml
import os
from utils import save_chat_history_json, get_timestamp, load_chat_history_json

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


def load_chain(chat_history):
    return load_normal_chain(chat_history)


def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ""


def set_send_input():
    st.session_state.send_input = True
    clear_input_field()


def track_index():
    st.session_state.session_index_tracker = st.session_state.session_key


def save_chat_history():
    if st.session_state.history != []:
        if st.session_state.session_key == "new_session":
            st.session_state.new_session_key = get_timestamp() + ".json"
            save_chat_history_json(
                st.session_state.history,
                config["chat_history_path"] + st.session_state.new_session_key,
            )
        else:
            save_chat_history_json(
                st.session_state.history,
                config["chat_history_path"] + st.session_state.session_key,
            )


def main():
    st.title("Multi-Modal Local AI Chatbot")
    chat_container = st.container()
    st.sidebar.title("Chat Sessions")
    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])

    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
        if (
            st.session_state.session_key == "new_session"
            and st.session_state.new_session_key != None
        ):
            st.session_state.session_index_tracker = st.session_state.new_session_key
            st.session_state.new_session_key = None
    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox(
        "Select a chat session",
        chat_sessions,
        key="session_key",
        index=index,
        on_change=track_index,
    )
    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(
            config["chat_history_path"] + st.session_state.session_key
        )
    else:
        st.session_state.history = []
    chat_history = StreamlitChatMessageHistory(key="history")
    llm_chain = load_chain(chat_history)

    user_input = st.text_input(
        "Enter your message here", key="user_input", on_change=set_send_input
    )
    voice_recording_column, send_button_column = st.columns(2)
    with voice_recording_column:
        voice_recording = mic_recorder(
            start_prompt="Start Recording", stop_prompt="Stop Recording"
        )
    with send_button_column:
        send_button = st.button("Send", key="send_button", on_click=clear_input_field)

    uploaded_audio = st.sidebar.file_uploader(
        "Upload Audio Files Here", type=["wav", "mp3", "ogg"]
    )
    uploaded_image = st.sidebar.file_uploader(
        "Upload Image Files Here", type=["png", "jpg", "jpeg"]
    )
    uploaded_image = st.sidebar.file_uploader(
        "Upload Image Files Here", type=["png", "jpg", "jpeg"]
    )

    if uploaded_audio:
        transcribed_audio = transcribe_audio(uploaded_audio.getvalue())
        print(transcribed_audio)
        llm_chain.run("Summarize This Text : " + transcribed_audio)

    if voice_recording:
        transcribed_audio = transcribe_audio(voice_recording["bytes"])
        print(transcribed_audio)
        llm_chain.run(transcribed_audio)

    if send_button or st.session_state.send_input:
        if uploaded_image:
            with st.spinner("Processing Image...."):
                user_message = "Describe This Image in Detail Please"
                if st.session_state.user_question != "":
                    user_message = st.session_state.user_question
                    st.session_state.user_question = ""
                llm_answer = handle_image(
                    uploaded_image.getvalue(), st.session_state.user_question
                )
                chat_history.add_user_message(user_message)
                chat_history.add_ai_message(llm_answer)
        if st.session_state.user_question != "":
            with chat_container:
                llm_response = llm_chain.run(st.session_state.user_question)
                st.session_state.user_question = ""
            if uploaded_image:
                with st.spinner("Processing image ... ") :
                    user_message = "Describe this image in detail please."
                    if st.session_state.user_question != "":
                        user_message = st.session_state.user_question
                        st.session_state.user_question = ""
                llm_answer = handle_image(uploaded_image.getvalue(), st.session_state.user_question)
                chat_history.add_user_message(user_message)
                chat_history.add_ai_message(llm_answer)

    if chat_history.messages != []:
        with chat_container:
            st.write("Chat History:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)
    # print(chat_history.messages[0].dict())
    save_chat_history()


if __name__ == "__main__":
    main()
