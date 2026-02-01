# Project: Local EU Accounting AI Assistant (Czech) – Neural Retrieval Pivot

## 1. Project Overview & Pivot Strategy
We are building a specialized, privacy-first AI assistant for accountants to answer queries regarding EU accounting regulations in **Czech**.

**Strategic Pivot (Feb 2026):** We are moving away from relying solely on Generative LLMs (Generative AI) for answers due to the risk of hallucination and lack of strict adherence to complex legal structures.

**New Direction:** We are adopting a **Neural Information Retrieval (IR)** architecture. The system will function less like a "creative chatbot" and more like an "intelligent search engine" that understands intent.
1.  **Router (SetFit):** Classifies queries into specific Accounting Standards (e.g., "IAS 16", "IFRS 9") or "Off-Topic".
2.  **Reranker (Cross-Encoder):** Re-evaluates vector search results to find the single best matching paragraph with high precision.
3.  **Deterministic Output:** The primary output is the *exact* legal text, highlighted and ranked, rather than a generated summary.

## 2. Core Constraints
1.  **Local Execution:** All models (SetFit, Cross-Encoders, Vector DB) run locally.
2.  **Zero Hallucination:** The system extracts and ranks existing text; it does not generate new legal advice.
3.  **Precision over Creativity:** We prefer "No result found" over a low-confidence guess.
4.  **Deterministic Math:** Python handles calculations.
5.  **Language:** **Czech (CES)**.

## 3. Tech Stack
* **Retrieval Engine:** ChromaDB (Vector Search).
* **Router/Classifier:** **SetFit** (Sentence Transformer Fine-tuning) – trained on custom accounting intent data.
* **Reranker:** **Cross-Encoder** (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2` or multilingual variant).
* **Orchestration:** Python (replacing/augmenting MCP with direct inference pipelines).
* **Ingestion:** Python scripts (EUR-Lex API -> XML -> Chunking).
* **UI:** Streamlit (Search Engine Interface).

## 4. Data Source
* **Document:** Commission Regulation (EU) 2023/1803 (International Accounting Standards).
* **CELEX ID:** `02023R1803` (Consolidated).
* **Format:** XML (Formex).
* **Language:** Czech (`CES`).

## 5. Implementation Roadmap

### Phase 1: Data Pipeline (Foundational - Completed)
* [x] **Setup:** Environment (`uv`, Python 3.13).
* [x] **Fetch:** Download consolidated XML from EUR-Lex (`02023R1803`).
* [x] **Parse:** Extract `ARTICLE` blocks from Formex XML.
* [x] **Clean:** Pre-process text (Whitespace normalization, metadata extraction).
    * *Result:* `data/processed/cleaned_data.json`.

### Phase 2: Vector Storage (Foundational - Completed)
* [x] **Setup ChromaDB:** `paraphrase-multilingual-MiniLM-L12-v2`.
* [x] **Embed data:** Ingested 10,779 items with metadata (`article_number`, `ref_id`).
* [x] **Unique IDs:** Implemented collision-free IDs (e.g., `REG:5`, `STD:IAS 23:5`).

### Phase 3: Dataset Creation for "Neural Pivot" (New - High Priority)
* **Goal:** Create a labelled dataset to train the SetFit Router.
* **Steps:**
    1.  Create a CSV schema: `query`, `label` (e.g., "IAS 16", "IFRS 9", "OFF_TOPIC").
    2.  Generate synthetic training data: Use the LLM (Ollama) one last time to generate 10-20 distinct questions for each major Accounting Standard based on the parsed XML.
    3.  Manually review and clean the dataset to ensure ground truth.

### Phase 4: Training the SetFit Router (New)
* **Goal:** Train a small, fast model to route queries to the correct standard or reject them.
* **Steps:**
    1.  Install `setfit` and `sentence-transformers`.
    2.  Train a SetFit model on the dataset from Phase 3.
    3.  Evaluate accuracy on a hold-out test set.
    4.  Save the model locally (`models/setfit_router`).

### Phase 5: Implementing the Cross-Encoder Reranker (New)
* **Goal:** Filter the top 20 ChromaDB results down to the "Gold Standard" answer.
* **Steps:**
    1.  Integrate a Cross-Encoder model (`sentence-transformers/CrossEncoder`).
    2.  Create a pipeline: `Query -> ChromaDB (Top 20) -> Cross-Encoder -> Top 3`.
    3.  Benchmark precision against the previous pure-Vector approach.

### Phase 6: The "Search Engine" UI (UI Pivot)
* **Goal:** Move away from "Chat" to "Search".
* **Steps:**
    1.  Refactor Streamlit app to look like a search engine.
    2.  Display results as: **Standard Name** | **Relevance Score** | **Snippet**.
    3.  Implement "Expand to read full text" logic using the Verbatim Store.

---
## Progress Log

### 2026-02-01 [Strategic Pivot]
* **Decision:** Shifted strategy from Generative RAG to **Neural Information Retrieval**.
* **Reasoning:** Generative models proved too unstable for strict legal/accounting compliance (hallucination risk, formatting inconsistency).
* **Action:**
    * Defined new architecture: SetFit Router + Cross-Encoder Reranking.
    * Deprecated "Chatbot" persona in favor of "Intelligent Search" persona.
    * Added Phases 3-6 to build the discriminative model pipeline.

### 2026-02-01
* **Feature: Reference-Only Citation Injection (Completed):**
    * Successfully implemented logic where LLM outputs `[[REF:ID]]` and Python injects text.
    * *Note:* This logic remains useful for the "Snippet Display" in the new Search UI.
* **Data Cleanup:**
    * Fixed XML parsing issues (spacing).
    * Re-ingested 10.7k items with unique `ref_id`.