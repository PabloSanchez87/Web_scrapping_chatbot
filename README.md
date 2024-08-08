
# Proyecto de Chatbot con Memoria Personalizable | RAG | WebScrapping

## Contextualización
### ¿Qué es Retrieval-Augmented Generation (RAG)?

Retrieval-Augmented Generation (RAG) es una técnica que combina la generación de texto mediante modelos de lenguaje con la recuperación de información relevante de una base de datos. En esencia, un sistema RAG utiliza una base de datos de conocimiento para mejorar la precisión y relevancia de las respuestas generadas por el modelo de lenguaje. Los pasos para crear un sistema RAG son los siguientes:

1. **Preparación de la Base de Datos**:
   - Recopilar documentos, informes o cualquier otra fuente de información relevante.
   - Procesar estos documentos para extraer el texto útil.

2. **Generación de Embeddings**:
   - Utilizar un modelo de lenguaje (por ejemplo, `text-embedding-ada-002` de OpenAI) para convertir el texto en vectores numéricos llamados embeddings.
   - Estos embeddings representan el contenido semántico de los textos y permiten compararlos de manera eficiente.

3. **Almacenamiento en una Base de Datos de Vectores**:
   - Almacenar los embeddings generados en una base de datos de vectores, como ChromaDB.
   - Esta base de datos permitirá la búsqueda y recuperación eficiente de información relevante basada en similitudes semánticas.

4. **Recuperación de Información**:
   - Cuando el usuario realiza una consulta, convertir esta consulta en embeddings utilizando el mismo modelo de lenguaje.
   - Buscar los embeddings más similares en la base de datos de vectores para recuperar la información relevante.

5. **Generación de Respuestas**:
   - Utilizar un modelo de lenguaje (por ejemplo, `gpt-4` de OpenAI) para generar una respuesta basada en la información recuperada y la consulta del usuario.
   - La respuesta generada se basa tanto en la capacidad del modelo de lenguaje como en la información contextual recuperada de la base de datos.

Este enfoque mejora significativamente la calidad de las respuestas generadas, ya que el modelo de lenguaje tiene acceso a información específica y relevante que enriquece sus respuestas.

---

## Descripción del proyecto.

Este proyecto implementa un chatbot basado en la plataforma Streamlit, que utiliza la API de OpenAI y LangChain para generar respuestas contextuales basadas en una base de datos de informes y conocimientos de Oakdene Hollins.

La aplicación es interactiva y permite a los usuarios obtener respuestas precisas y útiles a sus consultas.

## Contenido del Proyecto

- `app.py`: Archivo principal que contiene la lógica de la aplicación Streamlit.
- `requirements.txt`: Lista de dependencias necesarias para ejecutar el proyecto.
- `update_embeddings.py`: Script para generar y actualizar los embeddings.
- Otros archivos relacionados con el scraping de datos y la configuración del asistente.

## Instalación

1. Clonar el repositorio:
   ```sh
   git clone https://github.com/PabloSanchez87/Web_scrapping_chatbot.git
   cd <nombre_del_repositorio>
   ```

2. Crear un entorno virtual y activarlo:
   ```sh
   python -m venv .env
   source .env/bin/activate  # En Windows usa `env\Scripts\activate`
   ```

3. Instalar las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

## Configuración

1. Crear un archivo `.env` en el directorio principal del proyecto con el siguiente contenido, reemplazando `<YOUR_OPENAI_API_KEY>` con tu clave de API de OpenAI:
   ```env
   export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
   ```

## Generación de Embeddings y Configuración de ChromaDB

1. Ejecutar el script `update_embeddings.py` para generar y actualizar los embeddings:
   ```sh
   python update_embeddings.py
   ```
   - Debes ajustar modelo a utilizar, directorios,...

2. Este script realiza las siguientes tareas:
   - Carga y procesa los documentos de interés.
   - Genera embeddings para los textos utilizando el modelo `text-embedding-ada-002` de OpenAI.
   - Almacena los embeddings en una base de datos Chroma para una recuperación eficiente.

## Uso de la Aplicación

1. Para iniciar la aplicación Streamlit, ejecuta:
   ```sh
   streamlit run main.py
   ```

2. La aplicación mostrará una interfaz de chat donde puedes interactuar con el asistente.

## Estructura del Código

### `app.py`

1. **Importaciones y Configuración Inicial**:
   - Se configuran los módulos necesarios y se carga la clave de API de OpenAI desde el archivo `.env`.
   - Se configura la interfaz de Streamlit con un título, ícono y diseño.

2. **Carga de Embeddings**:
   - Función `load_embeddings`: Carga los embeddings desde la base de datos Chroma.
   ```python
   def load_embeddings(persist_directory):
       embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', api_key=OPENAI_API_KEY)
       vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
       return vectordb
   ```

3. **Configuración del Modelo de Lenguaje y Plantilla de Prompt**:
   - Se configura el modelo de lenguaje `ChatOpenAI` con el modelo `gpt-4`.
   - Se define una plantilla de prompt para estructurar las consultas al modelo de lenguaje.
   ```python
   prompt_template = """
   You are a knowledgeable and helpful assistant...
   """
   ```
   - Se puede cambiar el modelo a utilizar.

4. **Funciones de Respuesta del Asistente**:
   - Función `get_ai_response`: Procesa los mensajes del usuario y genera una respuesta utilizando el modelo de lenguaje y los embeddings.
   ```python
   def get_ai_response(messages):
       context = ""
       for msg in messages:
           context += f"{msg['role']}: {msg['content']}"

       input_data = {"input": messages[-1]['content'], "context": context}
       try:
           answer = qa_chain.invoke(input_data)
           return answer if isinstance(answer, str) else answer.content
       except OpenAIError as e:
           return f"Error: {e}"
   ```

5. **Interfaz de Usuario con Streamlit**:
   - Función `chat`: Define la interfaz de usuario, mostrando mensajes y permitiendo la entrada de nuevos mensajes.
   ```python
   def chat():
       st.markdown("<h1 style='text-align: center; color: red;'>OAKDENE HOLLINS Help Assistant</h1>", unsafe_allow_html=True)
       ...
       if 'messages' not in st.session_state:
           st.session_state['messages'] = [welcome_message]
       ...
   ```

## Archivos de Scraping y Configuración

- `web_scrapping_pdfs_reports.py`: Script para realizar scraping de PDF de reportes.
- `web_scrapping_pdfs_news-insights.py`: Script para realizar scraping de PDFs de noticias e insights.
- `web_scrapping_urls.py`: Script para realizar scraping de URLs.

## Actualización de Embeddings

### Estructura de `update_embeddings.py`

- Carga los textos a partir de los archivos scrapeados.
- Genera embeddings utilizando `OpenAIEmbeddings`.
- Almacena los embeddings en ChromaDB.

### Ejecución del Script

```sh
python update_embeddings.py
```

## Notas para el despliegue en Streamlit usando un repositorio en Github
- [Consultar este documento](notes_deploy.md)

## Contribuciones

Si deseas contribuir a este proyecto, por favor crea un fork del repositorio y realiza un pull request con tus cambios.


## Contacto

Para más información o consultas, contacta a [sancheztorrespablo@gmail.com](mailto:sancheztorrespablo@gmail.com).