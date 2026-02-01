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
from src.accountant_helper.mcp.tools.citation import get_verbatim_text
import re

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
    st.markdown("""
    **Soukromí na prvním místě** 🔒
    Tento asistent běží plně lokálně. Vaše data ani dotazy neopouštějí tento počítač.

    **Základní principy:**
    - **Nulová halucinace:** AI necituje text z paměti, ale vkládá jej přímo z ověřené databáze.
    - **Verifikovatelnost:** Každé tvrzení je doloženo doslovnou citací z právního předpisu.
    - **Aktuálnost:** Čerpá z konsolidovaného znění nařízení **[ (EU) 2023/1803](https://eur-lex.europa.eu/legal-content/CS/TXT/?uri=CELEX%3A02023R1803-20240430)**.
    """)

    with st.expander("Technické detaily"):
        st.write("""
        - **Model:** Llama 3.2 (přes Ollama)
        - **Vektorová databáze:** ChromaDB
        - **RAG:** Sémantické vyhledávání v 10 700+ paragrafech.
        """)
    
    try:
        stats = count_standards()
        st.metric("Počet záznamů v databázi", f"{stats['total_records']:,}".replace(",", " "))
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
        st.markdown(message["content"], unsafe_allow_html=True)

def inject_verbatim_citations(llm_output):
    """
    Identifies [[REF:ID]] tags in LLM output and replaces them with verbatim text from the database.
    """
    ref_pattern = r"\[\[REF:([^\]]+)\]\]"
    matches = re.finditer(ref_pattern, llm_output)
    
    final_output = llm_output
    injected_refs = []
    
    for match in matches:
        ref_tag = match.group(0)
        ref_id = match.group(1)
        
        # Fetch verbatim text
        verbatim_text = get_verbatim_text(ref_id)
        
        # Format for UI
        formatted_citation = f"""
<div class="citation-box">
    <b>Doslovná citace ({ref_id}):</b><br>
    <i>{verbatim_text}</i>
</div>
"""
        
        # Replace tag
        final_output = final_output.replace(ref_tag, formatted_citation)
        injected_refs.append(ref_id)
        
    return final_output, injected_refs

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
        raw_results = search_accounting_standards(prompt, n_results=5)
        
        # 2. Construct RAG prompt with the refined master prompt
        master_prompt = f"""Jste profesionální český asistent specializovaný na účetní standardy.
KOMUNIKUJTE VÝHRADNĚ V ČEŠTINĚ. Je přísně zakázáno používat polská, anglická nebo jiná cizí slova (např. 'Odpowiedź', 'цих', 'these').

### PRAVIDLA PRO RELEVANTNÍ DOTAZY:
1. Odpovídejte POUZE na základě KONTEXTU. Pokud tam odpověď není, řekněte to.
2. Dodržujte STRIKTNĚ níže uvedenou strukturu s nadpisy začínajícími na ###.
3. V sekci '### 1. Odpověď' nepoužívejte žádné značky [[REF:ID]].
4. Všechny značky [[REF:SOURCE_ID]] uveďte VÝHRADNĚ v sekci '### 2. Doslovná citace ze zdroje'.
5. SOURCE_ID získáte z KONTEXTU (např. z [SOURCE_ID: STD:IAS 23:5] vytvořte [[REF:STD:IAS 23:5]]).

### PRAVIDLA PRO OFF-TOPIC DOTAZY:
- Pokud se dotaz NETÝKÁ účetnictví (např. sport, Michael Jordan), odpovězte POUZE: "Omlouvám se, ale jsem specializovaný asistent pro účetní standardy. Na dotazy mimo toto téma nemohu odpovídat."

### POŽADOVANÁ STRUKTURA:
### 1. Odpověď
(Váš srozumitelný český výklad.)

### 2. Doslovná citace ze zdroje
[[REF:SOURCE_ID_1]]
[[REF:SOURCE_ID_2]]

### 3. Související články a normy
(Seznam ID, např. STD:IAS 23:1, REG:5)

---
KONTEXT:
{raw_results}

DOTAZ:
{prompt}

ODPOVĚĎ:"""

        full_response = ""
        
        try:
            # 3. Call Ollama with temperature 0 for consistency
            response = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': master_prompt}],
                options={'temperature': 0},
                stream=True,
            )
            
            for chunk in response:
                full_response += chunk['message']['content']
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            
            # 4. Injection Step & Conditional Rendering
            # Check if it's an off-topic refusal (more robust check)
            if "Omlouvám se" in full_response and ("specializovaný asistent" in full_response or "mimo toto téma" in full_response):
                # If it's a refusal, we want a clean output without any RAG headers
                final_response = full_response.split("###")[0].strip() 
                message_placeholder.markdown(final_response)
            else:
                final_response, refs = inject_verbatim_citations(full_response)
                message_placeholder.markdown(final_response, unsafe_allow_html=True)
            
            full_response = final_response # For history

            # Show citations in an expander
            with st.expander("Použité zdroje a citace (Kontext pro RAG)"):
                st.markdown(raw_results)

        except Exception as e:
            error_msg = f"Chyba při komunikaci s Ollama: {str(e)}"
            if "ConnectionError" in str(e) or "11434" in str(e):
                error_msg = "Chyba: Nepodařilo se připojit k Ollama. Ujistěte se, že Ollama běží na localhost:11434."
            
            message_placeholder.error(error_msg)
            full_response = error_msg

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
