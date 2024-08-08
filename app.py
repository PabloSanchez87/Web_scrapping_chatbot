# -------------- Need to deploy Streamlit cloud --------------
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3  # Replace the sqlite3 module with pysqlite3 to ensure compatibility

from langchain_openai.chat_models import ChatOpenAI  # Import the chat model from LangChain and OpenAI
import streamlit as st  # Import Streamlit for the user interface
from dotenv import load_dotenv  # Import function to load environment variables from a .env file
from langchain_openai import OpenAIEmbeddings  # Import OpenAI embeddings function
from langchain_chroma import Chroma  # Import Chroma for the vector database
from langchain.prompts import PromptTemplate  # Import prompt template
from langchain_core.runnables import RunnableSequence  # Import runnable sequence
import os  # Import the OS module to interact with the operating system
from openai import OpenAIError  # Import OpenAIError for error handling

# Load environment variables from a .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
persist_directory = './chroma_db'  # Directory where the Chroma database will be stored

# -------------- STREAMLIT CONFIGURATION --------------
# Set the configuration for the Streamlit app
page_title = "Help Assistant"  # Title of the application page
page_icon = "💬"  # Icon of the page
layout = "centered"  # Layout configuration for the Streamlit page
st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/pablosancheztorres/',
        'Report a bug': 'https://github.com/PabloSanchez87',
        'About': "# Help Assistant\nThis application generates a chat with customizable memory.\n\nCreated by Pablo Sánchez.\nFor support, send an email to sancheztorrespablo@gmail.com."
    },
)

# -------------- LOAD EMBEDDINGS --------------
# Function to load embeddings from ChromaDB
def load_embeddings(persist_directory):
    # Initialize OpenAI embeddings with the specified model and API key
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)
    # Initialize Chroma with the embeddings function and the persistence directory
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectordb

# Load the embeddings and store them in vectordb
vectordb = load_embeddings(persist_directory)

# -------------- LOAD PROMPT TEMPLATE --------------
# Define the prompt template for the assistant
prompt_template = """
You are a knowledgeable and helpful assistant designed to support employees of Oakdene Hollins by providing insights and answers based on the company's extensive database of reports and insights. Your goal is to offer clear, detailed, and contextually accurate responses. Ensure your answers are relevant to the employee's role and needs, and include practical steps or recommendations when appropriate.

Context: {context}

Employee Question: {input}

Answer:
"""

# Initialize the language model with the specified prompt template
llm = ChatOpenAI(model="gpt-4", max_tokens=1024, api_key=OPENAI_API_KEY)
# Create a prompt template object
prompt = PromptTemplate(input_variables=["input", "context"], template=prompt_template)
# Create a sequence of runnables with the prompt first and the language model last
qa_chain = RunnableSequence(first=prompt, last=llm)

# -------------- FUNCTIONS --------------
# Function to get AI response based on user messages
def get_ai_response(messages):
    # Concatenate all messages to form the context
    context = ""
    for msg in messages:
        context += f"{msg['role']}: {msg['content']}\n"
    
    # Prepare input data for the model
    input_data = {"input": messages[-1]['content'], "context": context}
    try:
        # Invoke the sequence to get the answer
        answer = qa_chain.invoke(input_data)
        return answer if isinstance(answer, str) else answer.content
    except OpenAIError as e:
        # Handle any errors that occur during the API call
        return f"Error: {e}"

# Function to handle the chat interface and logic
def chat():
    # Display the title and subtitle of the chat interface
    st.markdown("<h1 style='text-align: center; color: red;'>OAKDENE HOLLINS Help Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Help Assistant based on Reports and Insights</h4>", unsafe_allow_html=True)
    
    # Initial welcome message from the assistant
    welcome_message = {"role": "assistant", "content": "I'm a helpful assistant with access to a database from Oakdene Hollins."}
    
    # Initialize session state for messages if not already done
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [welcome_message]
    
    # Function to handle the submission of user input
    def submit():
        user_input = st.session_state.user_input.strip()
        if user_input:  # Check if the message is not blank
            st.session_state['messages'].append({'role': 'user', 'content': user_input})
            
            with st.spinner('Getting response...'):
                ai_response = get_ai_response(st.session_state['messages'])
                st.session_state['messages'].append({'role': 'assistant', 'content': ai_response})
            # Clear the input after submission
            st.session_state.user_input = ''

    # Display the messages
    if st.session_state['messages']:
        for msg in st.session_state['messages']:
            if msg['role'] == 'user':
                st.markdown(f"<div style='padding: 10px; border-radius: 10px; margin: 10px 0; text-align: left;'><b><u>You</u></b><br>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #4D4D4D; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; text-align: left;'><b><u>Assistant</u></b><br>{msg['content']}</div>", unsafe_allow_html=True)

    # Form to input new user messages
    with st.form(key='chat_form', clear_on_submit=True):
        st.text_area("You:", key='user_input')
        st.form_submit_button(label='Send', on_click=submit)

    # Add footer centered at the bottom
    st.markdown("<p style='text-align: right; color: gray'>App developed by Pablo Sánchez.</p>", unsafe_allow_html=True)

# -------------- MAIN --------------
# Main function to run the chat application
if __name__ == '__main__':
    chat()
