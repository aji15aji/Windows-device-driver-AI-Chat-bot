import os

# MUST be set before llama_index imports
os.environ["LLAMA_INDEX_DISABLE_TIKTOKEN"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
