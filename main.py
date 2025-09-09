from fastapi import FastAPI
from app import create_app

app: FastAPI = create_app()

@app.get("/health")
def health():
    return {"ok": True}
