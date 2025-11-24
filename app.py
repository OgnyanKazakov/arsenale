import streamlit as st
import os
import json
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.json import JSONReader

# --- CONSTANTS & CSS INJECTION FUNCTION ---
PERSIST_DIR = "index_storage"
INDEX_LOADED_KEY = "index_loaded"

def local_css(file_name):
    """Function to load local CSS file and inject it into Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fails silently if file not found, as we will provide the CSS content.
        pass

# 1. Configuration
# --- APPLY CUSTOM CSS AND CONFIG ---
local_css("assets/style.css") # Applies the new dark theme

st.set_page_config(
    page_title="JSON RAG Assistant", 
    layout="wide", 
    # Removed initial_sidebar_state="collapsed" so the sidebar is visible by default
)

# Replace st.title with centered Markdown headings
st.markdown("<h1 style='text-align: center;'>🤖 JSON RAG Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #9A9A9A;'>Ask about your data. Powered by Llama 3.</h4>", unsafe_allow_html=True)
st.markdown("---")

# Define where to look for Ollama
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 2. Setup LlamaIndex Settings (NOW INCLUDES PERSISTENCE CHECK)
if "setup_done" not in st.session_state:
    with st.spinner("Initializing Local Models..."):
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        Settings.llm = Ollama(
            model="llama3", 
            base_url=ollama_base_url,
            request_timeout=300.0
        )
        st.session_state["setup_done"] = True
    
    # --- Check for existing index and load it ---
    if os.path.exists(PERSIST_DIR) and not os.listdir(PERSIST_DIR) == []:
        with st.spinner(f"Loading existing index from {PERSIST_DIR}..."):
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            st.session_state["index"] = load_index_from_storage(storage_context)
            st.session_state["query_engine"] = st.session_state["index"].as_query_engine()
            st.session_state[INDEX_LOADED_KEY] = True
            st.success("Existing index loaded successfully!")
    else:
        st.session_state[INDEX_LOADED_KEY] = False
        
# 3. File Upload Section (Sidebar is now visible!)
with st.sidebar:
    st.header("Data Source")
    if st.session_state.get(INDEX_LOADED_KEY):
        st.info("Index already loaded from disk. Uploading new files will rebuild it.")
        
    uploaded_files = st.file_uploader("Upload JSON files", type=["json"], accept_multiple_files=True)
    
    if st.button("Build Index") and uploaded_files:
        with st.spinner("Indexing JSON data and persisting to disk..."):
            documents = []
            for uploaded_file in uploaded_files:
                # Load JSON content
                json_content = json.load(uploaded_file)
                text_content = json.dumps(json_content, indent=2)
                doc = Document(text=text_content, metadata={"filename": uploaded_file.name})
                documents.append(doc)
            
            # Create the Index (In-memory Vector Store)
            index = VectorStoreIndex.from_documents(documents)
            
            # --- PERSIST THE INDEX TO DISK ---
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            
            # Create Query Engine
            st.session_state["query_engine"] = index.as_query_engine()
            st.session_state[INDEX_LOADED_KEY] = True
            st.success(f"Indexed {len(documents)} files and saved to disk!")

# --- 4. CENTERING CHAT INTERFACE ---
# Use columns to create empty buffers on the left and right, centering the content
col1, col_center, col3 = st.columns([1, 5, 1])

with col_center:
    # 4. Chat Interface Logic
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input (This is now visually centered by the columns)
    if prompt := st.chat_input("Ask a question about your JSON data..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        if st.session_state.get("query_engine"):
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Use the stored query engine
                    response = st.session_state["query_engine"].query(prompt)
                    st.markdown(response.response)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({"role": "assistant", "content": response.response})
        else:
            st.warning("Please upload and index a JSON file first (or wait for the existing index to load).")