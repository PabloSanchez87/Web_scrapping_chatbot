from langchain_community.document_loaders import PyPDFLoader  # Import PDF loader from LangChain community
from langchain_openai import OpenAIEmbeddings  # Import OpenAI embeddings function from LangChain
from langchain_chroma import Chroma  # Import Chroma for the vector database
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Import text splitter from LangChain
import os  # Import OS module to interact with the operating system
import logging  # Import logging module to capture logs
from dotenv import load_dotenv  # Import function to load environment variables from a .env file
import time  # Import time module to measure time taken

# Load environment variables from a .env file
load_dotenv()

# Ensure to set your API key correctly
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# List of folder paths containing PDFs
folders_paths = ['pdf_news_insights', 'pdf_reports']
# Directory where the Chroma database will be stored
persist_directory = './chroma_db'

# Configure logging to capture errors and info messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to update embeddings
def update_embeddings(folders_paths, persist_directory):
    all_docs = []  # List to hold all documents

    # List all PDF files in the specified folders
    for folder_path in folders_paths:
        pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
        logger.info(f"Number of PDF files found in {folder_path}: {len(pdf_files)}")

        # Load each PDF file
        for pdf_file in pdf_files:
            path_pdf = os.path.join(folder_path, pdf_file)
            try:
                loader = PyPDFLoader(path_pdf)
                docs = loader.load()
                all_docs.extend(docs)
            except Exception as e:
                logger.error(f"Error loading {path_pdf}: {e}")

    logger.info(f"Total number of documents loaded: {len(all_docs)}")

    # If no documents are loaded, exit the function
    if not all_docs:
        logger.info("No new documents to add.")
        return

    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    chunked_documents = text_splitter.split_documents(all_docs)

    logger.info(f"Total number of document chunks: {len(chunked_documents)}")

    # Create embeddings using OpenAI
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)

    # Record the start time for API calls
    start_time = time.time()

    # Load the existing vector database or create a new one if it doesn't exist
    try:
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        vectordb.add_documents(chunked_documents)
    except ValueError as e:
        if 'tenant default_tenant' in str(e):
            vectordb = Chroma.from_documents(chunked_documents, embeddings, persist_directory=persist_directory)
        else:
            raise e

    # Record the total time taken for API calls
    end_time = time.time()
    total_time = end_time - start_time

    logger.info(f"Total time to add documents to Chroma: {total_time} seconds")
    logger.info("Embedding update process completed successfully.")

# Execute the function to update embeddings
update_embeddings(folders_paths, persist_directory)
