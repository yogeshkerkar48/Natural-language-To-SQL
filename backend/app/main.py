from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NLP to SQL API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

@app.get("/")
def read_root():
    return {"message": "Welcome to NL2SQL API"}
