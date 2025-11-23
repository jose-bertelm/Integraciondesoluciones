# Sistema Clínico Interoperable con HAPI FHIR

Sistema de Historia Clínica Electrónica (HCE) interoperable que integra **PostgreSQL**, **FastAPI**, **HAPI FHIR** y cumple con los estándares **HL7 FHIR R4** para garantizar la interoperabilidad de datos clínicos.

![Sistema Clínico](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![FHIR](https://img.shields.io/badge/FHIR-R4-orange)

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Interoperabilidad FHIR](#interoperabilidad-fhir)
- [Roles y Permisos](#roles-y-permisos)
- [API Endpoints](#api-endpoints)
- [Metadatos Multisede](#metadatos-multisede)
- [Seguridad](#seguridad)
- [Mantenimiento](#mantenimiento)
- [Tecnologías](#tecnologías)

---

## ✨ Características

### Funcionalidades Principales

- 🏥 **Historia Clínica Electrónica Única (HCEU)** - Centralizada y accesible desde múltiples sedes
- 🔗 **Interoperabilidad FHIR R4** - Sincronización con servidor HAPI FHIR
- 🔐 **Autenticación OAuth2 + JWT** - Sistema seguro de autenticación
- 👥 **Gestión por Roles** - 4 interfaces diferenciadas (Admin, Médico, Paciente, Admisionista)
- 📄 **Exportación PDF Protegida** - Historias clínicas con contraseña (número de documento)
- 🌍 **Trazabilidad Multisede** - Metadatos de ciudad/origen en cada registro
- 📊 **Reportes y Estadísticas** - Dashboard administrativo con métricas del sistema
- 🏷️ **Códigos Médicos Estandarizados** - Soporte para ICD-10, LOINC, SNOMED CT

### Recursos FHIR Implementados

- ✅ **Patient** - Información demográfica de pacientes
- ✅ **Practitioner** - Datos de médicos/profesionales
- ✅ **Encounter** - Encuentros médicos/consultas
- ✅ **Observation** - Observaciones clínicas y signos vitales

---

## 🏗️ Arquitectura
```
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                        │
│                    Puerto 80 (HTTP)                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┴──────────────┐
        │                              │
        ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  FastAPI App     │          │   HAPI FHIR      │
│  Puerto 8000     │◄────────►│   Puerto 8080    │
│  (Middleware)    │          │   (Docker)       │
└────────┬─────────┘          └──────────────────┘
         │
         ▼
┌──────────────────┐
│   PostgreSQL     │
│   Puerto 5432    │
│   (Docker)       │
└──────────────────┘
```

### Flujo de Datos

1. **Usuario** → Accede vía navegador
2. **NGINX** → Enruta la solicitud al backend correspondiente
3. **FastAPI** → Procesa la lógica de negocio
4. **PostgreSQL** → Almacena datos relacionales
5. **HAPI FHIR** → Sincroniza recursos clínicos en formato FHIR
6. **Respuesta** → Vista HTML renderizada con Jinja2

---

## 📦 Requisitos

### Hardware Recomendado

- **CPU:** 4 núcleos
- **RAM:** 16 GB (mínimo 8 GB)
- **Disco:** 50 GB de espacio libre

### Software

- **Sistema Operativo:** Ubuntu 24.04 LTS
- **Docker:** v29.0+
- **Docker Compose:** v2.40+
- **Python:** 3.12+
- **Git:** 2.43+

---

## 🚀 Instalación

### 1. Actualizar el Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential
```

### 2. Instalar Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Clonar el Repositorio
```bash
cd /opt
git clone https://github.com/jose-bertelm/Integraciondesoluciones.git
cd Integraciondesoluciones
```

### 4. Instalar Dependencias de Python
```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    libpq-dev libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libffi-dev shared-mime-info

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Nota:** Si no existe `requirements.txt`, instalar manualmente:
```bash
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary \
    python-jose[cryptography] passlib[bcrypt] python-multipart \
    jinja2 weasyprint httpx pydantic pydantic-settings \
    python-dotenv fhir.resources pikepdf
```

### 5. Configurar Variables de Entorno
```bash
cp .env.example .env
nano .env
```

Editar con tus valores:
```env
DATABASE_URL=postgresql://clinica_user:TU_PASSWORD@localhost:5432/clinica_db
FHIR_SERVER_URL=http://localhost:8080/fhir
SECRET_KEY=TU_CLAVE_SECRETA_MUY_SEGURA
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Levantar los Contenedores
```bash
docker compose up -d
```

Esperar 30 segundos y verificar:
```bash
docker compose ps
```

### 7. Crear Usuario Administrador
```bash
python3 << 'EOF'
from app.database import SessionLocal
from app.models.models import Usuario, Rol
from app.services.auth import get_password_hash

db = SessionLocal()
rol_admin = db.query(Rol).filter(Rol.nombre == "Administrador").first()
nuevo_admin = Usuario(
    nombres="Administrador",
    apellidos="Sistema",
    tipo_documento_id=3,
    numero_documento="admin123",
    fecha_nacimiento="1990-01-01",
    genero="Masculino",
    sede_registro_id=1,
    rol_id=rol_admin.id,
    password_hash=get_password_hash("admin123")
)
db.add(nuevo_admin)
db.commit()
print("✅ Usuario admin123 / admin123 creado")
db.close()
