---

## Packaging & Release Instructions (Windows)

This project is packaged into a **Windows desktop application** using **PyInstaller (onedir mode)**.

---

### 1. Prerequisites

Ensure the following are installed on the build machine:

* **Windows 10 / 11 (64-bit)**
* **Python 3.11.x**
* **Git**
* **Visual C++ Redistributable (x64)** (recommended)

Create and activate a virtual environment:

```bat
python -m venv venv
venv\Scripts\activate
```

Install dependencies:
Install Core Python Libraries
Run exactly these commands:
pip install --upgrade pip
pip install llama-index faiss-cpu sentence-transformers pyside6
pip install numpy torch tqdm
llama-index	RAG framework
faiss-cpu	Vector search
sentence-transformers	Embeddings
PySide6	Windows UI
torch	Required for embeddings

Setup llama.cpp (Windows)
This runs the LLM locally.

Model download link : https://huggingface.co/bartowski/Phi-3-mini-4k-instruct-GGUF
Place this model in folder "models" [create one after cloning this repo inside the root folder]

---

### 2. Folder Structure (Before Packaging)

Project root layout:

```
Win_Driver_HelperAI/
│
├─ backend/
├─ ui/
├─ docs/
├─ models/
├─ llama.cpp/
├─ embeddings/
├─ run_gui.py
├─ WinDriverHelperAI.spec
├─ requirements.txt
└─ README.md
```

⚠️ **Do not package from a partially built or dirty directory.**

---

### 3. Clean Previous Builds (Important)

Before every new build:

```bat
rmdir /s /q dist
rmdir /s /q build
```

Also ensure:

* No running `WinDriverHelperAI.exe`
* No open DLLs from previous builds

---

### 4. Build the Application (One-Directory Mode)

Run PyInstaller using the spec file:

```bat
pyinstaller --clean --noconfirm WinDriverHelperAI.spec
```

On success, output will be generated in:

```
dist/
└─ WinDriverHelperAI/
   ├─ WinDriverHelperAI.exe
   └─ _internal/
```

---

### 5. Verify Build Output

Ensure the following exist:

```
dist/WinDriverHelperAI/
│
├─ WinDriverHelperAI.exe        ← main executable
└─ _internal/
   ├─ backend/
   ├─ ui/
   ├─ models/
   ├─ llama.cpp/
   ├─ embeddings/
   ├─ *.dll
   └─ python runtime files
```

Test locally:

```bat
cd dist\WinDriverHelperAI
WinDriverHelperAI.exe
```

Confirm:

* App launches
* Model loads
* Queries work correctly

---

### 6. Rebuilding for a New Release

For every new release:

1. Update code / models
2. Clean `dist/` and `build/`
3. Run PyInstaller again
4. Test executable
5. Zip `dist/WinDriverHelperAI`
6. Deliver to customer

---

### 7. Supported Platform

* Windows 64-bit only
* CPU inference (llama.cpp)
* No internet connection required at runtime

---
Output : 
https://drive.google.com/drive/folders/1w8ouJZ6FTui318peW1SRONzeEPq1RgYZ?usp=sharing
