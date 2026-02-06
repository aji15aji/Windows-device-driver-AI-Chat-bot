from llama_index.core import VectorStoreIndex, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore
from pypdf import PdfReader
import faiss
import os
import re

PDF_DIR = "../docs/pdfs"
INDEX_DIR = "../embeddings/faiss_index"

os.makedirs(INDEX_DIR, exist_ok=True)

MAX_PAGES_PER_PDF = 150        # practical limit
MIN_PAGE_CHARS = 300
CHUNK_SIZE = 700               # tokens approx
CHUNK_OVERLAP = 100

documents = []

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, source, page):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append(
            Document(
                text=chunk_text,
                metadata={
                    "source": source,
                    "page": page
                }
            )
        )

        start += (CHUNK_SIZE - CHUNK_OVERLAP)

    return chunks

for pdf_file in os.listdir(PDF_DIR):
    if not pdf_file.lower().endswith(".pdf"):
        continue

    print(f"Processing PDF: {pdf_file}")
    reader = PdfReader(os.path.join(PDF_DIR, pdf_file))

    for page_num, page in enumerate(reader.pages[:MAX_PAGES_PER_PDF]):
        raw_text = page.extract_text()
        if not raw_text or len(raw_text) < MIN_PAGE_CHARS:
            continue

        raw_text = clean_text(raw_text)

        page_chunks = chunk_text(
            raw_text,
            source=pdf_file,
            page=page_num + 1
        )

        documents.extend(page_chunks)

print(f"Total chunks created: {len(documents)}")

# Embeddings
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

faiss_index = faiss.IndexFlatL2(384)
vector_store = FaissVectorStore(faiss_index=faiss_index)

index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store,
    embed_model=embed_model,
)

index.storage_context.persist(persist_dir=INDEX_DIR)

print("FAISS index built with chunked PDFs")
