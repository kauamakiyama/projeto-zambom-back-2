from typing import Final

USUARIOS_COL: Final[str]   = "usuarios"
ATIVIDADES_COL: Final[str] = "atividades"
MATRICULAS_COL: Final[str] = "matriculas"
PROGRESSO_COL: Final[str]  = "progresso"

# Helpers simples para montar filtros
def by_id_str(_id: str) -> dict:        # quando vier como string
    from bson import ObjectId
    return {"_id": ObjectId(_id)}

def by_cpf(cpf: str) -> dict:
    return {"cpf": cpf}
