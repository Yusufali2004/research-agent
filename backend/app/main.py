from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes.upload import router as upload_router

app = FastAPI(
    title="ResearchMate AI",
    description="AI-powered research paper generation agent",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)

@app.get("/")
def root():
    return {"status": "ResearchMate AI backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}