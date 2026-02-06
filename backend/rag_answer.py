import os
import sys

if getattr(sys, 'frozen', False):
    # Running as PyInstaller EXE
    app_dir = sys._MEIPASS
else:
    # Running normally
    app_dir = os.path.dirname(os.path.abspath(__file__))

if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

#import backend.early_init
os.environ["LLAMA_INDEX_DISABLE_TIKTOKEN"] = "1"
import tempfile
from backend.utils import resource_path
import subprocess
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core import Settings
Settings.tokenizer =  lambda text: text.split()

# ---- CONFIG ----

LLAMA_CLI_PATH = resource_path("llama.cpp/llama-cli.exe")
MODEL_PATH = resource_path("models/Phi-3-mini-4k-instruct-Q4_K_M.gguf")
FAISS_DIR = resource_path("embeddings/faiss_index")

DRIVER_KEYWORDS = ["adddevice", "analyzer", "api", "apis", "architecture", "audio", "bluetooth", "bsod", "bugcheck", "build", "bus", "catalog", "cat", ".inf", "checked build", "content", "core", "crash", "createfile", "debugger", "debug", "debugging", "deferred", "deployment", "descriptor", "devcon", "diagnostics", "direct", "display", "ddi", "ddk", "device", "deviceiocontrol","driver", "driverentry", "driverunload", "dump", "entry", "exe", "executives", "filesystem", "filter", "framework", "hal", "hardware", "headers", "hid", "hlk", "inf", "installation", "install", "interrupt", "io", "i/o", "irp", "irp_mj_", "irp_mn_", "irql", "isr", "kd", "kd.exe", "kernel", "kernel-mode", "kit", "lab", "level", "major", "manager", "mdl", "memory", "miniport", "minifilter", "mode", "model", "neither", "ndis", "network", "ntddk", "ntddk.h", "ntoskrnl", "ntstatus", "object", "package", "packet", "pci", "pcie", "peripheral", "performance", "plug", "pnp", "pnputil", "power", "printer", "procedure", "routine", "signing", "software", "storage", "storport", "struct", "structure", "testing", "trace", "tracing", "umdf", "user", "user-mode", "verifier", "verifier.exe", "visual studio", "wddm", "wdm", "wdm.h", "wdf", "wdfdevice", "wdfobject", "wdfqueue", "wdfrequest", "wdffunc.h", "wdk", "windbg", "windows"]

TOP_K = 3
MAX_TOKENS = 1024

# ----------------

# Offline embedding
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
Settings.llm = None  # VERY IMPORTANT

# Load index
storage_context = StorageContext.from_defaults(persist_dir=FAISS_DIR)
index = load_index_from_storage(storage_context)
retriever = index.as_retriever(
    similarity_top_k=3
)

def build_explanation_prompt(question, nodes):
    context = "\n".join(f"- {n.text[:500]}" for n in nodes)

    system_prompt = """You are a Windows Device Driver Development tutor for freshers.

Rules (STRICT):
- Use the documentation ONLY as background knowledge
- Do NOT quote, list, or restate documentation text
- Do NOT repeat documentation sentences or bullets
- Explain concepts in your own words
- If information is missing, say:
  "I dont have more informations as of now.". 
"""

    user_prompt = f"""Documentation:
{context}

Question:
{question}
"""

    return f"""<s><|user|>
{system_prompt}<|end|>
<|assistant|>
<|user|>
{user_prompt}<|end|>
<|assistant|>""".strip()

def build_code_prompt(question, nodes):
    context = "\n".join(f"- {n.text[:200]}" for n in nodes)

    system_prompt = """You are a Windows Device Driver Development tutor.

STRICT OUTPUT RULES:
- Generate COMPLETE, COMPILABLE code
- Use KMDF unless explicitly asked otherwise
- Include DriverEntry and EvtDeviceAdd
- Use clear comments inside the code
- Do NOT repeat documentation text
- Do NOT add explanations outside code comments
- Output ONLY code blocks
- If something is missing, add a comment explaining it
"""

    user_prompt = f"""Background documentation (for reference only):
{context}

Task:
{question}

Output:
- Single .c file
- Proper includes
- Minimal but correct Hello World style driver
"""

    return f"""<s><|user|>
{system_prompt}<|end|>
<|assistant|>
<|user|>
{user_prompt}<|end|>
<|assistant|>""".strip()


