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

### Phase 1: Data Pipeline (Current)
*   [x] **Setup:** Environment (`uv`, Python 3.14) and structure.
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
*   [ ] Setup ChromaDB.
*   [ ] Embed articles with metadata.
*   [ ] Create verbatim text store (JSON/SQLite).

### Phase 3: MCP Server
*   [ ] Initialize `fastmcp`.
*   [ ] Implement tools (`search`, `cite`, `calculate`).

### Phase 4: UI & Testing
*   [ ] Connect Claude Desktop.
*   [ ] Build Streamlit App.

---
## Progress Log

### 2026-01-31
*   **Parser:** Implemented `src/accountant_helper/data_pipeline/parser.py`.
    *   Parsed the 4.4MB XML file using `lxml` DOM.
    *   Successfully extracted:
        *   **Regulation Articles:** 5 main articles from `ENACTING.TERMS`.
        *   **Standard Paragraphs:** ~10.7k paragraphs from `CONS.ANNEX`.
    *   Preserved hierarchy context (e.g., "IAS 1 > Scope") for RAG metadata.
    *   Verified UTF-8 encoding integrity.
    *   Output: `data/processed/parsed_data.json`.
*   **Cleaner:** Implemented `src/accountant_helper/data_pipeline/cleaner.py`.
    *   Normalized whitespace.
    *   Separated paragraph numbers/headings from body text.
    *   Created `text_to_embed` combining hierarchy context and content.
    *   Output: `data/processed/cleaned_data.json`.

### 2026-01-18
*   **Environment:** Initialized with `uv`. Dependencies: `requests`, `lxml`.
*   **Fetcher:** Refactored `fetcher.py`.
    *   Successfully downloaded consolidated version (2025-07-30).
    *   Target File: `data/raw/CL2023R1803CS0050020.0001.xml`.
*   **Next:** Parse the XML to split into Articles.
