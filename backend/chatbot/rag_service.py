import os
import glob
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # type: ignore
# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma  # type: ignore
# pyrefly: ignore [missing-import]
from langchain_core.documents import Document  # type: ignore
# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore

load_dotenv()

logger = logging.getLogger("RAGService")
logging.basicConfig(level=logging.INFO)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PERSIST_DIR = os.path.join(CURRENT_DIR, "chroma_db")
KNOWLEDGE_BASE_DIR = os.path.join(CURRENT_DIR, "knowledge_base")
COLLECTION_NAME = "financial_advisor_knowledge"
EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")


class RAGService:
    """
    RAG Service managing ChromaDB vector store, Gemini embeddings, and document retrieval.
    """
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not set. Please set it in your .env file.")

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=self.api_key
        )

        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=80,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )

    def ingest_directory(self, directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Loads all markdown/text documents from the knowledge base directory, splits into chunks,
        and saves them into ChromaDB.
        """
        target_dir = directory_path or KNOWLEDGE_BASE_DIR
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            return {"status": "empty", "message": f"Knowledge base directory created at {target_dir}. Place documents inside to index.", "chunks_indexed": 0}

        doc_files = glob.glob(os.path.join(target_dir, "*.md")) + glob.glob(os.path.join(target_dir, "*.txt"))
        if not doc_files:
            return {"status": "empty", "message": "No .md or .txt files found in knowledge base.", "chunks_indexed": 0}

        all_documents: List[Document] = []
        for file_path in doc_files:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    chunks = self.text_splitter.split_text(content)
                    for idx, chunk in enumerate(chunks):
                        all_documents.append(
                            Document(
                                page_content=chunk,
                                metadata={
                                    "source": file_name,
                                    "chunk_id": idx,
                                    "category": file_name.replace(".md", "").replace(".txt", "").replace("_", " ")
                                }
                            )
                        )
            except Exception as e:
                logger.error(f"Error processing {file_name}: {e}")

        if all_documents:
            # Recreate vector store with fresh documents
            self.vector_store = Chroma.from_documents(
                documents=all_documents,
                embedding=self.embeddings,
                collection_name=COLLECTION_NAME,
                persist_directory=CHROMA_PERSIST_DIR
            )
            logger.info(f"Successfully indexed {len(all_documents)} chunks from {len(doc_files)} files.")
            return {
                "status": "success",
                "files_indexed": len(doc_files),
                "chunks_indexed": len(all_documents),
                "collection": COLLECTION_NAME
            }
        
        return {"status": "no_content", "chunks_indexed": 0}

    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches the Chroma vector store for chunks relevant to the user query.
        """
        try:
            results = self.vector_store.similarity_search_with_relevance_scores(query, k=top_k)
            retrieved_docs = []
            for doc, score in results:
                retrieved_docs.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Knowledge Base"),
                    "category": doc.metadata.get("category", "General"),
                    "relevance_score": round(float(score), 4) if score is not None else 1.0
                })
            return retrieved_docs
        except Exception as e:
            logger.warning(f"ChromaDB retrieval error (falling back to simple search): {e}")
            try:
                results = self.vector_store.similarity_search(query, k=top_k)
                return [{
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Knowledge Base"),
                    "category": doc.metadata.get("category", "General"),
                    "relevance_score": 1.0
                } for doc in results]
            except Exception as err:
                logger.error(f"Vector search failed: {err}")
                return []

    def format_retrieved_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves relevant documents and formats them as a clean prompt context block.
        """
        docs = self.retrieve_context(query, top_k=top_k)
        if not docs:
            return "No specific internal guidelines retrieved for this topic."

        formatted_chunks = []
        for i, doc in enumerate(docs, 1):
            source = doc.get("source", "Knowledge Base")
            category = doc.get("category", "General")
            formatted_chunks.append(
                f"[Source {i}: {source} ({category})]\n{doc['content']}"
            )

        return "\n\n---\n\n".join(formatted_chunks)

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns stats about the Chroma vector store collection.
        """
        try:
            count = self.vector_store._collection.count()
            return {
                "collection_name": COLLECTION_NAME,
                "total_indexed_chunks": count,
                "embedding_model": EMBEDDING_MODEL,
                "persist_directory": CHROMA_PERSIST_DIR
            }
        except Exception as e:
            return {"error": str(e), "total_indexed_chunks": 0}


# Global singleton instance
_rag_service: Optional[RAGService] = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
