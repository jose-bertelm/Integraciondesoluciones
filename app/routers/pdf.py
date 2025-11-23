from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Usuario, EncuentroMedico
from app.services.auth import get_current_user, require_roles
from app.services.pdf_service import generar_historia_clinica_pdf, generar_carne_paciente_pdf

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.get("/mi-historia")
async def descargar_mi_historia(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Paciente"]))
):
    encuentros = db.query(EncuentroMedico).filter(
        EncuentroMedico.paciente_id == current_user.id
    ).order_by(EncuentroMedico.fecha.desc()).all()
    
    pdf_buffer = generar_historia_clinica_pdf(current_user, encuentros)
    
    filename = f"historia_clinica_{current_user.numero_documento}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/historia/{paciente_id}")
async def descargar_historia_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Medico", "Administrador", "Admisionista"]))
):
    paciente = db.query(Usuario).filter(Usuario.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    encuentros = db.query(EncuentroMedico).filter(
        EncuentroMedico.paciente_id == paciente_id
    ).order_by(EncuentroMedico.fecha.desc()).all()
    
    pdf_buffer = generar_historia_clinica_pdf(paciente, encuentros)
    
    filename = f"historia_clinica_{paciente.numero_documento}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/carne/{paciente_id}")
async def descargar_carne_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Administrador", "Admisionista"]))
):
    paciente = db.query(Usuario).filter(Usuario.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    pdf_buffer = generar_carne_paciente_pdf(paciente)
    
    filename = f"carne_{paciente.numero_documento}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
