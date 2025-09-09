from fastapi import APIRouter, HTTPException, status
from app.schemas import Matricula, MatriculaCreate
from app.database import get_database
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

router = APIRouter(prefix="/matriculas", tags=["Matrículas"])

@router.post("/", response_model=Matricula, status_code=status.HTTP_201_CREATED)
async def criar_matricula(matricula: MatriculaCreate):
    db = get_database()

    usuario = await db["usuarios"].find_one({"cpf": matricula.cpf_usuario})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    atividade = await db["atividades"].find_one({"nome": matricula.nome_atividade})
    if not atividade:
        raise HTTPException(status_code=404, detail="Atividade não encontrada")

    try:
        res = await db["matriculas"].insert_one(matricula.dict())
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Matrícula já existe para este usuário/atividade")

    return {"id": str(res.inserted_id), **matricula.dict()}

@router.get("/", response_model=list[Matricula])
async def listar_matriculas():
    db = get_database()
    out = []
    async for m in db["matriculas"].find():
        out.append({"id": str(m["_id"]), "cpf_usuario": m["cpf_usuario"], "nome_atividade": m["nome_atividade"]})
    return out

@router.delete("/{matricula_id}", response_model=dict)
async def deletar_matricula(matricula_id: str):
    db = get_database()
    res = await db["matriculas"].delete_one({"_id": ObjectId(matricula_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")
    return {"message": "Matrícula removida com sucesso"}
