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

### Phase 4: UI & Core Refinement
*   [x] **Connect Claude Desktop:** Configured via `CLAUDE_CONFIG.json`.
*   [x] **Build Streamlit App:** Local RAG interface implemented in `src/accountant_helper/ui/app.py`.
*   [x] **Citation Injection:** Implemented "Reference-Only" injection.
*   [x] **Unique Citation IDs:** Resolved ID collisions between Regulation articles and Standard paragraphs by implementing prefixed IDs (e.g., `REG:5`, `STD:IAS 23:5`).
*   [x] **Prompt Engineering:** Refined and upgraded the master prompt for the `llama` family of models to improve Czech reasoning and citation accuracy.

### Phase 5: Future Enhancements
*   [x] **Data Quality:** Fixed XML text spacing and formatting issues in the ingestion pipeline.
*   [ ] **UI Upgrades:** Implement chat history persistence in the Streamlit interface.
*   [ ] **Infrastructure:**
    *   [ ] **Dockerization:** Create a Dockerized version for consistent local deployment.
    *   [ ] **Deployment Research:** Investigate strategies for "Private Cloud" or secure local server deployment for accounting firms.

### Phase 6: Testing & Quality Assurance (Final Phase)
*   [ ] **Unit Tests:** Implement comprehensive unit tests for tools and data pipeline logic.
*   [ ] **Integration Tests:** End-to-end testing of the RAG pipeline with Ollama.

---
## Progress Log

### 2026-02-01
*   **Feature: Unique Reference IDs & Collision Fix:**
    *   **Issue:** Collisions between "Článek 5" of the Regulation and "Odstavec 5" of specific Standards.
    *   **Fix:** Refactored `parser.py` to generate unique `ref_id` strings (e.g., `REG:5` for Regulation, `STD:IAS 23:5` for Standards).
    *   **Cleanup:** Implemented automatic abbreviation of standard names (e.g., "MEZINÁRODNÍ ÚČETNÍ STANDARD 1" -> "IAS 1").
    *   **LLM Context:** Updated `cleaner.py` to inject `[SOURCE_ID: ...]` directly into the context passed to the LLM.
    *   **Robust Retrieval:** Updated `citation.py` to perform exact metadata lookups on the new `ref_id` field.
*   **Feature: Reference-Only Citation Injection:**
    *   **Goal:** Eliminate legal hallucinations by preventing the LLM from writing citation text.
    *   **Implementation:** LLM now outputs `[[REF:ID]]` tags. Python backend (Streamlit) scans for these tags and injects verbatim text from ChromaDB using a new `get_verbatim_article` tool.
    *   **Metadata Upgrade:** Updated `parser.py` and `cleaner.py` to extract and index `article_number` (e.g., "Článek 5").
    *   **Database Refresh:** Successfully re-ingested 10.7k items with the new metadata schema.
    *   **UI Update:** Added professional CSS styling for injected citations using a dedicated `citation-box` info block.

### 2026-02-01
*   **Citation & Formatting Fixes:**
    *   **Robust Citation Retrieval:** Fixed `IndexError: list index out of range` in `get_verbatim_text` by adding robust checks for empty result sets from ChromaDB.
    *   **Context Injection Fix:** Updated `search_accounting_standards` to explicitly include `[SOURCE_ID: ref_id]` in the context returned to the LLM.
    *   **XML Parser Spacing:** Improved `parser.py` to preserve spaces between XML elements using `get_text_with_spaces`.
    *   **Citation Cleaning:** Modified `get_verbatim_text` to automatically strip leading paragraph/article numbers (e.g., "14 ", "Článek 5 ") from the verbatim text, as they are already shown in the citation header.
    *   **UI De-duplication:** Refined the master prompt in `app.py` to ensure `[[REF:ID]]` tags appear only in the "Doslovná citace" section, keeping the main "Odpověď" section clean and readable.
    *   **Data Refresh:** Re-parsed and re-ingested the entire database (10,779 records) to apply all formatting improvements.

### 2026-01-31

### 2026-01-18
*   **Environment:** Initialized with `uv`. Dependencies: `requests`, `lxml`.
*   **Fetcher:** Refactored `fetcher.py`.
    *   Successfully downloaded consolidated version (2025-07-30).
    *   Target File: `data/raw/CL2023R1803CS0050020.0001.xml`.
*   **Next:** Parse the XML to split into Articles.
