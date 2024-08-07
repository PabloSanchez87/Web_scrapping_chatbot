# update_embeddings.py
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Asegúrate de configurar tu clave API correctamente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

folder_path = 'pdf_reports'
persist_directory = './chroma_db'

# Configurar el registro para capturar errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_embeddings(folder_path, persist_directory):
    all_docs = []

    # Listar todos los archivos PDF en la carpeta
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

    for pdf_file in pdf_files:
        path_pdf = os.path.join(folder_path, pdf_file)
        try:
            loader = PyPDFLoader(path_pdf)
            docs = loader.load()
            all_docs.extend(docs)
        except Exception as e:
            logger.error(f"Error loading {path_pdf}: {e}")

    if not all_docs:
        logger.info("No new documents to add.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunked_documents = text_splitter.split_documents(all_docs)

    # Crear los embeddings usando OpenAI
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)

    # Cargar la base de datos existente o crear una nueva si no existe
    try:
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        vectordb.add_documents(chunked_documents)
    except ValueError as e:
        if 'tenant default_tenant' in str(e):
            vectordb = Chroma.from_documents(chunked_documents, embeddings, persist_directory=persist_directory)
        else:
            raise e

    vectordb.persist()
    logger.info("Embedding update process completed successfully.")

# Ejecutar la función para actualizar los embeddings
update_embeddings(folder_path, persist_directory)
