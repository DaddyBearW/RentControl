from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import models
from app.api import auth, equipment, rentals, admin

Base.metadata.create_all(bind=engine)
app = FastAPI(title="RentControl API", version="1.0.0", description="REST API системы аренды оборудования")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(equipment.router); app.include_router(rentals.router); app.include_router(admin.router)

@app.get("/api/health", tags=["Система"])
def health(): return {"status": "ok", "service": "RentControl API"}
