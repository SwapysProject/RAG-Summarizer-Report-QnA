"""
Orchestrator Agent - Central controller that coordinates all agents
"""
import time
from typing import Dict, Any, List
from loguru import logger
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from .document_loader import DocumentLoaderAgent
from .qa_agent import QAAgent
import config


class OrchestratorAgent:
    """Central agent that orchestrates workflow between specialized agents"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialize model for function calling
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL
        )
        
        # Initialize specialized agents
        self.document_loader = DocumentLoaderAgent()
        self.qa_agent = QAAgent()
        
        # Define available tools/functions
        self.tools = self._define_tools()
        
        logger.info("Orchestrator Agent initialized")
    
    def _define_tools(self) -> List[Dict]:
        """Define available tools for function calling"""
        return [
            {
                "name": "search_documents",
                "description": "Search through uploaded medical documents to find relevant information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query or question"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_document_stats",
                "description": "Get statistics about the uploaded documents collection",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def process_request(
        self,
        user_input: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process user request and route to appropriate agent
        
        Args:
            user_input: User's message
            chat_history: Previous conversation
            
        Returns:
            Response dictionary
        """
        try:
            time.sleep(config.REQUEST_DELAY_SECONDS)
            
            # Determine intent
            intent = self._determine_intent(user_input)
            
            if intent == 'qa':
                # Handle Q&A
                response = self.qa_agent.answer_question(
                    question=user_input,
                    chat_history=chat_history
                )
                return {
                    'type': 'qa',
                    'content': response['answer'],
                    'sources': response.get('sources', []),
                    'success': True
                }
            
            elif intent == 'stats':
                # Get document statistics
                stats = self.document_loader.get_document_stats()
                return {
                    'type': 'stats',
                    'content': f"Currently loaded documents: {stats['document_count']} chunks in collection '{stats['collection_name']}'",
                    'success': True
                }
            
            else:
                # General response
                return {
                    'type': 'general',
                    'content': "I'm here to help you with medical documents. You can ask me questions about the uploaded documents or request reports.",
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            return {
                'type': 'error',
                'content': f"An error occurred: {str(e)}",
                'success': False
            }
    
    def _determine_intent(self, user_input: str) -> str:
        """Determine user intent from input"""
        user_input_lower = user_input.lower()
        
        # Check for statistics requests
        if any(word in user_input_lower for word in ['how many', 'stats', 'statistics', 'count', 'loaded']):
            return 'stats'
        
        # Default to Q&A
        return 'qa'
    
    def load_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """Load documents using document loader agent"""
        return self.document_loader.load_documents(file_paths)
    
    def clear_documents(self):
        """Clear all loaded documents"""
        self.document_loader.clear_all_documents()