def extract_answer(raw_output: str, code_mode=False) -> str:
    """
    Extract only the final assistant answer from Phi-3 output.
    """

    if "(truncated)" in raw_output:
        raw_output = raw_output.split("(truncated)", 1)[1]

    if "<|assistant|>" in raw_output:
        raw_output = raw_output.split("<|assistant|>")[-1]

    lines = raw_output.splitlines()
    clean = []

    skip_patterns = [
        "<|user|>",
        "<|end|>",
        "You are a Windows Device Driver Development tutor",
        "Rules:",
        "Documentation:",
        "load_backend",
        "llama_memory_breakdown",
        "available commands",
        "build",
        "model",
        "modalities",
        "Prompt:",
        "Loading model",
        "or Ctrl+C",
        "/regen",
        "/clear",
        "/read",
        "▀", "▄", "█",
        "Exiting..."
    ]

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if any(p in line for p in skip_patterns):
            continue

        # Drop documentation-style bullet echoes
        if not code_mode and line.startswith("- ") and ":" in line:
            continue

        clean.append(line)

    return "\n".join(clean).strip() if code_mode else " ".join(clean).strip()



def ask_phi3(prompt, code_mode=False):
    print("\n[INFO] Launching Phi-3 (CPU inference)...")
    print("[DEBUG] Prompt length:", len(prompt))

    cmd = [
    LLAMA_CLI_PATH,
    "-m", MODEL_PATH,
    "--threads", "8",
    "--ctx-size", "4096",
    "--single-turn",
    "--no-display-prompt",
    "--log-disable",
    "--temp", "0.1",
    "-n", str(MAX_TOKENS),
    "-p", prompt
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  
            encoding="utf-8",
            errors="ignore",
            timeout=180,   # Prevent hanging
            cwd=os.path.dirname(LLAMA_CLI_PATH),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        return f"❌ Failed to start model: {e}"
        
    stdout = result.stdout or ""
    stderr = result.stderr or ""

    raw_output = (stdout + "\n" + stderr).strip()
    
    if not raw_output:
        return "⚠️ Model produced no output."

    if result.returncode != 0:
        return f"[Model error]\n{raw_output}"
        
    return extract_answer(raw_output, code_mode=code_mode)
  
def is_code_generation(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in [
        "write", "create", "generate", "sample",
        "hello world", "skeleton", "example driver"
    ])

def is_small_talk(text):
    return text.strip().lower() in [
        "hi", "hello", "hey", "good morning", "good evening"
    ]

def is_driver_related(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in DRIVER_KEYWORDS)

if __name__ == "__main__":

    while True:
        question = input("\nAsk a driver question (or 'exit'): ").strip()

        if question.lower() == "exit":
            print("Exiting...")
            break

        if is_small_talk(question):
            print("Hi! Ask me anything about Windows device driver development.")
            continue

        if not is_driver_related(question):
            print("Sorry. I can help only with Windows device driver development related questions.")
            continue

        print("Retrieving from the docs")
        nodes = retriever.retrieve(question)

        if not nodes or all(len(n.text.strip()) < 50 for n in nodes):
            print("Not found in documentation. May be google it for more info.")
            continue

        print("Building prompts")
        is_code = is_code_generation(question)
        if is_code:
            prompt = build_code_prompt(question, nodes)
        else:
            prompt = build_explanation_prompt(question, nodes)
        
        print("Waiting for analysis & summarizing")
        #raw = ask_phi2(prompt)

        #answer = extract_answer(raw)
        answer = ask_phi3(prompt, code_mode=is_code)
        
        print("\n" + "=" * 80)
        print(answer)
        print("=" * 80)

