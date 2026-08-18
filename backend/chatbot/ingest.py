"""
Ingestion script to parse, embed, and index financial knowledge base documents into ChromaDB.
Usage: python ingest.py
"""
import os
import sys
from rag_service import get_rag_service

def main():
    print("=" * 60)
    print(" CogAdvisor Knowledge Base Ingestion Pipeline (ChromaDB + Gemini)")
    print("=" * 60)

    try:
        rag = get_rag_service()
        print("Initialized RAG Service with Google Gemini Embeddings...")
        
        result = rag.ingest_directory()
        print("\nIngestion Result:")
        for k, v in result.items():
            print(f" - {k}: {v}")

        stats = rag.get_stats()
        print(f"\nVector Store Status: {stats.get('total_indexed_chunks', 0)} chunks currently indexed.")
        print("Ready for RAG queries!\n")

    except Exception as e:
        print(f"\n[Error] Ingestion failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
