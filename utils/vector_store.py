"""
Vector store operations using ChromaDB
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from loguru import logger
import config


def _filter_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter metadata to only include simple types supported by ChromaDB
    (str, int, float, bool)
    """
    filtered = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            filtered[key] = value
        elif isinstance(value, (list, tuple, dict)):
            # Skip complex types
            continue
        else:
            # Convert other types to string
            try:
                filtered[key] = str(value)
            except:
                continue
    return filtered


class VectorStore:
    """Manage vector database operations"""
    
    def __init__(self):
        self.collection_name = config.COLLECTION_NAME
        self.persist_directory = str(config.VECTOR_DB_DIR)
        
        # Initialize embeddings
        if config.USE_LOCAL_EMBEDDINGS:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=config.LOCAL_EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        else:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                google_api_key=config.GOOGLE_API_KEY
            )
        
        # Initialize vector store
        self.vectorstore = None
        self._initialize_vectorstore()
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store"""
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
            
        Returns:
            List of document IDs
        """
        try:
            # Prepare documents for ingestion
            texts = []
            metadatas = []
            
            for doc in documents:
                # Split text into chunks
                chunks = self.text_splitter.split_text(doc['text'])
                
                for chunk in chunks:
                    texts.append(chunk)
                    # Prepare metadata and filter out complex types
                    base_metadata = {
                        'filename': doc.get('filename', 'unknown'),
                        'source': doc.get('source', 'uploaded'),
                        'doc_type': doc.get('doc_type', 'medical'),
                        **doc.get('metadata', {})
                    }
                    # Filter complex metadata (tuples, lists, dicts, etc.)
                    filtered_metadata = _filter_metadata(base_metadata)
                    metadatas.append(filtered_metadata)
            
            # Add to vector store
            ids = self.vectorstore.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(ids)} chunks to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        k: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filters
            
        Returns:
            List of matching documents with scores
        """
        if k is None:
            k = config.TOP_K_RESULTS
        
        try:
            # Perform similarity search with scores
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def get_retriever(self, k: int = None):
        """Get a retriever for RAG pipeline"""
        if k is None:
            k = config.TOP_K_RESULTS
        
        return self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Delete the collection
            client = chromadb.PersistentClient(path=self.persist_directory)
            try:
                client.delete_collection(name=self.collection_name)
                logger.info(f"Cleared collection: {self.collection_name}")
            except:
                pass
            
            # Reinitialize
            self._initialize_vectorstore()
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                'document_count': count,
                'collection_name': self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'document_count': 0, 'collection_name': self.collection_name}
