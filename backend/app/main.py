from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes.upload import router as upload_router
from app.routes.generate import router as generate_router
from app.routes.export import router as export_router


app = FastAPI(
    title="ResearchMate AI",
    description="AI-powered research paper generation agent",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://research-agent-ecru.vercel.app", # Fixed syntax: added quotes and removed trailing slash for safety
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)
app.include_router(generate_router)
app.include_router(export_router)


@app.get("/")
def root():
    return {"status": "ResearchMate AI backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}