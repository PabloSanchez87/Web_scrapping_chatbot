from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os

load_dotenv()

# Asegúrate de configurar tu clave API correctamente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

persist_directory = './chroma_db'

def load_embeddings(persist_directory):
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vectordb

vectordb = load_embeddings(persist_directory)

# Plantilla de prompt para el asistente
prompt_template = """
You are a helpful assistant with access to a database of reports and insights from Oakdene Hollins. Use the following context to help answer the question.

Context: {context}

Question: {input}

Answer:
"""

# Usa ChatOpenAI con el modelo GPT-4
llm = ChatOpenAI(model="gpt-4", max_tokens=1024, api_key=OPENAI_API_KEY)
prompt = PromptTemplate(input_variables=["input", "context"], template=prompt_template)

# Crear la cadena combinando el prompt y el modelo usando RunnableSequence
qa_chain = RunnableSequence(first=prompt, last=llm)

st.title("OAKDENE HOLLINS Help Assistant")
st.write("Help Assistant based on Reports and Insights")

def send_question():
    question = st.session_state.get('question', '')
    if question:
        similar_results = vectordb.similarity_search(question, k=5)
        context = ""
        for doc in similar_results:
            context += doc.page_content + "\n"
        
        # Crear el input para el modelo
        input_data = {"input": question, "context": context}
        
        # Ejecutar la cadena
        answer = qa_chain.invoke(input_data)
        
        # Extraer el texto de la respuesta
        result = answer if isinstance(answer, str) else answer.content
        st.write(result)
    else:
        st.write('Please, enter a question before sending.')

# Crear un formulario para manejar el envío con la tecla Enter
with st.form(key='question_form', clear_on_submit=True):
    text_area_input = st.text_area("Ask your question", key='question')
    submit_button = st.form_submit_button(label='Send')

if submit_button:
    send_question()

# Añadir el pie de página centrado
st.markdown("<p style='text-align: right; color: gray'>App desarrollada por [Tu Nombre].</p>", unsafe_allow_html=True)
