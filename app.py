# main.py

from langchain_openai.chat_models import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os
from openai import OpenAIError

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
persist_directory = './chroma_db'

# -------------- CONFIGURACIÓN STREAMLIT--------------
page_title = "Help Assistant"  # Título de la página de la aplicación
page_icon = "💬" # Icono de la página
layout = "centered"  
st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/pablosancheztorres/',
        'Report a bug': 'https://github.com/PabloSanchez87',
        'About': "# Help Assistant\nEsta aplicación genera un chat con memoria personalizable.\n\nCreada por Pablo Sánchez.\nPara soporte, envíe un correo a sancheztorrespablo@gmail.com."
    },   
)


# -------------- LOAD EMBEDDINGS--------------
def load_embeddings(persist_directory):
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectordb

vectordb = load_embeddings(persist_directory)

# -------------- LOAD PROMPT TEMPLATE --------------
prompt_template = """
You are a knowledgeable and helpful assistant designed to support employees of Oakdene Hollins by providing insights and answers based on the company's extensive database of reports and insights. Your goal is to offer clear, detailed, and contextually accurate responses. Ensure your answers are relevant to the employee's role and needs, and include practical steps or recommendations when appropriate.

Context: {context}

Employee Question: {input}

Answer:
"""

llm = ChatOpenAI(model="gpt-4", max_tokens=1024, api_key=OPENAI_API_KEY)
prompt = PromptTemplate(input_variables=["input", "context"], template=prompt_template)
qa_chain = RunnableSequence(first=prompt, last=llm)

# -------------- FUNCTIONS --------------
def get_ai_response(messages):
    context = ""
    for msg in messages:
        context += f"{msg['role']}: {msg['content']}\n"
    
    input_data = {"input": messages[-1]['content'], "context": context}
    try:
        answer = qa_chain.invoke(input_data)
        return answer if isinstance(answer, str) else answer.content
    except OpenAIError as e:
        return f"Error: {e}"

def chat():
    st.markdown("<h1 style='text-align: center; color: red;'>OAKDENE HOLLINS Help Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Help Assistant based on Reports and Insights</h4>", unsafe_allow_html=True)    
    
    welcome_message = {"role": "assistant", "content": "I'm a helpful assistant with access to a database from Oakdene Hollins."}
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [welcome_message]
    
    def submit():
        user_input = st.session_state.user_input.strip()
        if user_input:  # Verifica que el mensaje no esté en blanco
            st.session_state['messages'].append({'role': 'user', 'content': user_input})
            
            with st.spinner('Getting response...'):
                ai_response = get_ai_response(st.session_state['messages'])
                st.session_state['messages'].append({'role': 'assistant', 'content': ai_response})
            # Limpiar el input después de enviar
            st.session_state.user_input = ''

    # Mostrar los mensajes
    if st.session_state['messages']:
        for msg in st.session_state['messages']:
            if msg['role'] == 'user':
                st.markdown(f"<div style='padding: 10px; border-radius: 10px; margin: 10px 0; text-align: left;'><b><u>Tú</u></b><br>{msg['content']}</div>", unsafe_allow_html=True)  
            else:
                st.markdown(f"<div style='background-color: #4D4D4D; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; text-align: left;'><b><u>Assistant</u></b><br>{msg['content']}</div>", unsafe_allow_html=True) 

    with st.form(key='chat_form', clear_on_submit=True):
        st.text_area("You:", key='user_input')
        st.form_submit_button(label='Send', on_click=submit)

    # Añadir el pie de página centrado
    st.markdown("<p style='text-align: right; color: gray'>App developed by Pablo Sánchez.</p>", unsafe_allow_html=True)


# -------------- MAIN --------------
if __name__ == '__main__':
    chat()
