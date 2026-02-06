# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = (
    collect_submodules("backend") +
    collect_submodules("ui") +
    collect_submodules("llama_index") +
    collect_submodules("sentence_transformers") +
    ["faiss", "numpy"]
)

datas = (
    collect_data_files("llama_index") +
    collect_data_files("sentence_transformers") +
    [
        ("models/Phi-3-mini-4k-instruct-Q4_K_M.gguf", "models"),
        ("embeddings", "embeddings"),
    ]
)

a = Analysis(
    ["run_gui.py"],
    pathex=["."],
    binaries=[
        ("llama.cpp/llama-cli.exe", "llama.cpp"),
		("llama.cpp/llama.dll","llama.cpp"),
		("llama.cpp/mtmd.dll","llama.cpp"),
		("llama.cpp/ggml-base.dll","llama.cpp"),
		("llama.cpp/ggml.dll","llama.cpp"),
		("llama.cpp/ggml-cpu-x64.dll","llama.cpp"),
    ],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["openai", "tiktoken"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="WinDriverHelperAI",
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="WinDriverHelperAI",
)
