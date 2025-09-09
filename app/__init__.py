from fastapi import FastAPI
from .database import connect_to_mongo, close_mongo_connection
from .routers import usuarios, atividades, matriculas, progresso

def create_app() -> FastAPI:
    app = FastAPI(title="Zambom API", version="1.0.0")

    # Routers
    app.include_router(usuarios.router)
    app.include_router(atividades.router)
    app.include_router(matriculas.router)
    app.include_router(progresso.router)

    @app.on_event("startup")
    async def _startup():
        await connect_to_mongo()

    @app.on_event("shutdown")
    async def _shutdown():
        await close_mongo_connection()

    return app
