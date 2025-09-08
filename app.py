from fastapi import FastAPI

app = FastAPI(title="progresso-service")

@app.get("/")
def root():
    return {"service": "progresso", "status": "ok"}

@app.get("/health")
def health():
    return {"ok": True}