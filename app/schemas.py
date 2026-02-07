from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- ESQUEMAS PARA CREAR ---

class ActivoCreate(BaseModel):
    serial: str
    hostname: Optional[str] = None
    referencia: Optional[str] = None
    mac_activo: Optional[str] = None
    ip_equipo: Optional[str] = None
    
    id_tipoequi: int
    id_marca: int
    id_modelo: Optional[int] = None
    
    estado: str # Bueno, Malo, etc.
    cod_nom_responsable: Optional[str] = None
    id_padre_activo: Optional[int] = None 

# --- ESQUEMAS PARA LEER ---

# Esquema simple para mostrar hijos 
class ActivoHijo(BaseModel):
    id_activo: int
    codigo_qr: Optional[str]
    serial: Optional[str]
    estado: str
    class Config:
        orm_mode = True

# Esquema completo de un activo
class ActivoResponse(BaseModel):
    id_activo: int
    codigo_qr: Optional[str]
    serial: Optional[str]
    hostname: Optional[str]
    modelo_nombre: Optional[str] = None 
    hijos: List[ActivoHijo] = [] 
    class Config:
        orm_mode = True