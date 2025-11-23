from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.models import Usuario, Rol, Sede, EncuentroMedico, ObservacionClinica, TipoEncuentroMedico
from app.services.auth import require_roles

router = APIRouter(prefix="/reportes", tags=["reportes"])

@router.get("/estadisticas")
async def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador"]))
):
    # Contar usuarios por rol
    usuarios_por_rol = db.query(
        Rol.nombre,
        func.count(Usuario.id).label('total')
    ).join(Usuario, Usuario.rol_id == Rol.id).group_by(Rol.nombre).all()
    
    # Total usuarios activos/inactivos
    usuarios_activos = db.query(Usuario).filter(Usuario.activo == True).count()
    usuarios_inactivos = db.query(Usuario).filter(Usuario.activo == False).count()
    
    # Total encuentros
    total_encuentros = db.query(EncuentroMedico).count()
    
    # Encuentros por tipo
    encuentros_por_tipo = db.query(
        TipoEncuentroMedico.nombre,
        func.count(EncuentroMedico.id).label('total')
    ).join(EncuentroMedico, EncuentroMedico.tipo_id == TipoEncuentroMedico.id).group_by(TipoEncuentroMedico.nombre).all()
    
    # Encuentros por sede
    encuentros_por_sede = db.query(
        Sede.nombre,
        func.count(EncuentroMedico.id).label('total')
    ).join(EncuentroMedico, EncuentroMedico.sede_id == Sede.id).group_by(Sede.nombre).all()
    
    # Total observaciones
    total_observaciones = db.query(ObservacionClinica).count()
    
    # Total sedes activas
    sedes_activas = db.query(Sede).filter(Sede.activo == True).count()
    
    # Usuarios con FHIR sincronizado
    pacientes_fhir = db.query(Usuario).filter(Usuario.fhir_patient_id != None).count()
    medicos_fhir = db.query(Usuario).filter(Usuario.fhir_practitioner_id != None).count()
    
    return {
        "usuarios": {
            "total": usuarios_activos + usuarios_inactivos,
            "activos": usuarios_activos,
            "inactivos": usuarios_inactivos,
            "por_rol": [{"rol": r[0], "total": r[1]} for r in usuarios_por_rol]
        },
        "encuentros": {
            "total": total_encuentros,
            "por_tipo": [{"tipo": t[0], "total": t[1]} for t in encuentros_por_tipo],
            "por_sede": [{"sede": s[0], "total": s[1]} for s in encuentros_por_sede]
        },
        "observaciones": {
            "total": total_observaciones
        },
        "sedes": {
            "activas": sedes_activas
        },
        "fhir": {
            "pacientes_sincronizados": pacientes_fhir,
            "medicos_sincronizados": medicos_fhir
        }
    }
