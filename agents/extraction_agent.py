"""
Extraction Agent - Extracts specific data, tables, and images from documents
"""
import time
from typing import List, Dict, Any
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore
from loguru import logger
import config


class ExtractionAgent:
    """Agent for extracting specific content from documents"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL
        )
        
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore()
        
        logger.info("Extraction Agent initialized")
    
    def extract_section(self, section_name: str) -> Dict[str, Any]:
        """
        Extract a specific section from documents
        
        Args:
            section_name: Name of the section to extract
            
        Returns:
            Extracted content
        """
        try:
            time.sleep(config.REQUEST_DELAY_SECONDS)
            
            # Search for section
            results = self.vector_store.similarity_search(
                query=f"Extract {section_name} section",
                k=5
            )
            
            if not results:
                return {
                    'section': section_name,
                    'content': '',
                    'found': False
                }
            
            # Combine relevant content
            content_parts = []
            for result in results:
                content_parts.append(result['content'])
            
            combined_content = '\n\n'.join(content_parts)
            
            return {
                'section': section_name,
                'content': combined_content,
                'found': True,
                'sources': [r['metadata'].get('filename', 'Unknown') for r in results]
            }
            
        except Exception as e:
            logger.error(f"Error extracting section: {e}")
            return {
                'section': section_name,
                'content': '',
                'found': False,
                'error': str(e)
            }
    
    def extract_tables(self) -> List[Dict[str, Any]]:
        """Extract all tables from uploaded documents"""
        # This would integrate with the document processor
        # to retrieve stored table data
        return []
    
    def extract_images(self) -> List[Dict[str, Any]]:
        """Extract all images from uploaded documents"""
        # This would integrate with the document processor
        # to retrieve stored image data
        return []
