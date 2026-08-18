"""
RAG (Retrieval-Augmented Generation) Service for Financial Advisor Chatbot.

Uses ChromaDB for vector storage and sentence-transformers for embeddings.
Provides semantic search over financial knowledge base documents.
"""

import os
import glob
import logging
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_DIR = os.path.join(CURRENT_DIR, "knowledge_base")
CHROMA_PERSIST_DIR = os.path.join(CURRENT_DIR, "chroma_db")
COLLECTION_NAME = "financial_advisor_knowledge"

# Embedding model - using a small, efficient model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast and efficient


class RAGService:
    """
    RAG Service managing ChromaDB vector store with sentence-transformer embeddings.
    
    Responsibilities:
    - Index knowledge base documents into vector database
    - Perform semantic search for relevant context
    - Format retrieved context for LLM prompts
    """
    
    def __init__(self, persist_directory: str = CHROMA_PERSIST_DIR):
        """
        Initialize RAG service with ChromaDB and sentence-transformers.
        
        Args:
            persist_directory: Path to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Initialize sentence transformer for embeddings
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Create embedding function for ChromaDB
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            logger.info(f"Loaded existing collection: {COLLECTION_NAME}")
        except Exception:
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"description": "Financial advisor knowledge base"}
            )
            logger.info(f"Created new collection: {COLLECTION_NAME}")
    
    def ingest_knowledge_base(
        self,
        directory_path: Optional[str] = None,
        chunk_size: int = 600,
        chunk_overlap: int = 80
    ) -> Dict[str, Any]:
        """
        Load and index all markdown/text documents from knowledge base directory.
        
        Args:
            directory_path: Path to knowledge base (defaults to ./knowledge_base)
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between consecutive chunks
            
        Returns:
            Dictionary with indexing statistics
        """
        target_dir = directory_path or KNOWLEDGE_BASE_DIR
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            return {
                "status": "empty",
                "message": f"Knowledge base directory created at {target_dir}",
                "chunks_indexed": 0
            }
        
        # Find all markdown and text files
        doc_files = glob.glob(os.path.join(target_dir, "*.md")) + \
                    glob.glob(os.path.join(target_dir, "*.txt"))
        
        if not doc_files:
            return {
                "status": "empty",
                "message": "No .md or .txt files found in knowledge base",
                "chunks_indexed": 0
            }
        
        # Process each document
        documents = []
        metadatas = []
        ids = []
        chunk_counter = 0
        
        for file_path in doc_files:
            file_name = os.path.basename(file_path)
            category = file_name.replace(".md", "").replace(".txt", "").replace("_", " ").title()
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                
                if not content:
                    continue
                
                # Simple chunking by sections and paragraphs
                chunks = self._chunk_text(content, chunk_size, chunk_overlap)
                
                for idx, chunk in enumerate(chunks):
                    if len(chunk.strip()) < 50:  # Skip very short chunks
                        continue
                    
                    documents.append(chunk)
                    metadatas.append({
                        "source": file_name,
                        "category": category,
                        "chunk_index": idx
                    })
                    ids.append(f"{file_name}_{idx}")
                    chunk_counter += 1
                    
            except Exception as e:
                logger.error(f"Error processing {file_name}: {e}")
        
        if documents:
            # Clear existing collection and add new documents
            try:
                self.client.delete_collection(name=COLLECTION_NAME)
                self.collection = self.client.create_collection(
                    name=COLLECTION_NAME,
                    embedding_function=self.embedding_function,
                    metadata={"description": "Financial advisor knowledge base"}
                )
            except Exception as e:
                logger.warning(f"Could not clear collection: {e}")
            
            # Add documents in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_metas = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
            
            logger.info(f"Successfully indexed {len(documents)} chunks from {len(doc_files)} files")
            return {
                "status": "success",
                "files_indexed": len(doc_files),
                "chunks_indexed": len(documents),
                "collection": COLLECTION_NAME
            }
        
        return {
            "status": "no_content",
            "chunks_indexed": 0
        }
    
    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 600,
        chunk_overlap: int = 80
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        # Split by double newlines first (paragraphs/sections)
        sections = text.split("\n\n")
        
        chunks = []
        current_chunk = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # If adding this section exceeds chunk_size, save current and start new
            if len(current_chunk) + len(section) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap from end of previous chunk
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = overlap_text + "\n\n" + section
            else:
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search vector store for chunks relevant to the query.
        
        Args:
            query: User's question or search query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with content, source, category, and relevance score
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            retrieved_docs = []
            
            if results and results["documents"] and results["documents"][0]:
                for idx, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][idx] if results["metadatas"] else {}
                    distance = results["distances"][0][idx] if results["distances"] else 0.0
                    
                    # Convert distance to similarity score (lower distance = higher similarity)
                    similarity = 1.0 / (1.0 + distance)
                    
                    retrieved_docs.append({
                        "content": doc,
                        "source": metadata.get("source", "Knowledge Base"),
                        "category": metadata.get("category", "General"),
                        "relevance_score": round(similarity, 4)
                    })
            
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def format_retrieved_context(
        self,
        query: str,
        top_k: int = 3
    ) -> str:
        """
        Retrieve relevant documents and format as prompt context.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            
        Returns:
            Formatted string with retrieved context
        """
        docs = self.retrieve_context(query, top_k=top_k)
        
        if not docs:
            return "No relevant knowledge base articles found for this query."
        
        formatted_chunks = []
        for i, doc in enumerate(docs, 1):
            source = doc.get("source", "Knowledge Base")
            category = doc.get("category", "General")
            score = doc.get("relevance_score", 0.0)
            
            formatted_chunks.append(
                f"**[Source {i}: {category}]** (Relevance: {score:.2f})\n{doc['content']}"
            )
        
        return "\n\n---\n\n".join(formatted_chunks)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": COLLECTION_NAME,
                "total_indexed_chunks": count,
                "embedding_model": EMBEDDING_MODEL,
                "persist_directory": self.persist_directory,
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "error": str(e),
                "total_indexed_chunks": 0,
                "status": "error"
            }


# Global singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get or create the global RAG service instance.
    
    Returns:
        RAGService singleton instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def initialize_rag() -> Dict[str, Any]:
    """
    Initialize RAG service and index knowledge base.
    
    Returns:
        Dictionary with initialization results
    """
    try:
        rag = get_rag_service()
        result = rag.ingest_knowledge_base()
        logger.info(f"RAG initialization: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to initialize RAG: {e}")
        return {
            "status": "error",
            "message": str(e),
            "chunks_indexed": 0
        }
