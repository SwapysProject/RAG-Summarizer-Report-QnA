"""
Q&A Agent - Handles retrieval-augmented generation for conversational Q&A
"""
import time
from typing import List, Dict, Any
from loguru import logger
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from utils.vector_store import VectorStore
import config


class QAAgent:
    """Agent for question answering using RAG"""
    
    def __init__(self):
        # Configure Google Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": config.MAX_OUTPUT_TOKENS,
            }
        )
        
        # Initialize vector store
        self.vector_store = VectorStore()
        
        # Chat history
        self.chat_history = []
        
        logger.info("Q&A Agent initialized")
    
    def answer_question(
        self,
        question: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User's question
            chat_history: Previous conversation history
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Rate limiting
            time.sleep(config.REQUEST_DELAY_SECONDS)
            
            # Retrieve relevant documents
            relevant_docs = self.vector_store.similarity_search(
                query=question,
                k=config.TOP_K_RESULTS
            )
            
            if not relevant_docs:
                return {
                    'answer': "I couldn't find relevant information in the uploaded documents to answer your question. Please make sure you've uploaded the necessary medical documents.",
                    'sources': [],
                    'confidence': 'low'
                }
            
            # Build context from retrieved documents
            context = self._build_context(relevant_docs)
            
            # Build chat history context
            history_context = ""
            if chat_history:
                history_context = self._build_history_context(chat_history[-5:])  # Last 5 turns
            
            # Create prompt
            prompt = self._create_rag_prompt(question, context, history_context)
            
            # Generate answer
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Extract sources
            sources = self._extract_sources(relevant_docs)
            
            logger.info(f"Question answered successfully")
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': 'high' if len(relevant_docs) >= 3 else 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc['content']
            source = doc['metadata'].get('filename', 'Unknown')
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _build_history_context(self, history: List[Dict[str, str]]) -> str:
        """Build context from chat history"""
        history_parts = []
        
        for turn in history:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            
            if role == 'user':
                history_parts.append(f"User: {content}")
            else:
                history_parts.append(f"Assistant: {content}")
        
        return "\n".join(history_parts)
    
    def _create_rag_prompt(
        self,
        question: str,
        context: str,
        history: str = ""
    ) -> str:
        """Create RAG prompt"""
        
        prompt = f"""You are a helpful medical document assistant. Answer the user's question based on the provided context from uploaded medical documents.

Instructions:
- Use ONLY information from the provided context to answer the question
- If the context doesn't contain enough information, say so clearly
- Be precise and cite specific details from the documents
- Maintain a professional medical tone
- If previous conversation history is provided, maintain context continuity

Previous Conversation:
{history if history else "No previous conversation"}

Context from Documents:
{context}

User Question: {question}

Answer:"""
        
        return prompt
    
    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract source information"""
        sources = []
        seen_sources = set()
        
        for doc in documents:
            filename = doc['metadata'].get('filename', 'Unknown')
            
            if filename not in seen_sources:
                sources.append({
                    'filename': filename,
                    'score': f"{doc['score']:.2f}"
                })
                seen_sources.add(filename)
        
        return sources
