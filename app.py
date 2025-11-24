import streamlit as st
import os
import json
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.json import JSONReader

# 1. Configuration
st.set_page_config(page_title="Local JSON RAG", layout="wide")
st.title("🤖 Chat with JSON Files (Local & Private)")

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

# 3. File Upload Section
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

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask something about your JSON data..."):
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