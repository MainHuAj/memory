# MemoryLayer

**A universal persistent memory layer for LLMs.**

MemoryLayer gives Claude long-term memory across conversations. It stores what you discuss, extracts key facts using an LLM, and retrieves the most relevant context automatically in future sessions — so your AI always knows who you are and what you're working on.

🌐 **[Live Demo & Setup Guide](https://mainhuaj.github.io/memory)**

---

## The Problem

Every time you start a new conversation with Claude, it has zero memory of who you are, what you're building, or what you discussed yesterday. You repeat yourself constantly. MemoryLayer fixes this.

---

## How It Works

```
User says "save this conversation"
              ↓
LLaMA 3.3 70B extracts facts + summary from the conversation
              ↓
Each fact stored as a semantic vector in Qdrant Cloud
              ↓
Next session: user asks a question
              ↓
MemoryLayer retrieves the most relevant facts (semantic search + time decay)
              ↓
Claude answers with full context from past sessions
```

---

## Features

| Feature | Description |
|---|---|
| 🧠 **Fact Extraction** | Conversations distilled into specific, searchable facts using LLaMA 3.3 70B — not vague summaries |
| 🔍 **Semantic Search** | Memories retrieved by meaning, not keywords. Ask naturally. |
| ⏱️ **Time Decay** | Recent memories rank higher. Old, irrelevant ones fade automatically. |
| 🔁 **Duplicate Detection** | Similarity above 90% is detected and skipped. Zero noise in your memory store. |
| 📊 **Importance Scoring** | Each memory gets an importance score (0.1–1.0) factored into retrieval ranking. |
| 🔐 **Secure Auth** | Every user has an isolated memory space via Supabase authentication. |
| 🤖 **MCP Native** | Works out of the box with Claude Desktop via the MCP protocol. |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Vector Database | Qdrant Cloud |
| Embeddings | HuggingFace Inference API — `all-MiniLM-L6-v2` (384 dimensions, cosine similarity) |
| LLM | Groq — `LLaMA 3.3 70B` (fact extraction + summarization) |
| Auth | Supabase |
| Deployment | Railway |
| MCP Server | FastMCP |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/signup` | Create a new user account |
| `POST` | `/login` | Login and get a JWT token |
| `POST` | `/store` | Extract facts from a conversation and store in Qdrant |
| `POST` | `/retrieve` | Semantic search for relevant memories |
| `DELETE` | `/delete/{memory_id}` | Delete a specific memory (with ownership verification) |
| `GET` | `/memories` | Paginated list of all memories for the authenticated user |
| `GET` | `/health` | Health check |

All endpoints except `/signup`, `/login`, and `/health` require a Bearer token in the `Authorization` header.

---

## Project Structure

```
memory/
├── main.py          # FastAPI endpoints
├── memory.py        # Qdrant store/retrieve/delete/scroll functions
├── summarize.py     # Groq fact extraction (LLaMA 3.3 70B)
├── auth.py          # Supabase JWT verification
├── mcp_server.py    # FastMCP server for Claude Desktop
├── index.html       # Landing page
└── .env             # Environment variables (not committed)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- [Qdrant Cloud](https://cloud.qdrant.io) account (free tier)
- [Groq](https://console.groq.com) API key (free tier)
- [HuggingFace](https://huggingface.co) API key (free tier)
- [Supabase](https://supabase.com) project (free tier)

### 1. Clone the repo

```bash
git clone https://github.com/MainHuAj/memory.git
cd memory
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn qdrant-client sentence-transformers groq supabase python-dotenv requests fastmcp
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
HF_API_KEY=your_huggingface_api_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
```

### 4. Run the API

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 5. Connect to Claude Desktop

Add the following to your `claude_desktop_config.json`:

**macOS path:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows path:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "Memory-Layer": {
      "command": "python",
      "args": ["/full/path/to/mcp_server.py"],
      "env": {
        "MEMORY_EMAIL": "your@email.com",
        "MEMORY_PASSWORD": "yourpassword",
        "RAILWAY_URL": "https://memory-production-d533.up.railway.app"
      }
    }
  }
}
```

Replace `/full/path/to/mcp_server.py` with the actual path on your machine. Restart Claude Desktop after saving.

---

## Usage

**Saving a conversation:**
```
"Save this conversation to memory"
"Remember this"
"Store this to memory"
```

**Retrieving memories:**
```
"What do you know about me? Load from memory."
"Do you remember what we discussed about my project?"
```

Claude will automatically call the MCP tools to store and retrieve memories.

---

## Deployment

This project is deployed on Railway. To deploy your own instance:

1. Fork this repo
2. Create a new Railway project and connect your fork
3. Add all environment variables from `.env` to Railway's Variables tab
4. Railway will auto-deploy on every push to `main`

---

## Privacy Notice

Conversations processed by MemoryLayer are sent to third-party services (Groq, HuggingFace) for fact extraction and embedding. Do not send sensitive personal information, passwords, financial data, or confidential business information through MemoryLayer.

---

## Roadmap

- [ ] Browser extension for ChatGPT and Gemini support
- [ ] Memory expiry / forgetting mechanism
- [ ] Rate limiting
- [ ] Memory categories and filtering
- [ ] Dashboard UI to view, search, and delete memories

---

## Author

**Abhinav Bhatera**  
Final year B.Tech Computer Science student passionate about ML engineering and building useful AI tools.

[![GitHub](https://img.shields.io/badge/GitHub-MainHuAj-181717?style=flat&logo=github)](https://github.com/MainHuAj)

---

## License

MIT License — free to use, modify, and distribute.
