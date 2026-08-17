# Production RAG AI Assistant — Backend API

Production-ready backend for a Retrieval-Augmented Generation (RAG) system built with **FastAPI**, **PostgreSQL (`pgvector`)**, and **Google Gemini API**. It processes PDF documents, creates semantic vector embeddings, performs similarity searches, and streams grounded AI responses.

🔗 **Frontend Repository**: [PriskySimbar/production-rag-oriented-ui](https://github.com/PriskySimbar/production-rag-oriented-ui)  
🚀 **Live Web App Demo**: [https://production-rag-oriented-ui.vercel.app](https://production-rag-oriented-ui.vercel.app/)

---

## 🏛️ System Architecture

```
[ PDF Upload ] ──> [ Text Extraction (pypdf) ] ──> [ Chunking & Overlap ]
                                                            │
                                                            ▼
[ pgvector (Neon DB) ] <── [ Vector Embedding (Gemini) ] <──┘
         │
         │ (Cosine Similarity Search Top-K)
         ▼
[ Context Augmentation ] + [ Conversation History ]
         │
         ▼
[ Google Gemini LLM ] ──> [ Real-time Token Streaming (text/plain) ]
```

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [`pgvector`](https://github.com/pgvector/pgvector) extension (Hosted on Neon)
- **ORM & Migrations**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/)
- **Embedding & LLM**: [Google GenAI SDK](https://github.com/google/generative-ai-python) (`gemini-embedding-001` & `gemini-3.6-flash`)
- **PDF Processing**: [pypdf](https://pypdf.readthedocs.io/)
- **Server**: [Uvicorn](https://www.uvicorn.org/) (ASGI)
- **Containerization**: Docker (Lightweight multi-stage Linux container)

---

## 📦 API Reference

### Health Check
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status check |

### Documents Management
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/documents/upload` | Upload PDF file (`multipart/form-data`), extract text, chunk, and index embeddings |
| `GET` | `/documents` | List all indexed documents with metadata and timestamps |
| `DELETE` | `/documents/{id}` | Delete document and cascade delete all associated chunks and embeddings |

### Conversations & RAG Streaming
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/conversations` | Create a new conversation session |
| `GET` | `/conversations/{id}` | Retrieve chat history for a conversation |
| `POST` | `/conversations/{id}/messages` | Send query, perform similarity retrieval, and stream response (`text/plain`) |

---

## ⚙️ Environment Variables

Create a `.env` file in the root backend directory:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
GEMINI_API_KEY=your_gemini_api_key_here

GEMINI_MODEL=gemini-3.6-flash
EMBEDDING_MODEL=gemini-embedding-001

TOP_K_RETRIEVAL=20
TOP_K_FINAL=5

CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 🚀 Local Development Setup

### 1. Clone & Create Virtual Environment
```bash
git clone https://github.com/PriskySimbar/production-rag-oriented.git
cd production-rag-oriented

python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Apply Database Migrations
```bash
alembic upgrade head
```

### 4. Run the Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at `http://localhost:8000/docs`.

---

## 🐳 Docker & Production Deployment

Build and run using Docker:

```bash
docker build -t production-rag-backend .
docker run -p 8080:8080 --env-file .env production-rag-backend
```

---

## 📄 License
MIT License. Feel free to use and adapt for your own production systems.
