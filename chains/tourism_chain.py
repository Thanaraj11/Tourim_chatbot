from typing import Dict, Any
from memory.chat_memory import ChatMemory
from classifier.query_classifier import QueryClassifier, IntentType
from retrieval.retriever import Retriever
from retrieval.metadata_filters import MetadataFilter
from retrieval.reranker import Reranker
from llm.llm import LLM
from prompts.prompt_templates import build_contextual_prompt, build_followup_prompt, build_fallback_prompt

class TourismChain:
    """
    Orchestrates the entire RAG pipeline with memory and classification
    """
    
    def __init__(self, retriever: Retriever, llm: LLM, memory: ChatMemory):
        self.retriever = retriever
        self.llm = llm
        self.memory = memory
        self.classifier = QueryClassifier(llm)
        self.metadata_filter = MetadataFilter()
        self.reranker = Reranker()
        self.previous_intent = None
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Main chain execution
        """
        # 1. Classify the query with conversation context
        conversation_history = self.memory.get_recent_messages(6)
        classification = self.classifier.classify(query, conversation_history)
        intent = classification["intent"]
        entities = classification.get("entities", {})
        
        # 2. Build metadata filter based on intent
        where_filter = self.metadata_filter.build_filter(
            intent, 
            entities, 
            self.previous_intent
        )
        
        # 3. Get search limit based on intent
        top_k = self.metadata_filter.get_search_limit(intent)
        
        # 4. Retrieve documents with filter
        retrieved_docs = self.retriever.retrieve(
            query, 
            top_k=top_k,
            where_filter=where_filter
        )
        
        # 5. Handle follow-up specially if needed
        is_followup = (intent == IntentType.FOLLOWUP_QUERY)
        
        # 6. Re-rank documents
        if retrieved_docs and len(retrieved_docs) > 0:
            retrieved_docs = self.reranker.rerank(retrieved_docs, query, intent.value)
        else:
            retrieved_docs = []
        
        # 7. Build prompt based on context
        if is_followup:
            previous_question = self.memory.get_last_user_query()
            previous_answer = self.memory.get_last_assistant_response()
            
            if previous_question and previous_answer:
                prompt = build_followup_prompt(
                    query, 
                    previous_question, 
                    previous_answer,
                    intent.value
                )
            else:
                prompt = build_contextual_prompt(
                    query, 
                    retrieved_docs, 
                    self.memory.get_conversation_summary(),
                    intent.value
                )
        elif not retrieved_docs or len(retrieved_docs) == 0:
            prompt = build_fallback_prompt(query)
        else:
            prompt = build_contextual_prompt(
                query, 
                retrieved_docs, 
                self.memory.get_conversation_summary(),
                intent.value
            )
        
        # 8. Generate answer
        answer = self.llm.generate(prompt)
        
        # 9. Update memory
        self.memory.add_message("user", query, {"intent": intent.value})
        self.memory.add_message("assistant", answer, {
            "intent": intent.value,
            "retrieved_count": len(retrieved_docs)
        })
        
        # 10. Update context variables
        if entities.get("locations"):
            self.memory.update_context("current_location", entities["locations"][0])
        
        # Store current topic
        current_topic = self.memory.get_current_topic()
        if current_topic:
            self.memory.update_context("current_topic", current_topic)
        
        # Store intent for next follow-up
        self.previous_intent = intent
        
        # 11. Prepare response
        return {
            "query": query,
            "answer": answer,
            "intent": intent.value,
            "confidence": classification.get("confidence", 0.7),
            "sources": [
                {
                    "content": doc['content'][:200] + "...",
                    "category": doc.get('metadata', {}).get('category'),
                    "relevance": doc.get('reranked_score', doc.get('relevance_score', 0))
                }
                for doc in retrieved_docs[:3]
            ] if retrieved_docs else [],
            "entities": entities
        }