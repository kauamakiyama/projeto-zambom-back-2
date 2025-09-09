from fastapi import APIRouter, HTTPException
from app.schemas import Atividade, AtividadeCreate
from app.database import get_database
from bson import ObjectId

router = APIRouter(prefix="/atividades", tags=["Atividades"])

@router.post("/", response_model=Atividade)
async def criar_atividade(atividade: AtividadeCreate):
    db = get_database()
    # opcional: evitar nomes duplicados
    existe = await db["atividades"].find_one({"nome": atividade.nome})
    if existe:
        raise HTTPException(status_code=400, detail="Atividade já existe")
    result = await db["atividades"].insert_one(atividade.dict())
    return {"id": str(result.inserted_id), **atividade.dict()}

@router.get("/", response_model=list[Atividade])
async def listar_atividades():
    db = get_database()
    out = []
    async for a in db["atividades"].find():
        out.append({"id": str(a["_id"]), "nome": a["nome"], "descricao": a["descricao"]})
    return out

@router.get("/{atividade_id}", response_model=Atividade)
async def obter_atividade(atividade_id: str):
    db = get_database()
    a = await db["atividades"].find_one({"_id": ObjectId(atividade_id)})
    if not a:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return {"id": str(a["_id"]), "nome": a["nome"], "descricao": a["descricao"]}

@router.put("/{atividade_id}", response_model=Atividade)
async def atualizar_atividade(atividade_id: str, atividade: AtividadeCreate):
    db = get_database()
    res = await db["atividades"].update_one({"_id": ObjectId(atividade_id)}, {"$set": atividade.dict()})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    a = await db["atividades"].find_one({"_id": ObjectId(atividade_id)})
    return {"id": str(a["_id"]), "nome": a["nome"], "descricao": a["descricao"]}

@router.delete("/{atividade_id}", response_model=dict)
async def deletar_atividade(atividade_id: str):
    db = get_database()
    res = await db["atividades"].delete_one({"_id": ObjectId(atividade_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")
    return {"message": "Atividade removida com sucesso"}
