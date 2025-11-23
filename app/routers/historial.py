from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Usuario, EncuentroMedico
from app.services.auth import get_current_user, require_roles
from app.services.fhir_service import fhir_service

router = APIRouter(prefix="/historial", tags=["historial"])

@router.get("/")
async def obtener_mi_historial(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Paciente"]))
):
    encuentros = db.query(EncuentroMedico).filter(
        EncuentroMedico.paciente_id == current_user.id
    ).order_by(EncuentroMedico.fecha.desc()).all()
    
    historial = []
    for enc in encuentros:
        historial.append({
            "id": enc.id,
            "fecha": enc.fecha.isoformat(),
            "tipo": enc.tipo.nombre if enc.tipo else None,
            "sede": enc.sede.nombre if enc.sede else None,
            "medico": f"{enc.medico.nombres} {enc.medico.apellidos}" if enc.medico else None,
            "diagnostico": enc.diagnostico,
            "codigo_icd10": enc.diagnostico_codigo_icd10,
            "observaciones": [{
                "descripcion": obs.descripcion,
                "valor": obs.valor,
                "unidad": obs.unidad,
                "interpretacion": obs.interpretacion,
                "fecha": obs.fecha.isoformat()
            } for obs in enc.observaciones]
        })
    
    return {"historial": historial}

@router.get("/fhir")
async def obtener_historial_fhir(
    current_user: Usuario = Depends(require_roles(["Paciente"]))
):
    if not current_user.fhir_patient_id:
        raise HTTPException(status_code=404, detail="No tiene registro FHIR")
    
    history = await fhir_service.get_patient_history(current_user.fhir_patient_id)
    return history

@router.get("/paciente/{paciente_id}")
async def obtener_historial_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Medico", "Administrador"]))
):
    paciente = db.query(Usuario).filter(Usuario.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    encuentros = db.query(EncuentroMedico).filter(
        EncuentroMedico.paciente_id == paciente_id
    ).order_by(EncuentroMedico.fecha.desc()).all()
    
    historial = []
    for enc in encuentros:
        historial.append({
            "id": enc.id,
            "fecha": enc.fecha.isoformat(),
            "tipo": enc.tipo.nombre if enc.tipo else None,
            "sede": enc.sede.nombre if enc.sede else None,
            "medico": f"{enc.medico.nombres} {enc.medico.apellidos}" if enc.medico else None,
            "diagnostico": enc.diagnostico,
            "codigo_icd10": enc.diagnostico_codigo_icd10,
            "observaciones": [{
                "descripcion": obs.descripcion,
                "valor": obs.valor,
                "unidad": obs.unidad,
                "interpretacion": obs.interpretacion,
                "fecha": obs.fecha.isoformat()
            } for obs in enc.observaciones]
        })
    
    return {
        "paciente": f"{paciente.nombres} {paciente.apellidos}",
        "documento": paciente.numero_documento,
        "historial": historial
    }
