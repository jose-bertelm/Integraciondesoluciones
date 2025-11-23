from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Usuario, Rol, TipoDocumento, Sede
from app.schemas.schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut, UsuarioConRelaciones
from app.services.auth import get_password_hash, get_current_user, require_roles
from app.services.fhir_service import fhir_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

class ToggleEstado(BaseModel):
    activo: bool

def get_user_data(usuario):
    return {
        "numero_documento": usuario.numero_documento,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "genero": usuario.genero,
        "fecha_nacimiento": usuario.fecha_nacimiento,
        "telefono": usuario.telefono,
        "email": usuario.email
    }

@router.get("/", response_model=List[UsuarioConRelaciones])
async def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador", "Admisionista"]))
):
    return db.query(Usuario).all()

@router.get("/{usuario_id}", response_model=UsuarioConRelaciones)
async def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador", "Admisionista"]))
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.post("/", response_model=UsuarioOut)
async def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador", "Admisionista"]))
):
    existe = db.query(Usuario).filter(Usuario.numero_documento == usuario.numero_documento).first()
    if existe:
        raise HTTPException(status_code=400, detail="El documento ya está registrado")
    
    nuevo_usuario = Usuario(
        nombres=usuario.nombres,
        apellidos=usuario.apellidos,
        tipo_documento_id=usuario.tipo_documento_id,
        numero_documento=usuario.numero_documento,
        fecha_nacimiento=usuario.fecha_nacimiento,
        genero=usuario.genero,
        telefono=usuario.telefono,
        email=usuario.email,
        sede_registro_id=usuario.sede_registro_id,
        rol_id=usuario.rol_id,
        password_hash=get_password_hash(usuario.password)
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    rol = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
    user_data = {
        "numero_documento": usuario.numero_documento,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "genero": usuario.genero,
        "fecha_nacimiento": usuario.fecha_nacimiento,
        "telefono": usuario.telefono,
        "email": usuario.email
    }
    
    if rol:
        if rol.nombre == "Paciente":
            fhir_id = await fhir_service.create_patient(user_data)
            if fhir_id:
                nuevo_usuario.fhir_patient_id = fhir_id
                db.commit()
        elif rol.nombre == "Medico":
            fhir_id = await fhir_service.create_practitioner(user_data)
            if fhir_id:
                nuevo_usuario.fhir_practitioner_id = fhir_id
                db.commit()
    
    return nuevo_usuario

@router.put("/{usuario_id}", response_model=UsuarioOut)
async def actualizar_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador", "Admisionista"]))
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    rol_anterior = usuario.rol.nombre if usuario.rol else None
    rol_nuevo_id = usuario_data.rol_id if usuario_data.rol_id else usuario.rol_id
    rol_nuevo = db.query(Rol).filter(Rol.id == rol_nuevo_id).first()
    rol_nuevo_nombre = rol_nuevo.nombre if rol_nuevo else None
    
    for key, value in usuario_data.model_dump(exclude_unset=True).items():
        setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    
    user_data = get_user_data(usuario)
    
    if rol_anterior != rol_nuevo_nombre:
        if rol_anterior == "Paciente" and usuario.fhir_patient_id:
            await fhir_service.delete_patient(usuario.fhir_patient_id)
            usuario.fhir_patient_id = None
        elif rol_anterior == "Medico" and usuario.fhir_practitioner_id:
            await fhir_service.delete_practitioner(usuario.fhir_practitioner_id)
            usuario.fhir_practitioner_id = None
        
        if rol_nuevo_nombre == "Paciente":
            fhir_id = await fhir_service.create_patient(user_data)
            if fhir_id:
                usuario.fhir_patient_id = fhir_id
        elif rol_nuevo_nombre == "Medico":
            fhir_id = await fhir_service.create_practitioner(user_data)
            if fhir_id:
                usuario.fhir_practitioner_id = fhir_id
        
        db.commit()
    else:
        if rol_nuevo_nombre == "Paciente" and usuario.fhir_patient_id:
            await fhir_service.update_patient(usuario.fhir_patient_id, user_data)
        elif rol_nuevo_nombre == "Medico" and usuario.fhir_practitioner_id:
            await fhir_service.update_practitioner(usuario.fhir_practitioner_id, user_data)
    
    return usuario

@router.patch("/{usuario_id}/toggle-estado")
async def toggle_estado_usuario(
    usuario_id: int,
    estado: ToggleEstado,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.activo = estado.activo
    db.commit()
    
    return {"message": f"Usuario {'activado' if estado.activo else 'desactivado'}", "activo": estado.activo}

@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario.fhir_patient_id:
        await fhir_service.delete_patient(usuario.fhir_patient_id)
        print(f"[FHIR] Deleted Patient: {usuario.fhir_patient_id}")
    
    if usuario.fhir_practitioner_id:
        await fhir_service.delete_practitioner(usuario.fhir_practitioner_id)
        print(f"[FHIR] Deleted Practitioner: {usuario.fhir_practitioner_id}")
    
    db.delete(usuario)
    db.commit()
    
    return {"message": "Usuario eliminado completamente"}
