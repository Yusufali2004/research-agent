# CONTEXT.md — AI Research Paper Agent

## What We're Building
An AI agent that takes researcher's raw content (notes, data, references)
and a template (IEEE, APA, custom) and generates a complete research paper.

## Stack
- Frontend: Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
- Backend: FastAPI + SQLAlchemy + Alembic
- AI: Gemini 2.0 Flash + LangChain + ChromaDB + SentenceTransformers
- DB: Neon PostgreSQL
- Auth: JWT (python-jose)
- Deploy: Vercel (frontend) + Render (backend)

## Folder Structure
research-agent/
├── frontend/        # Next.js app
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── agents/
│   │   └── models/
│   ├── .env
│   ├── requirements.txt
│   └── Dockerfile
├── CONTEXT.md
├── README.md
└── docker-compose.yml

## Agent Pipeline
User uploads content + selects template
→ Parser Agent     (extracts sections, citations)
→ Research Agent   (structures content)
→ Writing Agent    (generates each section)
→ Formatting Agent (applies IEEE/APA template)
→ Export Agent     (outputs DOCX/PDF)

## Team Split
- Person 1: Frontend (Next.js, upload UI, paper preview, download)
- Person 2: Backend (FastAPI routes, DB, auth)
- Person 3: AI layer (LangChain agents, ChromaDB, prompt engineering)
- Person 4: Templates + export (DOCX/PDF generation, IEEE/APA formatting)

## Progress Tracker
- [x] Project structure created
- [ ] Next.js setup
- [ ] FastAPI base setup
- [ ] File upload endpoint
- [ ] LangChain agent pipeline
- [ ] ChromaDB integration
- [ ] Paper export (DOCX/PDF)
- [ ] Frontend upload UI
- [ ] Frontend paper preview
- [ ] Deployment

## Current Task
Setting up base project structure.

## Known Issues / Blockers
None yet.

## How to Run
### Backend
cd backend
python -m venv venv
venv/Scripts/activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend
cd frontend
npm install
npm run dev

## Prompt for New Claude Session
Read CONTEXT.md fully. That is the complete state of our project.
Continue from where the team left off.
Current task: [UPDATE THIS before sharing with new Claude]
Relevant code: [PASTE the file you're working on]