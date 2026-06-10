from .system_prompt import get_system_prompt

def build_contextual_prompt(query: str, retrieved_docs: list, memory_summary: str, intent: str) -> str:
    """Build prompt with full context including memory and intent"""
    
    # Build context section
    context = ""
    for i, doc in enumerate(retrieved_docs, 1):
        context += f"\n[Document {i} - Category: {doc['metadata'].get('category', 'unknown')}]\n"
        context += doc['content']
        context += "\n" + "-" * 40 + "\n"
    
    # Build conversation memory section
    memory_section = ""
    if memory_summary:
        memory_section = f"""
Previous conversation context:
{memory_summary}
"""
    
    # Intent-specific instructions
    intent_instructions = {
        "price": "Focus on extracting and clearly stating any pricing information. If exact prices aren't available, provide ranges or suggest contacting the property.",
        "comparison": "Compare the mentioned items clearly, listing pros and cons. Use a table format if comparing 2-3 items.",
        "recommendation": "Provide 2-3 top recommendations with clear reasoning. Consider user's implied preferences from conversation history.",
        "hotel": "Include price range, location, and key amenities. Mention proximity to attractions if relevant.",
        "place": "Include historical significance, best time to visit, entry fee, and any unique features."
    }
    
    intent_instruction = intent_instructions.get(intent, "Provide a clear, helpful response based on the context.")
    
    prompt = f"""{get_system_prompt()}

{memory_section}

User Intent: {intent}
{intent_instruction}

Retrieved Information:
{context}

Current User Question: {query}

Assistant Response:"""
    
    return prompt

def build_followup_prompt(query: str, previous_question: str, previous_answer: str, intent: str) -> str:
    """Special prompt for follow-up questions with context"""
    
    prompt = f"""{get_system_prompt()}

Context from previous exchange:
User previously asked: "{previous_question}"
Assistant answered: "{previous_answer}"

Now user asks (follow-up): "{query}"

This is a follow-up question. Refer to the previous exchange to provide a relevant answer.

Current User Question: {query}

Assistant Response:"""
    
    return prompt

def build_fallback_prompt(query: str) -> str:
    """Prompt for when no relevant documents are found"""
    
    return f"""{get_system_prompt()}

I checked my tourism database but couldn't find specific information about: "{query}"

Please respond naturally by:
1. Apologizing that the information isn't available
2. Suggesting alternative related topics I can help with
3. Offering to connect with a local tourism office for specific inquiries

My response:"""