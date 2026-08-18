# RAG (Retrieval-Augmented Generation) Implementation

## Overview

The Financial Advisor chatbot uses RAG to combine customer-specific context with general financial knowledge from a curated knowledge base. This allows the chatbot to provide both personalized advice and accurate general financial information.

## Architecture

```
User Question
     ↓
Chatbot Service
     ↓
   ┌─────────────────────┬────────────────────┐
   ↓                     ↓                    ↓
Customer Context   RAG Service          Conversation
(Database)        (Vector DB)           History
   ↓                     ↓                    ↓
   └──────────────→ LLM (Groq) ←─────────────┘
                        ↓
                   AI Response
```

## Components

### 1. Knowledge Base
**Location**: `backend/app/genai/knowledge_base/`

Curated markdown files with financial planning knowledge:
- `budgeting_strategies.md` - Budgeting methods and tips
- `debt_management.md` - Debt repayment strategies
- `emergency_funds.md` - Emergency fund guidelines
- `investing_and_retirement.md` - Investment basics
- `tax_advantaged_accounts.md` - Tax-saving instruments

### 2. Vector Database
**Technology**: ChromaDB (local, persistent storage)
**Location**: `backend/app/genai/chroma_db/` (git-ignored)

**Features**:
- Stores document embeddings for semantic search
- Persists across application restarts
- Fast similarity search (~ms response time)

### 3. Embedding Model
**Model**: `all-MiniLM-L6-v2` (sentence-transformers)
**Dimensions**: 384
**Advantages**:
- Free and runs locally (no API calls)
- Fast inference (~30ms per query)
- Good quality for semantic search
- Small model size (~90MB)

### 4. RAG Service
**File**: `backend/app/genai/rag_service.py`

**Key Functions**:
```python
# Initialize and index knowledge base
initialize_rag()

# Retrieve relevant context for a query
rag_service.retrieve_context(query, top_k=3)

# Get formatted context for LLM prompt
rag_service.format_retrieved_context(query, top_k=3)

# Check system status
rag_service.get_stats()
```

## How It Works

### Indexing (Startup)

1. **Load Knowledge Base**: Reads all `.md` and `.txt` files from `knowledge_base/`
2. **Chunk Documents**: Splits documents into ~600 character chunks with 80 character overlap
3. **Generate Embeddings**: Creates vector representations using sentence-transformers
4. **Store in ChromaDB**: Saves embeddings with metadata (source, category, chunk_index)

### Retrieval (Runtime)

1. **User Query**: User asks a question (e.g., "What is an emergency fund?")
2. **Semantic Search**: Query is embedded and compared to stored vectors
3. **Retrieve Top-K**: Returns 3 most relevant chunks with similarity scores
4. **Format Context**: Chunks are formatted with source attribution
5. **Augment Prompt**: Retrieved context is added to LLM system prompt
6. **Generate Response**: LLM generates answer using both customer context and retrieved knowledge

### Example Flow

```
User: "What is an emergency fund?"
  ↓
RAG retrieves from knowledge base:
  - emergency_funds.md (chunk 1): "Emergency fund definition..."
  - emergency_funds.md (chunk 2): "How much to save..."
  - budgeting_strategies.md (chunk 3): "Building savings..."
  ↓
Customer context:
  - Monthly income: ₹80,000
  - Monthly expenses: ₹50,000
  - Current savings: ₹1,00,000
  ↓
LLM generates personalized response:
  "An emergency fund is money set aside for unexpected expenses.
   Based on your monthly expenses of ₹50,000, you should aim for
   ₹3,00,000 (6 months). You currently have ₹1,00,000, so you're
   one-third of the way there!"
```

## API Endpoints

### Get RAG Statistics
```bash
GET /api/v1/chat/rag/stats
Authorization: Bearer <token>

Response:
{
  "collection_name": "financial_advisor_knowledge",
  "total_indexed_chunks": 42,
  "embedding_model": "all-MiniLM-L6-v2",
  "persist_directory": "backend/app/genai/chroma_db",
  "status": "ready"
}
```

### Reinitialize RAG
```bash
POST /api/v1/chat/rag/reinitialize
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "files_indexed": 5,
  "chunks_indexed": 42,
  "collection": "financial_advisor_knowledge"
}
```

## Configuration

### Environment Variables

No additional configuration needed! RAG works out of the box.

### Customization

**Chunk Size**: Adjust in `rag_service.py`
```python
chunk_size = 600  # characters
chunk_overlap = 80  # characters
```

**Number of Retrieved Chunks**: Adjust in `chatbot.py`
```python
rag_context = rag_service.format_retrieved_context(user_message, top_k=3)
```

**Embedding Model**: Change in `rag_service.py`
```python
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Other options: all-mpnet-base-v2, etc.
```

## Adding New Knowledge

### Step 1: Create Markdown File
```bash
cd backend/app/genai/knowledge_base/
nano retirement_planning.md
```

### Step 2: Write Content
```markdown
# Retirement Planning

## Overview
Retirement planning involves...

## Key Strategies
1. Start early
2. Maximize contributions
3. Diversify investments
```

### Step 3: Reinitialize RAG
```bash
# Option 1: Restart backend (auto-indexes on startup)
# Option 2: Call API endpoint
curl -X POST http://localhost:8000/api/v1/chat/rag/reinitialize \
  -H "Authorization: Bearer <token>"
```

## Monitoring

### Check RAG Status
```python
from app.genai.rag_service import get_rag_service

rag = get_rag_service()
stats = rag.get_stats()
print(f"Indexed chunks: {stats['total_indexed_chunks']}")
print(f"Status: {stats['status']}")
```

### View Logs
```bash
# Backend logs show RAG initialization
grep "RAG" backend_logs.txt

# Expected output:
# INFO: Initializing RAG system...
# INFO: Successfully indexed 42 chunks from 5 files
# INFO: RAG initialization complete
```

## Troubleshooting

### Issue: "No chunks indexed"
**Cause**: Knowledge base directory is empty or files have no content
**Solution**: 
```bash
ls backend/app/genai/knowledge_base/*.md
# Ensure .md files exist and have content
```

### Issue: "RAG initialization failed"
**Cause**: Missing dependencies
**Solution**:
```bash
pip install chromadb sentence-transformers
```

### Issue: "Chatbot works but doesn't use knowledge base"
**Cause**: RAG initialized but retrieval failing silently
**Solution**: Check logs for RAG retrieval errors, verify stats endpoint

### Issue: "Slow responses"
**Cause**: First query downloads embedding model
**Solution**: Wait ~1 minute for model download (one-time), subsequent queries are fast

## Performance

- **Indexing**: ~2-5 seconds for 5 files (42 chunks)
- **Query**: ~30-50ms per semantic search
- **Memory**: ~200MB for model + vector DB
- **Storage**: ~5MB for embeddings (42 chunks)

## Benefits

✅ **Accurate General Knowledge**: Uses curated financial content
✅ **Personalized Advice**: Combines knowledge with customer data
✅ **No API Costs**: Runs locally, no embedding API needed
✅ **Fast**: Sub-second response times
✅ **Scalable**: Can handle thousands of documents
✅ **Maintainable**: Easy to add/update knowledge base files

## Future Enhancements

- Multi-language support (Hindi financial terms)
- Dynamic knowledge base updates without restart
- User feedback to improve retrieval quality
- Automatic knowledge base versioning
- Integration with external financial data sources
