from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.routers import auth, usuarios, roles, encuentros, historial, views, sedes, reportes, pdf
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory="/opt/clinica-fhir/app/static"), name="static")

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(roles.router)
app.include_router(encuentros.router)
app.include_router(historial.router)
app.include_router(sedes.router)
app.include_router(reportes.router)
app.include_router(pdf.router)
app.include_router(views.router)

@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc):
    return RedirectResponse(url="/")

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    return RedirectResponse(url="/dashboard")
