# Implementation Plan: Colab Live Demonstration

## Overview
We need a free, zero-setup way for interviewers to test the High-Throughput Inference Engine. We will create a Google Colab notebook that installs the repo, runs the FastAPI backend in the background, and exposes a public web interface using Gradio's `share=True` feature.

## Architecture Decisions
- **Hosting:** Google Colab (Free T4 GPU).
- **Frontend UI:** Gradio (`gradio_ui.py`). Gradio natively supports generating public URLs (`share=True`), bypassing the need for users to set up an `ngrok` account and auth token.
- **Integration:** The Gradio UI will make HTTP POST requests to the local `http://localhost:8000/v1/rag` endpoint, acting exactly as a real client would.

## Task List

### Phase 1: Foundation
- [ ] **Task 1: Build the Gradio UI**
  - **Description:** Create `src/gradio_ui.py` with a simple chat interface that queries our `/v1/rag` endpoint.
  - **Acceptance:** Must accept user text and display the RAG response. Must support `share=True` for public links.
  - **Scope:** Small (1 file).

### Checkpoint: Foundation
- [ ] Run the UI locally and verify it talks to the local FastAPI server.

### Phase 2: Colab Integration
- [ ] **Task 2: Generate the Colab Notebook**
  - **Description:** Create a `demo.ipynb` file containing the cells to clone the repo, install `uv`, install dependencies, start the FastAPI server in the background, and launch the Gradio UI.
  - **Acceptance:** Notebook must be valid JSON and run sequentially without errors.
  - **Scope:** Small (1 file).
- [ ] **Task 3: Update README.md**
  - **Description:** Add the "Open in Colab" badge to the README so interviewers can launch the demo with one click.
  - **Scope:** Small (1 file).

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Ready for review

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Colab terminates background processes | High | Use `nohup` or `subprocess.Popen` carefully to ensure the FastAPI server outlives the cell execution. |
| Ngrok auth required | Medium | We bypassed this entirely by using Gradio's built-in `share=True` feature. |
