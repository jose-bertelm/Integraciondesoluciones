-- Tipos de Documentos
CREATE TABLE tipos_documentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    prefijo VARCHAR(10) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sedes
CREATE TABLE sedes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    direccion TEXT,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    tipo_documento_id INTEGER REFERENCES tipos_documentos(id),
    numero_documento VARCHAR(50) NOT NULL UNIQUE,
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) CHECK (genero IN ('Masculino', 'Femenino')),
    telefono VARCHAR(20),
    email VARCHAR(100),
    sede_registro_id INTEGER REFERENCES sedes(id),
    rol_id INTEGER REFERENCES roles(id),
    password_hash VARCHAR(255) NOT NULL,
    fhir_patient_id VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tipos de Encuentro Médico
CREATE TABLE tipos_encuentro_medico (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo_fhir VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);

-- Encuentros Médicos
CREATE TABLE encuentros_medicos (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_id INTEGER REFERENCES tipos_encuentro_medico(id),
    sede_id INTEGER REFERENCES sedes(id),
    paciente_id INTEGER REFERENCES usuarios(id),
    medico_id INTEGER REFERENCES usuarios(id),
    diagnostico TEXT,
    diagnostico_codigo_icd10 VARCHAR(20),
    diagnostico_codigo_snomed VARCHAR(50),
    fhir_encounter_id VARCHAR(100),
    estado VARCHAR(50) DEFAULT 'finished',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Observaciones Clínicas
CREATE TABLE observaciones_clinicas (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    encuentro_id INTEGER REFERENCES encuentros_medicos(id),
    descripcion TEXT NOT NULL,
    valor VARCHAR(100),
    unidad VARCHAR(50),
    codigo_loinc VARCHAR(20),
    interpretacion VARCHAR(100),
    sede_id INTEGER REFERENCES sedes(id),
    fhir_observation_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_usuarios_documento ON usuarios(numero_documento);
CREATE INDEX idx_usuarios_rol ON usuarios(rol_id);
CREATE INDEX idx_encuentros_paciente ON encuentros_medicos(paciente_id);
CREATE INDEX idx_encuentros_medico ON encuentros_medicos(medico_id);
CREATE INDEX idx_encuentros_fecha ON encuentros_medicos(fecha);
CREATE INDEX idx_observaciones_encuentro ON observaciones_clinicas(encuentro_id);

-- Datos iniciales
INSERT INTO tipos_documentos (nombre, prefijo) VALUES
('Registro Civil de Nacimiento', 'RC'),
('Tarjeta de Identidad', 'TI'),
('Cédula de Ciudadanía', 'CC'),
('Cédula de Extranjería', 'CE'),
('Pasaporte', 'PA'),
('Permiso por Protección Temporal', 'PPT'),
('Salvoconducto de Permanencia', 'SP');

INSERT INTO roles (nombre, descripcion) VALUES
('Administrador', 'Acceso total al sistema'),
('Medico', 'Registro de encuentros y observaciones'),
('Paciente', 'Consulta de historia clínica'),
('Admisionista', 'Gestión de admisiones');

INSERT INTO tipos_encuentro_medico (nombre, codigo_fhir) VALUES
('Consulta General', 'AMB'),
('Urgencias', 'EMER'),
('Hospitalización', 'IMP'),
('Consulta Virtual', 'VR');

INSERT INTO sedes (nombre, ciudad, direccion) VALUES
('Sede Principal', 'Bogotá', 'Calle 100 #15-20'),
('Sede Norte', 'Bogotá', 'Carrera 7 #120-30'),
('Sede Sur', 'Bogotá', 'Avenida 68 #50-10');
