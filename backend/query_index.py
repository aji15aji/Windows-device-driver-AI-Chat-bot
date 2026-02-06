from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Explicitly set embedding model (offline)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# IMPORTANT: Disable LLM completely
Settings.llm = None

# Load FAISS index
storage_context = StorageContext.from_defaults(
    persist_dir="../embeddings/faiss_index"
)
index = load_index_from_storage(storage_context)

# Use retriever directly (NO LLM)
retriever = index.as_retriever(similarity_top_k=3)

questions = [
    "What is DriverEntry?",
    "Explain KMDF",
    "What is IRQL?"
]

for q in questions:
    print("\n" + "=" * 80)
    print(f"QUESTION: {q}")

    nodes = retriever.retrieve(q)

    for i, node in enumerate(nodes, 1):
        print(f"\n--- Retrieved Chunk {i} ---")
        print(f"Source: {node.metadata.get('source')} | Page: {node.metadata.get('page')}")
        print(node.text[:800])
