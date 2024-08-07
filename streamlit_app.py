import streamlit as st
import openai
import time
from dotenv import load_dotenv
import os

load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Set up the assistant ID
assistant_id = os.getenv('ASSISTANT_ID')

def create_thread():
    thread = openai.beta.threads.create()
    return thread.id

def add_message_to_thread(thread_id, message):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

def run_assistant(thread_id):
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    while run.status != "completed":
        time.sleep(0.1)
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value

def main():
    st.title("OpenAI Assistant Chatbot")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = create_thread()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is your question?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        add_message_to_thread(st.session_state.thread_id, prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = run_assistant(st.session_state.thread_id)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()