"""
Document Loader Agent - Handles multi-format document ingestion
"""
import os
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
import sys
sys.path.append(str(Path(__file__).parent.parent))

from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStore
import config


class DocumentLoaderAgent:
    """Agent responsible for loading and processing documents"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.vector_store = VectorStore()
        logger.info("Document Loader Agent initialized")
    
    def load_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Load and process multiple documents
        
        Args:
            file_paths: List of paths to documents
            
        Returns:
            Processing results including success/failure status
        """
        results = {
            'success': [],
            'failed': [],
            'total_chunks': 0,
            'processed_docs': []
        }
        
        for file_path in file_paths:
            try:
                logger.info(f"Processing document: {file_path}")
                
                # Process the document
                processed = self.processor.process_document(file_path)
                
                # Extract all text
                full_text = self.processor.extract_all_text(processed)
                
                # Prepare for vector store
                doc_data = {
                    'text': full_text,
                    'filename': Path(file_path).name,
                    'source': 'uploaded',
                    'doc_type': 'medical',
                    'metadata': processed['metadata']
                }
                
                # Add to vector store
                chunk_ids = self.vector_store.add_documents([doc_data])
                
                results['success'].append(file_path)
                results['total_chunks'] += len(chunk_ids)
                results['processed_docs'].append({
                    'filename': Path(file_path).name,
                    'chunks': len(chunk_ids),
                    'has_tables': len(processed.get('tables', [])) > 0,
                    'has_images': len(processed.get('images', [])) > 0,
                    'metadata': processed['metadata']
                })
                
                logger.info(f"Successfully processed: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results['failed'].append({
                    'file': file_path,
                    'error': str(e)
                })
        
        logger.info(f"Document loading complete. Success: {len(results['success'])}, Failed: {len(results['failed'])}")
        return results
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded documents"""
        return self.vector_store.get_collection_stats()
    
    def clear_all_documents(self):
        """Clear all documents from the vector store"""
        self.vector_store.clear_collection()
        logger.info("All documents cleared from vector store")
