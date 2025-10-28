"""
Summarization Agent - Creates summaries of document content
"""
import time
from typing import Dict, Any
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from utils.vector_store import VectorStore
from loguru import logger
import config


class SummarizationAgent:
    """Agent for generating summaries"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config={
                "temperature": 0.3,  # Lower temperature for more focused summaries
                "top_p": 0.8,
                "max_output_tokens": config.MAX_OUTPUT_TOKENS,
            }
        )
        
        self.vector_store = VectorStore()
        
        logger.info("Summarization Agent initialized")
    
    def generate_summary(self, max_length: int = 500) -> Dict[str, Any]:
        """
        Generate a summary of all uploaded documents
        
        Args:
            max_length: Maximum length of summary in words
            
        Returns:
            Summary content
        """
        try:
            time.sleep(config.REQUEST_DELAY_SECONDS)
            
            # Get sample content from documents
            results = self.vector_store.similarity_search(
                query="main findings clinical data patient information key results",
                k=10
            )
            
            if not results:
                return {
                    'content': "No document content available for summarization.",
                    'success': False
                }
            
            # Combine content
            content_parts = []
            for result in results:
                content_parts.append(result['content'])
            
            combined_content = '\n\n'.join(content_parts)
            
            # Create summarization prompt
            prompt = f"""You are a medical documentation specialist. Create a concise professional summary of the following medical document content.

Instructions:
- Focus on key findings, clinical data, and important information
- Keep the summary to approximately {max_length} words
- Use professional medical terminology
- Organize information clearly
- Highlight the most important points

Content to summarize:
{combined_content[:15000]}  # Limit to avoid token overflow

Summary:"""
            
            # Generate summary
            response = self.model.generate_content(prompt)
            summary = response.text
            
            return {
                'content': summary,
                'success': True,
                'word_count': len(summary.split())
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                'content': f"Error generating summary: {str(e)}",
                'success': False
            }
    
    def summarize_section(self, section_content: str) -> str:
        """
        Summarize a specific section
        
        Args:
            section_content: Content to summarize
            
        Returns:
            Summarized content
        """
        try:
            time.sleep(config.REQUEST_DELAY_SECONDS)
            
            prompt = f"""Summarize the following medical document section concisely:

{section_content[:10000]}

Summary:"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error in section summarization: {e}")
            return section_content  # Return original if summarization fails
