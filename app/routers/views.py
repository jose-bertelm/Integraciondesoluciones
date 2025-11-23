from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Usuario, Rol, TipoDocumento, Sede, TipoEncuentroMedico, EncuentroMedico
from app.services.auth import decode_token

router = APIRouter(tags=["views"])
templates = Jinja2Templates(directory="/opt/clinica-fhir/app/templates")

def get_current_user_optional(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    usuario = db.query(Usuario).filter(Usuario.numero_documento == payload.get("sub")).first()
    return usuario

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url="/")
    
    template_map = {
        "Administrador": "admin/dashboard.html",
        "Medico": "medico/dashboard.html",
        "Paciente": "paciente/dashboard.html",
        "Admisionista": "admisionista/dashboard.html"
    }
    
    template = template_map.get(user.rol.nombre, "login.html")
    return templates.TemplateResponse(template, {"request": request, "user": user})

# ==================== ADMIN ====================
@router.get("/admin/usuarios", response_class=HTMLResponse)
async def admin_usuarios(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Administrador":
        return RedirectResponse(url="/")
    
    usuarios = db.query(Usuario).all()
    tipos_doc = db.query(TipoDocumento).all()
    roles = db.query(Rol).filter(Rol.activo == True).all()
    sedes = db.query(Sede).filter(Sede.activo == True).all()
    
    return templates.TemplateResponse("admin/usuarios.html", {
        "request": request,
        "user": user,
        "usuarios": usuarios,
        "tipos_documento": tipos_doc,
        "roles": roles,
        "sedes": sedes
    })

@router.get("/admin/roles", response_class=HTMLResponse)
async def admin_roles(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Administrador":
        return RedirectResponse(url="/")
    
    roles = db.query(Rol).all()
    return templates.TemplateResponse("admin/roles.html", {
        "request": request,
        "user": user,
        "roles": roles
    })

@router.get("/admin/sedes", response_class=HTMLResponse)
async def admin_sedes(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Administrador":
        return RedirectResponse(url="/")
    
    sedes = db.query(Sede).all()
    return templates.TemplateResponse("admin/sedes.html", {
        "request": request,
        "user": user,
        "sedes": sedes
    })

@router.get("/admin/reportes", response_class=HTMLResponse)
async def admin_reportes(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Administrador":
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse("admin/reportes.html", {
        "request": request,
        "user": user
    })

# ==================== MEDICO ====================
@router.get("/medico/consultas", response_class=HTMLResponse)
async def medico_consultas(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Medico":
        return RedirectResponse(url="/")
    
    encuentros = db.query(EncuentroMedico).filter(
        EncuentroMedico.medico_id == user.id
    ).order_by(EncuentroMedico.fecha.desc()).all()
    
    return templates.TemplateResponse("medico/consultas.html", {
        "request": request,
        "user": user,
        "encuentros": encuentros
    })

@router.get("/medico/nuevo-encuentro", response_class=HTMLResponse)
async def medico_nuevo_encuentro(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Medico":
        return RedirectResponse(url="/")
    
    rol_paciente = db.query(Rol).filter(Rol.nombre == "Paciente").first()
    pacientes = db.query(Usuario).filter(Usuario.rol_id == rol_paciente.id, Usuario.activo == True).all()
    tipos = db.query(TipoEncuentroMedico).filter(TipoEncuentroMedico.activo == True).all()
    sedes = db.query(Sede).filter(Sede.activo == True).all()
    
    return templates.TemplateResponse("medico/nuevo_encuentro.html", {
        "request": request,
        "user": user,
        "pacientes": pacientes,
        "tipos_encuentro": tipos,
        "sedes": sedes
    })

# ==================== PACIENTE ====================
@router.get("/paciente/historial", response_class=HTMLResponse)
async def paciente_historial(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Paciente":
        return RedirectResponse(url="/")
    
    encuentros = db.query(EncuentroMedico).filter(
        EncuentroMedico.paciente_id == user.id
    ).order_by(EncuentroMedico.fecha.desc()).all()
    
    return templates.TemplateResponse("paciente/historial.html", {
        "request": request,
        "user": user,
        "encuentros": encuentros
    })

# ==================== ADMISIONISTA ====================
@router.get("/admisionista/pacientes", response_class=HTMLResponse)
async def admisionista_pacientes(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Admisionista":
        return RedirectResponse(url="/")
    
    rol_paciente = db.query(Rol).filter(Rol.nombre == "Paciente").first()
    pacientes = db.query(Usuario).filter(Usuario.rol_id == rol_paciente.id).all()
    tipos_doc = db.query(TipoDocumento).all()
    sedes = db.query(Sede).filter(Sede.activo == True).all()
    
    return templates.TemplateResponse("admisionista/pacientes.html", {
        "request": request,
        "user": user,
        "pacientes": pacientes,
        "tipos_documento": tipos_doc,
        "sedes": sedes
    })

@router.get("/admisionista/nuevo-paciente", response_class=HTMLResponse)
async def admisionista_nuevo_paciente(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Admisionista":
        return RedirectResponse(url="/")
    
    tipos_doc = db.query(TipoDocumento).all()
    sedes = db.query(Sede).filter(Sede.activo == True).all()
    rol_paciente = db.query(Rol).filter(Rol.nombre == "Paciente").first()
    
    return templates.TemplateResponse("admisionista/nuevo_paciente.html", {
        "request": request,
        "user": user,
        "tipos_documento": tipos_doc,
        "sedes": sedes,
        "rol_paciente_id": rol_paciente.id
    })

@router.get("/admisionista/buscar", response_class=HTMLResponse)
async def admisionista_buscar(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Admisionista":
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse("admisionista/buscar.html", {
        "request": request,
        "user": user
    })

@router.get("/admisionista/api/buscar/{documento}")
async def api_buscar_paciente(documento: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user or user.rol.nombre != "Admisionista":
        return {"encontrado": False}
    
    rol_paciente = db.query(Rol).filter(Rol.nombre == "Paciente").first()
    paciente = db.query(Usuario).filter(
        Usuario.numero_documento == documento,
        Usuario.rol_id == rol_paciente.id
    ).first()
    
    if paciente:
        return {
            "encontrado": True,
            "paciente": {
                "id": paciente.id,
                "nombres": paciente.nombres,
                "apellidos": paciente.apellidos,
                "numero_documento": paciente.numero_documento,
                "fecha_nacimiento": str(paciente.fecha_nacimiento) if paciente.fecha_nacimiento else None,
                "telefono": paciente.telefono,
                "email": paciente.email,
                "fhir_patient_id": paciente.fhir_patient_id
            }
        }
    return {"encontrado": False}
