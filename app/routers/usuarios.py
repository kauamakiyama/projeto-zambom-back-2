from fastapi import APIRouter, HTTPException, status
from app.schemas import Usuario, UsuarioCreate
from app.database import get_database

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/", response_model=Usuario, status_code=status.HTTP_201_CREATED)
async def criar_usuario(usuario: UsuarioCreate):
    db = get_database()
    existente = await db["usuarios"].find_one({"cpf": usuario.cpf})
    if existente:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    result = await db["usuarios"].insert_one(usuario.dict())
    return {"id": str(result.inserted_id), **usuario.dict()}

@router.get("/", response_model=list[Usuario])
async def listar_usuarios():
    db = get_database()
    out = []
    async for u in db["usuarios"].find():
        out.append({"id": str(u["_id"]), **{k: u.get(k) for k in [
            "nome","idade","email","cpf","endereco","numero","complemento","cep"
        ]}})
    return out

@router.get("/{cpf}", response_model=Usuario)
async def obter_usuario(cpf: str):
    db = get_database()
    u = await db["usuarios"].find_one({"cpf": cpf})
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"id": str(u["_id"]), **{k: u.get(k) for k in [
        "nome","idade","email","cpf","endereco","numero","complemento","cep"
    ]}}

@router.delete("/{cpf}", response_model=dict)
async def deletar_usuario(cpf: str):
    db = get_database()
    res = await db["usuarios"].delete_one({"cpf": cpf})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido com sucesso"}
