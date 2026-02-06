STEP 1 — Create Python Virtual Environment (IMPORTANT)
Open cmd and run:
cd D:\win_driver_ai_tutor
python -m venv venv
Activate it:
venv\Scripts\activate
You should see:
(venv)
⚠️ Always activate this before running the project.

STEP 2 — Install Core Python Libraries
Run exactly these commands:
pip install --upgrade pip
pip install llama-index faiss-cpu sentence-transformers pyside6
pip install numpy torch tqdm
llama-index	RAG framework
faiss-cpu	Vector search
sentence-transformers	Embeddings
PySide6	Windows UI
torch	Required for embeddings

STEP 3 — Setup llama.cpp (Windows)
This runs the LLM locally.
