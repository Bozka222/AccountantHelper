import streamlit as st
import ollama
import os
import sys

# Add the project root to sys.path to allow imports from src
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.accountant_helper.mcp.utils.db import get_collection
from src.accountant_helper.mcp.tools.search import search_accounting_standards
from src.accountant_helper.mcp.tools.stats import count_standards

st.set_page_config(
    page_title="Účetní asistent - EU Accounting AI Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stChatFloatingInputContainer {
        padding-bottom: 20px;
    }
    .citation-box {
        background-color: #eef2f6;
        border-left: 5px solid #004a99;
        padding: 10px;
        margin: 10px 0;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Účetní asistent")
st.subheader("Místní asistent pro EU účetní standardy (IAS/IFRS)")

# Sidebar
with st.sidebar:
    st.header("O aplikaci")
    st.info("Tato aplikace využívá RAG (Retrieval-Augmented Generation) pro poskytování přesných odpovědí na základě nařízení Komise (EU) 2023/1803.")
    
    try:
        stats = count_standards()
        st.metric("Počet záznamů v databázi", stats["total_records"])
    except Exception:
        st.warning("Nepodařilo se načíst statistiky databáze.")

    st.divider()
    model_name = st.selectbox("Vyberte LLM model (Ollama)", ["llama3.2"], index=0)
    
    if st.button("Vymazat historii chatu"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Zadejte svůj dotaz ohledně účetnictví..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 Prohledávám standardy...")
        
        # 1. Search for relevant context
        context = search_accounting_standards(prompt, n_results=3)
        
        # 2. Construct RAG prompt
        rag_prompt = f"""Jste odborný asistent pro EU účetní standardy. Odpovídejte v češtině.
Použijte POUZE následující kontext k zodpovězení dotazu. Pokud kontext neobsahuje odpověď, řekněte, že nevíte.
Vždy citujte konkrétní články nebo odstavce.

KONTEXT:
{context}

DOTAZ:
{prompt}

ODPOVĚĎ:"""

        full_response = ""
        
        try:
            # 3. Call Ollama
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': rag_prompt}],
                stream=True,
            )
            
            for chunk in response:
                full_response += chunk['message']['content']
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Show citations in an expander
            with st.expander("Použité zdroje a citace"):
                st.markdown(context)
                
        except Exception as e:
            error_msg = f"Chyba při komunikaci s Ollama: {str(e)}"
            if "ConnectionError" in str(e) or "11434" in str(e):
                error_msg = "Chyba: Nepodařilo se připojit k Ollama. Ujistěte se, že Ollama běží na localhost:11434."
            
            message_placeholder.error(error_msg)
            full_response = error_msg

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
