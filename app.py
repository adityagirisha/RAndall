import streamlit as st
import openai
import toml
from llama_index.llms.openai import OpenAI
try:
  from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
  from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

try:
    secrets = toml.load(".streamlit/secrets.toml")
    openai.api_key = secrets['OPENAI_API_KEY']
except FileNotFoundError:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Randall", 
                   page_icon="🐱", 
                   layout="centered", 
                   initial_sidebar_state="auto", 
                   menu_items=None)
st.title("Hi! I'm RAndall! 🐱")
st.subheader('A Virtual Resident Advisor', divider='red')

# Initialize Chat
if "messages" not in st.session_state.keys(): 
    st.session_state.messages = [
        {"role": "assistant", "content": "How Can I Help You?"}
    ]

# Initialize Randall
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Randall is waking up... give him a moment"):
        reader = SimpleDirectoryReader(input_dir="./protocols", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(
            llm=OpenAI(model="gpt-3.5-turbo", 
                       temperature=0.5, 
                       system_prompt="You are an expert on the answering questions related to university housing and your job is to answer housing related questions. Assume that all questions are related to the Chico State Resident Housing Protocols. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index
index = load_data()

# Initialize Engine
if "chat_engine" not in st.session_state.keys(): 
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

# Prompt
if prompt := st.chat_input("Your question"): 
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display 
for message in st.session_state.messages: 
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Generate
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)