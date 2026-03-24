"""MedGuardX FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import auth_routes, upload, retrieve, preview, audit

app = FastAPI(
    title="MedGuardX",
    description="Healthcare Data Protection System with AI-based PII Detection & Context-Aware Masking",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router)
app.include_router(upload.router)
app.include_router(retrieve.router)
app.include_router(preview.router)
app.include_router(audit.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"name": "MedGuardX", "version": "1.0.0", "status": "running"}
