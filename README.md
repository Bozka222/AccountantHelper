# AccountantHelper (Czech) ⚖️

A privacy-first, local AI assistant designed to help accountants navigate EU accounting standards (IAS/IFRS). 

**Note:** This project is a **Proof of Concept (PoC)** demonstrating local Retrieval-Augmented Generation (RAG) for legal and accounting domains.

## 🌟 Key Features

- **Local & Private:** Your data never leaves your machine. Uses local embeddings (ChromaDB) and local LLMs (Ollama).
- **Zero Hallucination Focus:** The assistant is instructed to answer strictly based on the provided EU Regulation (2023/1803) text.
- **Verbatim Citations:** Every answer includes links to specific articles and paragraphs from the official Czech translation of the EU standards.
- **Hallucination Protection:** The system uses a "Reference-Only" injection mechanism. The LLM identifies relevant articles, but the actual legal text is injected by the Python backend directly from the database, ensuring 100% accuracy.

## 🛡 Reliability & Anti-Hallucination

In legal and accounting domains, paraphrasing errors can lead to serious mistakes. AccountantHelper uses a unique **Reference-Only Injection** workflow:

1. **Semantic Search:** The system finds relevant legal context.
2. **Restricted Generation:** The LLM is strictly forbidden from writing the legal text itself. It is only allowed to output a reference tag (e.g., `[[REF:Článek 5]]`).
3. **Verbatim Injection:** The Python backend detects these tags and performs an exact lookup in the ChromaDB metadata.
4. **UI Presentation:** The verbatim text is injected into the final response and displayed in a distinct "Doslovná citace" (Verbatim Citation) box.

This ensures that the legal text you see is exactly what is written in Commission Regulation (EU) 2023/1803, with zero interference from the LLM.

## 🛠 Tech Stack

- **Orchestration:** [FastMCP](https://github.com/jlowin/fastmcp) (Python)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (Sentence-Transformers)
- **LLM Engine:** [Ollama](https://ollama.com/)
- **UI:** [Streamlit](https://streamlit.io/)
- **Package Manager:** [uv](https://github.com/astral-sh/uv)

## 🚀 Getting Started

### Prerequisites

1. **Python 3.13+** (Managed via `uv` is recommended).
2. **Ollama:** Install from [ollama.com](https://ollama.com/) and pull a model:
   ```bash
   ollama pull llama3.2
   ```

### Installation

1. Clone this repository.
2. Install dependencies using `uv`:
   ```bash
   uv sync
   ```

### Running the App

#### 1. Streamlit Web UI (Recommended)
This provides a user-friendly chat interface with a sidebar showing database statistics and source citations.
```bash
   uv run streamlit run src/accountant_helper/ui/app.py
   ```

#### 2. Claude Desktop Integration (MCP)
To use AccountantHelper as a "Tool" inside Claude Desktop:

1. Open your Claude Desktop configuration file:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the configuration from the generated `CLAUDE_CONFIG.json` in this project. It should look like this (replace paths with your absolute paths):
   ```json
   {
     "mcpServers": {
       "accountant-helper": {
         "command": "uv",
         "args": [
           "--directory",
           "C:\\Path\\To\\AccountantHelper",
           "run",
           "python",
           "-m",
           "src.accountant_helper.mcp.server"
         ]
       }
     }
   }
   ```
3. Restart Claude Desktop. You will see a 🔌 icon indicating the tool is active.

## 🔄 Interface Comparison

The project provides two distinct ways to interact with the accounting standards. Choose the one that best fits your needs:

| Feature | Streamlit Web UI (Production) | Claude Desktop Integration (Development) |
| :--- | :--- | :--- |
| **Model Engine** | **Local (Ollama)** - Runs 100% on your machine. | **Cloud (Anthropic)** - Advanced reasoning via Claude. |
| **Privacy** | **Total Privacy** - No data leaves the device. | Hybrid - Local data access via MCP, cloud processing. |
| **Connectivity** | **Offline Capable** - Works without internet. | Requires internet connection to Anthropic. |
| **Logic** | Hardcoded RAG Pipeline for consistency. | "Agentic" - Claude decides when to use tools. |
| **User Experience** | Tailored Czech dashboard with stats & citations. | General chat interface with tool output. |
| **Use Case** | Daily work for accountants in a secure environment. | Testing tools, complex reasoning, and debugging. |

## 📂 Project Structure

- `src/accountant_helper/mcp/`: MCP server and specialized tools (search, calculate, stats).
- `src/accountant_helper/ui/`: Streamlit application code.
- `src/accountant_helper/vector_store/`: Logic for data ingestion and semantic search.
- `data/vector_db/`: Local storage for indexed accounting standards.

## ⚖️ Legal Disclaimer
This tool is for informational purposes only and does not constitute professional accounting or legal advice. Always verify findings against official EU publications.
