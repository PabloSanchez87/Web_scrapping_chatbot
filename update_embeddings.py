from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging
from dotenv import load_dotenv
import time

load_dotenv()

# Asegúrate de configurar tu clave API correctamente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

folders_paths = ['pdf_news_insights', 'pdf_reports']
persist_directory = './chroma_db'

# Configurar el registro para capturar errores
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_embeddings(folders_paths, persist_directory):
    all_docs = []

    # Listar todos los archivos PDF en las carpetas
    for folder_path in folders_paths:
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        logger.info(f"Número de archivos PDF encontrados en {folder_path}: {len(pdf_files)}")

        for pdf_file in pdf_files:
            path_pdf = os.path.join(folder_path, pdf_file)
            try:
                loader = PyPDFLoader(path_pdf)
                docs = loader.load()
                all_docs.extend(docs)
            except Exception as e:
                logger.error(f"Error al cargar {path_pdf}: {e}")

    logger.info(f"Número total de documentos cargados: {len(all_docs)}")

    if not all_docs:
        logger.info("No hay nuevos documentos para agregar.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunked_documents = text_splitter.split_documents(all_docs)

    logger.info(f"Número total de fragmentos de documentos: {len(chunked_documents)}")

    # Crear los embeddings usando OpenAI
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)

    # Registrar el tiempo de inicio
    start_time = time.time()

    # Cargar la base de datos existente o crear una nueva si no existe
    try:
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        vectordb.add_documents(chunked_documents)
    except ValueError as e:
        if 'tenant default_tenant' in str(e):
            vectordb = Chroma.from_documents(chunked_documents, embeddings, persist_directory=persist_directory)
        else:
            raise e

    # Registrar el tiempo total tomado para las llamadas a la API
    end_time = time.time()
    total_time = end_time - start_time

    logger.info(f"Tiempo total para añadir documentos a Chroma: {total_time} segundos")
    logger.info("Proceso de actualización de embeddings completado con éxito.")

# Ejecutar la función para actualizar los embeddings
update_embeddings(folders_paths, persist_directory)
