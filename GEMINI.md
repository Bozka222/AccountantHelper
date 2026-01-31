# Project: Local EU Accounting AI Assistant (Czech)

## 1. Project Overview
We are building a specialized, privacy-first AI assistant for accountants to answer queries regarding EU accounting regulations in **Czech**.

**Crucial Requirement:** The AI must use *only* provided legal documentation (RAG). Zero hallucinations. Answers must be traceable to specific legal articles with verbatim citations.

## 2. Core Constraints
1.  **Local Execution:** LLM (Ollama) and Vector DB (Chroma) run locally. No data leaves the machine.
2.  **Zero Hallucination:** "I don't know" > Guessing.
3.  **Verbatim Citations:** Exact legal text must be retrievable.
4.  **Deterministic Math:** Python handles calculations, not the LLM.
5.  **Language:** **Czech (CES)**.

## 3. Tech Stack
*   **LLM:** Ollama (e.g., llama3.2, mistral-nemo).
*   **Orchestration:** Python MCP Server (`fastmcp`).
*   **RAG:** ChromaDB (local).
*   **Ingestion:** Python scripts (EUR-Lex API -> XML -> Chunking).
*   **UI:** Claude Desktop (dev), Streamlit (prod).

## 4. Data Source
*   **Document:** Commission Regulation (EU) 2023/1803 (International Accounting Standards).
*   **CELEX ID:** `02023R1803` (Consolidated).
*   **Format:** XML (Formex).
*   **Language:** Czech (`CES`).

## 5. Implementation Roadmap

### Phase 1: Data Pipeline
*   [x] **Setup:** Environment (`uv`, Python 3.13) and structure.
*   [x] **Fetch:** Script to download consolidated XML from EUR-Lex.
    *   *Status:* `src/accountant_helper/data_pipeline/fetcher.py` works.
    *   *Result:* `data/raw/CL2023R1803CS0050020.0001.xml` (Czech).
*   [x] **Parse:** Extract `ARTICLE` blocks from Formex XML.
    *   *Status:* `src/accountant_helper/data_pipeline/parser.py` implemented using `lxml`.
    *   *Result:* `data/processed/parsed_data.json` (10,779 items: 5 Articles, 10,774 Paragraphs).
*   [x] **Clean:** Pre-process text for embedding (Chunking/Cleaning).
    *   *Status:* `src/accountant_helper/data_pipeline/cleaner.py` implemented.
    *   *Result:* `data/processed/cleaned_data.json` (Whitespace normalized, numbers separated, `text_to_embed` field created).

### Phase 2: Vector Storage
*   [x] **Setup ChromaDB:** Installed and configured with `paraphrase-multilingual-MiniLM-L12-v2`.
*   [x] **Embed data:** Ingested 10,779 items (Articles & Paragraphs).
    *   *Status:* Ingestion script `src/accountant_helper/vector_store/ingest.py` completed.
    *   *Result:* Persistent database in `data/vector_db`.
*   [x] **Verbatim store:** Metadata in ChromaDB includes full verbatim text for retrieval.

### Phase 3: MCP Server
*   [x] **Initialize `fastmcp`:** Created `src/accountant_helper/mcp/server.py`.
*   [x] **Modular Architecture:** Refactored tools into separate modules for maintainability.
    *   `src/accountant_helper/mcp/tools/search.py`: Semantic search.
    *   `src/accountant_helper/mcp/tools/calculate.py`: Precision math.
    *   `src/accountant_helper/mcp/tools/stats.py`: Database statistics.
    *   `src/accountant_helper/mcp/tools/citation.py`: Specific citation retrieval with metadata filtering.
*   [x] **Implement tools:**
    *   `search_accounting_standards`: Semantic search in Czech standards.
    *   `calculate_accounting_formula`: Deterministic Python-based math tool.
    *   `count_standards`: Reports database size.
    *   `get_citation`: Targeted citation lookup using standard names and paragraph numbers.

### Phase 4: UI & Testing
*   [x] **Connect Claude Desktop:** Configured via `CLAUDE_CONFIG.json`.
*   [x] **Build Streamlit App:** Local RAG interface implemented in `src/accountant_helper/ui/app.py`.
*   [ ] **Testing & Quality Assurance:**
    *   [ ] **Unit Tests:** Implement comprehensive unit tests for tools and data pipeline logic.
    *   [ ] **Integration Tests:** End-to-end testing of the RAG pipeline with Ollama.
    *   [ ] **Prompt Engineering:** Refine and upgrade the master prompt for the `llama` family of models to improve Czech reasoning.

### Phase 5: Future Enhancements
*   [ ] **Data Quality:** Fix XML text spacing and formatting issues in the ingestion pipeline.
*   [ ] **UI Upgrades:** Implement chat history persistence in the Streamlit interface.
*   [ ] **Infrastructure:**
    *   [ ] **Dockerization:** Create a Dockerized version for consistent local deployment.
    *   [ ] **Deployment Research:** Investigate strategies for "Private Cloud" or secure local server deployment for accounting firms.

---
## Progress Log

### 2026-01-31
*   **MCP Server Refactoring & New Tools:**
    *   **Modular Refactor:** Restructured the MCP server into a package (`src/accountant_helper/mcp`) with subdirectories for `tools` and `utils`.
    *   **Citation Tool:** Added `get_citation` which supports metadata filtering (e.g., specific paragraph numbers) to improve RAG precision.
    *   **Stats Tool:** Added `count_standards` to monitor the vector database size (currently 10,779 items).
    *   **Bug Fixes:** Resolved a set-dictionary hashability error in the calculation tool and corrected import paths across modular tools.
    *   **Verification:** All tools (search, calculate, stats, citation) verified via `test_mcp_refactor.py`.
*   **Vector Store & Path Handling:**
    *   (Existing entries...)

### 2026-01-18
*   **Environment:** Initialized with `uv`. Dependencies: `requests`, `lxml`.
*   **Fetcher:** Refactored `fetcher.py`.
    *   Successfully downloaded consolidated version (2025-07-30).
    *   Target File: `data/raw/CL2023R1803CS0050020.0001.xml`.
*   **Next:** Parse the XML to split into Articles.
