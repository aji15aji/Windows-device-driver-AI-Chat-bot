# backend/bridge.py
import sys
print("SYS.PATH:", sys.path)

def ask_backend(question: str) -> str:
    from backend.rag_answer import (
        ask_phi3,
        build_explanation_prompt,
        build_code_prompt,
        retriever,
        is_small_talk,
        is_driver_related,
        is_code_generation,
    )
    
    question = question.strip()

    if is_small_talk(question):
        return "Hi! Ask me anything about Windows device driver development."
    if not is_driver_related(question):
        return "Sorry. I can help only with Windows device driver development related questions."

    # Retrieve docs
    nodes = retriever.retrieve(question)

    if not nodes or all(len(n.text.strip()) < 50 for n in nodes):
        return "Not found in documentation which I have. Try rephrasing your question."

    is_code = is_code_generation(question)
    if is_code:
        prompt = build_code_prompt(question, nodes)
    else:
        prompt = build_explanation_prompt(question, nodes)

    return ask_phi3(prompt, code_mode=is_code)
