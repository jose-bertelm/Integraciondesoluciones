from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Sede, Usuario
from app.services.auth import require_roles

router = APIRouter(prefix="/sedes", tags=["sedes"])

class SedeCreate(BaseModel):
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None

class SedeUpdate(BaseModel):
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None

@router.get("/")
async def listar_sedes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    return db.query(Sede).all()

@router.get("/{sede_id}")
async def obtener_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    return sede

@router.post("/")
async def crear_sede(
    sede: SedeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    nueva_sede = Sede(
        nombre=sede.nombre,
        ciudad=sede.ciudad,
        direccion=sede.direccion if sede.direccion else None,
        telefono=sede.telefono if sede.telefono else None
    )
    db.add(nueva_sede)
    db.commit()
    db.refresh(nueva_sede)
    return nueva_sede

@router.put("/{sede_id}")
async def actualizar_sede(
    sede_id: int,
    sede_data: SedeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    update_data = sede_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value == "":
            value = None
        setattr(sede, key, value)
    
    db.commit()
    db.refresh(sede)
    return sede

@router.patch("/{sede_id}/toggle-estado")
async def toggle_estado_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    sede.activo = not sede.activo
    db.commit()
    return {"message": f"Sede {'activada' if sede.activo else 'desactivada'}", "activo": sede.activo}

@router.delete("/{sede_id}")
async def eliminar_sede(
    sede_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    sede = db.query(Sede).filter(Sede.id == sede_id).first()
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    db.delete(sede)
    db.commit()
    return {"message": "Sede eliminada"}
