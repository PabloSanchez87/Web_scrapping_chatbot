# main.py

from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
persist_directory = './chroma_db'

def load_embeddings(persist_directory):
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectordb

vectordb = load_embeddings(persist_directory)

prompt_template = """
You are a helpful assistant with access to a database of reports and insights from Oakdene Hollins. Use the following context to help answer the question.

Context: {context}

Question: {input}

Answer:
"""

llm = ChatOpenAI(model="gpt-4", max_tokens=1024, api_key=OPENAI_API_KEY)
prompt = PromptTemplate(input_variables=["input", "context"], template=prompt_template)
qa_chain = RunnableSequence(first=prompt, last=llm)

def get_ai_response(messages):
    context = ""
    for msg in messages:
        context += f"{msg['role']}: {msg['content']}\n"
    
    input_data = {"input": messages[-1]['content'], "context": context}
    answer = qa_chain.invoke(input_data)
    return answer if isinstance(answer, str) else answer.content

def chat():
    st.title("OAKDENE HOLLINS Help Assistant")
    st.write("Help Assistant based on Reports and Insights")
    
    welcome_message = {"role": "assistant", "content": "I'm a helpful assistant with access to a database from Oakdene Hollins."}
    
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [welcome_message]
    
    def submit():
        user_input = st.session_state.user_input.strip()
        if user_input:  # Verifica que el mensaje no esté en blanco
            st.session_state['messages'].append({'role': 'user', 'content': user_input})
            
            with st.spinner('Obteniendo respuesta...'):
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
                st.markdown(f"<div style='background-color: #4D4D4D; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; text-align: left;'><b><u>Asistente</u></b><br>{msg['content']}</div>", unsafe_allow_html=True) 

    with st.form(key='chat_form', clear_on_submit=True):
        st.text_input("Tu:", key='user_input')
        st.form_submit_button(label='Enviar', on_click=submit)

    # Añadir el pie de página centrado
    st.markdown("<p style='text-align: right; color: gray'>App desarrollada por Pablo Sánchez.</p>", unsafe_allow_html=True)

if __name__ == '__main__':
    chat()
