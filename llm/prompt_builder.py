def build_rag_prompt(query: str, retrieved_documents: list) -> str:
    context = ""
    for i, doc in enumerate(retrieved_documents, 1):
        context += f"\n--- Document {i} ---\n"
        context += doc['content']
        context += f"\nSource: {doc['metadata'].get('category', 'unknown')}\n"
    
    prompt = f"""
You are a helpful Sri Lanka tourism assistant. Answer questions based ONLY on the provided context.

Guidelines:
- Be friendly, informative, and concise
- If the answer is not in the context, say: "I don't have that information in my database. Please contact a local tourism office."
- Never invent information
- Suggest related places when relevant
- Format answers with bullet points for lists

CONTEXT:
{context}

USER QUESTION: {query}

YOUR ANSWER:
"""
    return prompt

def build_simple_prompt(query: str) -> str:
    return f"""
You are a Sri Lanka tourism assistant. Answer briefly and helpfully.

USER: {query}
ASSISTANT:
"""