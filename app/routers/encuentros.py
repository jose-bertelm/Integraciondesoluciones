from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.models import EncuentroMedico, ObservacionClinica, Usuario, TipoEncuentroMedico
from app.schemas.schemas import EncuentroCreate, EncuentroOut, EncuentroConRelaciones
from app.services.auth import require_roles, get_current_user
from app.services.fhir_service import fhir_service

router = APIRouter(prefix="/encuentros", tags=["encuentros"])

@router.get("/", response_model=List[EncuentroConRelaciones])
async def listar_encuentros(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if current_user.rol.nombre == "Medico":
        return db.query(EncuentroMedico).filter(EncuentroMedico.medico_id == current_user.id).order_by(EncuentroMedico.fecha.desc()).all()
    elif current_user.rol.nombre == "Paciente":
        return db.query(EncuentroMedico).filter(EncuentroMedico.paciente_id == current_user.id).order_by(EncuentroMedico.fecha.desc()).all()
    else:
        return db.query(EncuentroMedico).order_by(EncuentroMedico.fecha.desc()).all()

@router.get("/{encuentro_id}", response_model=EncuentroConRelaciones)
async def obtener_encuentro(
    encuentro_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    encuentro = db.query(EncuentroMedico).filter(EncuentroMedico.id == encuentro_id).first()
    if not encuentro:
        raise HTTPException(status_code=404, detail="Encuentro no encontrado")
    
    if current_user.rol.nombre == "Paciente" and encuentro.paciente_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    if current_user.rol.nombre == "Medico" and encuentro.medico_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permisos")
    
    return encuentro

@router.post("/", response_model=EncuentroOut)
async def crear_encuentro(
    encuentro: EncuentroCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Medico"]))
):
    paciente = db.query(Usuario).filter(Usuario.id == encuentro.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    tipo = db.query(TipoEncuentroMedico).filter(TipoEncuentroMedico.id == encuentro.tipo_id).first()
    
    nuevo_encuentro = EncuentroMedico(
        fecha=datetime.now(),
        tipo_id=encuentro.tipo_id,
        sede_id=encuentro.sede_id,
        paciente_id=encuentro.paciente_id,
        medico_id=current_user.id,
        diagnostico=encuentro.diagnostico,
        diagnostico_codigo_icd10=encuentro.diagnostico_codigo_icd10,
        diagnostico_codigo_snomed=encuentro.diagnostico_codigo_snomed
    )
    
    db.add(nuevo_encuentro)
    db.commit()
    db.refresh(nuevo_encuentro)
    
    if paciente.fhir_patient_id:
        fhir_encounter_id = await fhir_service.create_encounter({
            "fecha": nuevo_encuentro.fecha.isoformat(),
            "codigo_fhir": tipo.codigo_fhir if tipo else "AMB",
            "tipo_nombre": tipo.nombre if tipo else "Consulta",
            "diagnostico": encuentro.diagnostico,
            "diagnostico_codigo_icd10": encuentro.diagnostico_codigo_icd10
        }, paciente.fhir_patient_id, current_user.id)
        
        if fhir_encounter_id:
            nuevo_encuentro.fhir_encounter_id = fhir_encounter_id
            db.commit()
        
        for obs in encuentro.observaciones:
            nueva_obs = ObservacionClinica(
                fecha=datetime.now(),
                encuentro_id=nuevo_encuentro.id,
                descripcion=obs.descripcion,
                valor=obs.valor,
                unidad=obs.unidad,
                codigo_loinc=obs.codigo_loinc,
                interpretacion=obs.interpretacion,
                sede_id=encuentro.sede_id
            )
            db.add(nueva_obs)
            db.commit()
            db.refresh(nueva_obs)
            
            if fhir_encounter_id:
                fhir_obs_id = await fhir_service.create_observation({
                    "fecha": nueva_obs.fecha.isoformat(),
                    "descripcion": obs.descripcion,
                    "valor": obs.valor,
                    "unidad": obs.unidad,
                    "codigo_loinc": obs.codigo_loinc,
                    "interpretacion": obs.interpretacion
                }, paciente.fhir_patient_id, fhir_encounter_id)
                
                if fhir_obs_id:
                    nueva_obs.fhir_observation_id = fhir_obs_id
                    db.commit()
    
    return nuevo_encuentro
