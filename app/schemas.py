from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date

# --- Usuários ---
class UsuarioBase(BaseModel):
    nome: str
    idade: int
    email: EmailStr
    cpf: str
    endereco: str
    numero: str
    complemento: Optional[str] = None
    cep: str

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: str

# --- Atividades ---
class AtividadeBase(BaseModel):
    nome: str
    descricao: str

class AtividadeCreate(AtividadeBase):
    pass

class Atividade(AtividadeBase):
    id: str

# --- Matrículas ---
class MatriculaBase(BaseModel):
    cpf_usuario: str
    nome_atividade: str

class MatriculaCreate(MatriculaBase):
    pass

class Matricula(MatriculaBase):
    id: str

# --- Progresso (métricas individuais) ---
class ProgressoBase(BaseModel):
    cpf_usuario: str = Field(..., description="CPF do usuário dono das métricas")
    data: date
    peso_kg: float
    gordura_perc: Optional[float] = Field(None, ge=0, le=100)
    carga_total: Optional[float] = Field(None, description="Carga total nos exercícios do dia")

class ProgressoCreate(ProgressoBase):
    pass

class Progresso(ProgressoBase):
    id: str

# --- Relatórios ---
class SerieValor(BaseModel):
    data: date
    valor: float

class FreqSemanalItem(BaseModel):
    semana: str  # ex.: "2025-W36"
    registros: int

class RelatorioBasico(BaseModel):
    cpf_usuario: str
    periodo_inicio: date
    periodo_fim: date
    evolucao_peso: List[SerieValor]
    delta_peso_kg: Optional[float] = None
    freq_semanal: List[FreqSemanalItem]
    peso_min: Optional[float] = None
    peso_max: Optional[float] = None
    peso_medio: Optional[float] = None
