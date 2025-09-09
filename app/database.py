from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.database import Database
from pymongo import ASCENDING
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "atividades_db")

client: AsyncIOMotorClient | None = None
db: Database | None = None

def get_database() -> Database:
    assert db is not None, "DB não inicializado; chame connect_to_mongo()"
    return db

async def _ensure_indexes(database: Database) -> None:
    # Único CPF em usuários
    await database["usuarios"].create_index([("cpf", ASCENDING)], unique=True)
    # Nome de atividade único (se fizer sentido)
    await database["atividades"].create_index([("nome", ASCENDING)], unique=True)
    # Evita matrícula duplicada (mesmo cpf + mesma atividade)
    await database["matriculas"].create_index(
        [("cpf_usuario", ASCENDING), ("nome_atividade", ASCENDING)], unique=True
    )
    # Índices úteis para o progresso
    await database["progresso"].create_index([("cpf_usuario", ASCENDING), ("data", ASCENDING)])

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await _ensure_indexes(db)
    print("✅ Conectado ao MongoDB")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ Conexão MongoDB fechada")
