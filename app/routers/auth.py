from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import LoginForm
from app.services.auth import verify_password, create_access_token, get_current_user

router = APIRouter(tags=["auth"])

@router.post("/login")
async def login(response: Response, form_data: LoginForm, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.numero_documento == form_data.numero_documento).first()
    
    if not usuario or not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    if not usuario.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inactivo")
    
    access_token = create_access_token(data={"sub": usuario.numero_documento})
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/me")
async def get_me(current_user: Usuario = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "nombres": current_user.nombres,
        "apellidos": current_user.apellidos,
        "rol": current_user.rol.nombre
    }
