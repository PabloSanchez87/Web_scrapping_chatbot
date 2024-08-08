# Uso de Git LFS para ChromaDB
## ¿Por qué usar Git LFS?
Git LFS (Large File Storage) es una extensión para Git que permite el manejo de archivos grandes. En este proyecto, ChromaDB genera archivos binarios, pickle y sqlite3 que pueden ser bastante grandes debido a la cantidad de datos y embeddings que almacena.

Algunas razones para usar Git LFS:

1. Manejo eficiente de archivos grandes: Los archivos grandes pueden ralentizar el rendimiento de Git. Git LFS almacena estos archivos de manera diferente para mantener el repositorio ligero y eficiente.
   
2. Evitación de límites de tamaño de repositorio: Al utilizar Git LFS, evitamos exceder los límites de tamaño impuestos por servicios de hospedaje de repositorios como GitHub.
   
3. Mejor rendimiento en clonado y extracción: Los usuarios que clonan el repositorio no tienen que descargar todos los archivos grandes a menos que realmente los necesiten, lo que mejora el rendimiento general.

## Configuración de Git LFS
En el archivo .gitattributes, se han añadido las siguientes líneas para indicar a Git LFS que maneje los archivos grandes generados por ChromaDB:
```scss
chroma_db/**/*.bin filter=lfs diff=lfs merge=lfs -text
chroma_db/**/*.pickle filter=lfs diff=lfs merge=lfs -text
chroma_db/**/*.sqlite3 filter=lfs diff=lfs merge=lfs -text
```
Estas líneas especifican que cualquier archivo con extensiones .bin, .pickle, y .sqlite3 dentro del directorio chroma_db debe ser gestionado por Git LFS.

---

# Carga de SQLite en Streamlit
## ¿Por qué cargar SQLite?
SQLite es una base de datos ligera y embebida que es excelente para aplicaciones de escritorio y web debido a su simplicidad y eficiencia. En el contexto de Streamlit, necesitamos una base de datos eficiente y fácil de manejar para almacenar y recuperar embeddings y otros datos relacionados con ChromaDB.

## Algunas razones para usar SQLite:

1. Portabilidad: SQLite es un archivo de base de datos único que se puede mover fácilmente entre sistemas.
2. Sin configuración de servidor: No requiere la configuración de un servidor de base de datos separado, lo que simplifica la implementación.
3. Integración con ChromaDB: ChromaDB puede usar SQLite para almacenar embeddings, lo que facilita la gestión de datos y la recuperación eficiente.

## Despliegue en Streamlit
Para desplegar la aplicación en Streamlit y usar SQLite, se ha incluido el módulo `pysqlite3` para asegurar la compatibilidad y evitar problemas con el módulo sqlite3 predeterminado de Python. La configuración en el código asegura que pysqlite3 se use en lugar de `sqlite3`:
```python
import sys
import pysqlite3
sys.modules['sqlite3'] = pysqlite3
```
Esto garantiza que todas las operaciones de base de datos se manejen correctamente cuando la aplicación se despliega en el entorno de Streamlit.
