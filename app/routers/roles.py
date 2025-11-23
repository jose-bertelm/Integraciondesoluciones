from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Rol, Usuario
from app.schemas.schemas import RolCreate, RolOut
from app.services.auth import require_roles

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", response_model=List[RolOut])
async def listar_roles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    return db.query(Rol).all()

@router.get("/{rol_id}", response_model=RolOut)
async def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol

@router.post("/", response_model=RolOut)
async def crear_rol(
    rol: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    existe = db.query(Rol).filter(Rol.nombre == rol.nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="El rol ya existe")
    
    nuevo_rol = Rol(nombre=rol.nombre, descripcion=rol.descripcion)
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    return nuevo_rol

@router.put("/{rol_id}", response_model=RolOut)
async def actualizar_rol(
    rol_id: int,
    rol_data: RolCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    rol.nombre = rol_data.nombre
    rol.descripcion = rol_data.descripcion
    db.commit()
    db.refresh(rol)
    return rol

@router.delete("/{rol_id}")
async def eliminar_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    rol.activo = False
    db.commit()
    return {"message": "Rol desactivado"}
