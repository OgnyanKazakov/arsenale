import streamlit as st
import os
import json
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.json import JSONReader

# --- CSS INJECTION FUNCTION ---
def local_css(file_name):
    """Function to load local CSS file and inject it into Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found at: {file_name}. Did you create the 'assets/style.css' file?")

# 1. Configuration
# --- APPLY CUSTOM CSS AND CONFIG ---
local_css("assets/style.css")

st.set_page_config(
    page_title="JSON RAG Assistant", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Starts with sidebar hidden, cleaner for chat UI
)

# Replace st.title with centered Markdown headings
st.markdown("<h1 style='text-align: center; color: #111111;'>🤖 JSON RAG Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555555;'>Ask about your data. Powered by Llama 3.</h4>", unsafe_allow_html=True)
st.markdown("---")

# Define where to look for Ollama
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 2. Setup LlamaIndex Settings
# We use a small, fast local embedding model (runs on CPU fine)
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

# 3. File Upload Section (Stays in the sidebar)
with st.sidebar:
    st.header("Data Source")
    uploaded_files = st.file_uploader("Upload JSON files", type=["json"], accept_multiple_files=True)
    
    if st.button("Build Index") and uploaded_files:
        with st.spinner("Indexing JSON data..."):
            documents = []
            for uploaded_file in uploaded_files:
                # Load JSON content
                json_content = json.load(uploaded_file)
                # Convert JSON to string for indexing (simple method)
                # For complex JSON, JSONReader manages structure better
                text_content = json.dumps(json_content, indent=2)
                doc = Document(text=text_content, metadata={"filename": uploaded_file.name})
                documents.append(doc)
            
            # Create the Index (In-memory Vector Store)
            index = VectorStoreIndex.from_documents(documents)
            
            # Create Query Engine
            st.session_state["query_engine"] = index.as_query_engine()
            st.success(f"Indexed {len(documents)} files!")

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
        if "query_engine" in st.session_state:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state["query_engine"].query(prompt)
                    st.markdown(response.response)
                    
                    # Add assistant response to history
                    st.session_state.messages.append({"role": "assistant", "content": response.response})
        else:
            st.warning("Please upload and index a JSON file first.")