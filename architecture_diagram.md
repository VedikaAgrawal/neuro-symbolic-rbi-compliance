# Hybrid Neuro-Symbolic Compliance Guardrails Architecture

This document describes the pipeline architecture of the RBI Compliance Guardrails project.

## Architecture Pipeline Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as React Frontend
    participant API as FastAPI Backend
    participant LLM as Gemini 1.5 Flash (Neural Layer)
    participant Z3 as Z3 SMT Solver (Symbolic Layer)
    participant DB as Supabase PostgreSQL DB

    User->>API: POST /verify { query: "..." }
    note over API: Phase 1: Neural Perception
    API->>LLM: generate_content(query, schema)
    LLM-->>API: Extracted Facts (JSON)
    note over API: Phase 2: Symbolic Verification
    API->>Z3: Assert facts & RBI rules
    Z3-->>API: SAT / UNSAT + Violations
    note over API: Phase 3: Secure Logging
    API->>DB: INSERT log (secured server-to-server)
    API-->>User: Verification Result & Explanation
```

---

## Tooling & Rendering Information

The diagram above is written in **Mermaid.js** syntax. 
* **What is Mermaid?** Mermaid is an open-source, JavaScript-based diagramming and charting tool that uses Markdown-like text definitions to generate diagrams dynamically.
* **How to view/render it**:
  1. **GitHub / GitLab**: If you commit this file to a GitHub repository, GitHub will automatically render the diagram natively in the browser.
  2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension to see it inside your editor's Markdown preview tab.
  3. **Live Editor**: You can copy-paste the sequence diagram code into the official [Mermaid Live Editor](https://mermaid.live/) to export it as an image (PNG, SVG, or PDF) for your project presentations, report documents, or thesis files.
