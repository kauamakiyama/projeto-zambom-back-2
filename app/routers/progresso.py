from fastapi import APIRouter, HTTPException, Query
from datetime import date
from typing import List
import pandas as pd

from app.database import get_database
from app.schemas import Progresso, ProgressoCreate, RelatorioBasico, SerieValor, FreqSemanalItem

router = APIRouter(prefix="/progresso", tags=["Progresso & Relatórios"])

@router.post("/", response_model=Progresso)
async def criar_registro_progresso(dado: ProgressoCreate):
    db = get_database()

    # Confere se o usuário existe
    user = await db["usuarios"].find_one({"cpf": dado.cpf_usuario})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    res = await db["progresso"].insert_one(dado.dict())
    return {"id": str(res.inserted_id), **dado.dict()}

@router.get("/{cpf}", response_model=List[Progresso])
async def listar_progresso(
    cpf: str,
    inicio: date | None = Query(None, description="Filtra a partir desta data"),
    fim: date | None = Query(None, description="Filtra até esta data (inclusive)"),
):
    db = get_database()
    filtro: dict = {"cpf_usuario": cpf}
    if inicio or fim:
        filtro["data"] = {}
        if inicio:
            filtro["data"]["$gte"] = inicio
        if fim:
            # incluir o dia 'fim'
            filtro["data"]["$lte"] = fim

    out: list[Progresso] = []
    async for doc in db["progresso"].find(filtro).sort("data", 1):
        out.append({
            "id": str(doc["_id"]),
            "cpf_usuario": doc["cpf_usuario"],
            "data": doc["data"],
            "peso_kg": doc["peso_kg"],
            "gordura_perc": doc.get("gordura_perc"),
            "carga_total": doc.get("carga_total"),
        })
    return out

@router.get("/{cpf}/relatorio", response_model=RelatorioBasico)
async def relatorio_basico(
    cpf: str,
    inicio: date = Query(..., description="Início do período"),
    fim: date = Query(..., description="Fim do período (inclusive)"),
):
    db = get_database()
    cursor = db["progresso"].find(
        {"cpf_usuario": cpf, "data": {"$gte": inicio, "$lte": fim}},
        {"_id": 0, "cpf_usuario": 1, "data": 1, "peso_kg": 1},
    ).sort("data", 1)

    registros = [doc async for doc in cursor]
    if not registros:
        return RelatorioBasico(
            cpf_usuario=cpf,
            periodo_inicio=inicio,
            periodo_fim=fim,
            evolucao_peso=[],
            delta_peso_kg=None,
            freq_semanal=[],
            peso_min=None,
            peso_max=None,
            peso_medio=None,
        )

    df = pd.DataFrame(registros)  # colunas: cpf_usuario, data, peso_kg
    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data")

    # Série de peso
    serie_peso = [
        SerieValor(data=row["data"].date(), valor=float(row["peso_kg"]))
        for _, row in df.iterrows()
    ]

    delta = float(df["peso_kg"].iloc[-1] - df["peso_kg"].iloc[0])

    # Freq. semanal de registros
    weekly = (
        df.set_index("data")
          .resample("W-MON")  # semanas começando na segunda
          .size()
          .reset_index(name="registros")
    )
    weekly["semana"] = weekly["data"].dt.strftime("%G-W%V")
    freq = [
        FreqSemanalItem(semana=row["semana"], registros=int(row["registros"]))
        for _, row in weekly.iterrows()
    ]

    return RelatorioBasico(
        cpf_usuario=cpf,
        periodo_inicio=inicio,
        periodo_fim=fim,
        evolucao_peso=serie_peso,
        delta_peso_kg=delta,
        freq_semanal=freq,
        peso_min=float(df["peso_kg"].min()),
        peso_max=float(df["peso_kg"].max()),
        peso_medio=float(df["peso_kg"].mean()),
    )
