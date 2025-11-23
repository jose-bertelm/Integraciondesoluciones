from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TipoDocumento(Base):
    __tablename__ = "tipos_documentos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    prefijo = Column(String(10), unique=True, nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Rol(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Sede(Base):
    __tablename__ = "sedes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=False)
    direccion = Column(Text)
    telefono = Column(String(20))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo_documento_id = Column(Integer, ForeignKey("tipos_documentos.id"))
    numero_documento = Column(String(50), unique=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(20))
    telefono = Column(String(20))
    email = Column(String(100))
    sede_registro_id = Column(Integer, ForeignKey("sedes.id"))
    rol_id = Column(Integer, ForeignKey("roles.id"))
    password_hash = Column(String(255), nullable=False)
    fhir_patient_id = Column(String(100))
    fhir_practitioner_id = Column(String(100))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    tipo_documento = relationship("TipoDocumento")
    sede_registro = relationship("Sede")
    rol = relationship("Rol")

class TipoEncuentroMedico(Base):
    __tablename__ = "tipos_encuentro_medico"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    codigo_fhir = Column(String(50))
    activo = Column(Boolean, default=True)

class EncuentroMedico(Base):
    __tablename__ = "encuentros_medicos"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=func.now(), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos_encuentro_medico.id"))
    sede_id = Column(Integer, ForeignKey("sedes.id"))
    paciente_id = Column(Integer, ForeignKey("usuarios.id"))
    medico_id = Column(Integer, ForeignKey("usuarios.id"))
    diagnostico = Column(Text)
    diagnostico_codigo_icd10 = Column(String(20))
    diagnostico_codigo_snomed = Column(String(50))
    fhir_encounter_id = Column(String(100))
    estado = Column(String(50), default="finished")
    created_at = Column(DateTime, default=func.now())
    
    tipo = relationship("TipoEncuentroMedico")
    sede = relationship("Sede")
    paciente = relationship("Usuario", foreign_keys=[paciente_id])
    medico = relationship("Usuario", foreign_keys=[medico_id])
    observaciones = relationship("ObservacionClinica", back_populates="encuentro")

class ObservacionClinica(Base):
    __tablename__ = "observaciones_clinicas"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=func.now(), nullable=False)
    encuentro_id = Column(Integer, ForeignKey("encuentros_medicos.id"))
    descripcion = Column(Text, nullable=False)
    valor = Column(String(100))
    unidad = Column(String(50))
    codigo_loinc = Column(String(20))
    interpretacion = Column(String(100))
    sede_id = Column(Integer, ForeignKey("sedes.id"))
    fhir_observation_id = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    
    encuentro = relationship("EncuentroMedico", back_populates="observaciones")
    sede = relationship("Sede")
