from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    numero_documento: Optional[str] = None

# TipoDocumento
class TipoDocumentoBase(BaseModel):
    nombre: str
    prefijo: str

class TipoDocumentoOut(TipoDocumentoBase):
    id: int
    class Config:
        from_attributes = True

# Rol
class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    pass

class RolOut(RolBase):
    id: int
    activo: bool
    class Config:
        from_attributes = True

# Sede
class SedeBase(BaseModel):
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None

class SedeOut(SedeBase):
    id: int
    activo: bool
    class Config:
        from_attributes = True

# Usuario
class UsuarioBase(BaseModel):
    nombres: str
    apellidos: str
    tipo_documento_id: int
    numero_documento: str
    fecha_nacimiento: date
    genero: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    sede_registro_id: int
    rol_id: int

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    sede_registro_id: Optional[int] = None
    rol_id: Optional[int] = None
    activo: Optional[bool] = None

class UsuarioOut(UsuarioBase):
    id: int
    activo: bool
    fhir_patient_id: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class UsuarioConRelaciones(UsuarioOut):
    tipo_documento: Optional[TipoDocumentoOut] = None
    sede_registro: Optional[SedeOut] = None
    rol: Optional[RolOut] = None

# TipoEncuentro
class TipoEncuentroOut(BaseModel):
    id: int
    nombre: str
    codigo_fhir: Optional[str] = None
    class Config:
        from_attributes = True

# Observacion
class ObservacionBase(BaseModel):
    descripcion: str
    valor: Optional[str] = None
    unidad: Optional[str] = None
    codigo_loinc: Optional[str] = None
    interpretacion: Optional[str] = None

class ObservacionCreate(ObservacionBase):
    pass

class ObservacionOut(ObservacionBase):
    id: int
    fecha: datetime
    fhir_observation_id: Optional[str] = None
    class Config:
        from_attributes = True

# Encuentro
class EncuentroBase(BaseModel):
    tipo_id: int
    sede_id: int
    paciente_id: int
    diagnostico: Optional[str] = None
    diagnostico_codigo_icd10: Optional[str] = None
    diagnostico_codigo_snomed: Optional[str] = None

class EncuentroCreate(EncuentroBase):
    observaciones: Optional[List[ObservacionCreate]] = []

class EncuentroOut(EncuentroBase):
    id: int
    fecha: datetime
    medico_id: int
    estado: str
    fhir_encounter_id: Optional[str] = None
    class Config:
        from_attributes = True

class EncuentroConRelaciones(EncuentroOut):
    tipo: Optional[TipoEncuentroOut] = None
    sede: Optional[SedeOut] = None
    paciente: Optional[UsuarioOut] = None
    medico: Optional[UsuarioOut] = None
    observaciones: List[ObservacionOut] = []

# Login
class LoginForm(BaseModel):
    numero_documento: str
    password: str
