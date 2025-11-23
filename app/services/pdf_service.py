from weasyprint import HTML, CSS
from io import BytesIO
from datetime import datetime

def generar_historia_clinica_pdf(paciente, encuentros):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 12px;
                line-height: 1.5;
                color: #333;
                padding: 20px;
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #2196f3;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #2196f3;
                font-size: 24px;
                margin-bottom: 5px;
            }}
            .header p {{
                color: #666;
                font-size: 11px;
            }}
            .patient-info {{
                background: #f5f5f5;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 25px;
            }}
            .patient-info h2 {{
                color: #2196f3;
                font-size: 16px;
                margin-bottom: 10px;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
            }}
            .patient-info .row {{
                display: flex;
                margin-bottom: 5px;
            }}
            .patient-info .label {{
                font-weight: bold;
                width: 180px;
                color: #555;
            }}
            .patient-info .value {{
                color: #333;
            }}
            .encounter {{
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-bottom: 20px;
                overflow: hidden;
            }}
            .encounter-header {{
                background: #2196f3;
                color: white;
                padding: 12px 15px;
            }}
            .encounter-header h3 {{
                font-size: 14px;
                margin-bottom: 3px;
            }}
            .encounter-header span {{
                font-size: 11px;
                opacity: 0.9;
            }}
            .encounter-body {{
                padding: 15px;
            }}
            .encounter-body .section {{
                margin-bottom: 15px;
            }}
            .encounter-body .section-title {{
                font-weight: bold;
                color: #2196f3;
                margin-bottom: 5px;
                font-size: 12px;
            }}
            .observation {{
                background: #fafafa;
                padding: 10px;
                border-left: 3px solid #4caf50;
                margin-bottom: 8px;
            }}
            .observation .obs-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }}
            .observation .obs-title {{
                font-weight: bold;
                color: #333;
            }}
            .observation .obs-date {{
                color: #888;
                font-size: 10px;
            }}
            .observation .obs-value {{
                color: #4caf50;
                font-weight: bold;
            }}
            .observation .obs-interpretation {{
                font-size: 11px;
                color: #666;
                font-style: italic;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 10px;
                color: #888;
                border-top: 1px solid #ddd;
                padding-top: 15px;
            }}
            .no-records {{
                text-align: center;
                padding: 40px;
                color: #888;
            }}
            .fhir-badge {{
                background: #e3f2fd;
                color: #1976d2;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 10px;
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 Historia Clínica</h1>
            <p>Sistema Clínico Interoperable - FHIR R4</p>
            <p>Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
        </div>
        
        <div class="patient-info">
            <h2>Información del Paciente</h2>
            <div class="row">
                <span class="label">Nombre Completo:</span>
                <span class="value">{paciente.nombres} {paciente.apellidos}</span>
            </div>
            <div class="row">
                <span class="label">Documento:</span>
                <span class="value">{paciente.tipo_documento.prefijo if paciente.tipo_documento else ''} {paciente.numero_documento}</span>
            </div>
            <div class="row">
                <span class="label">Fecha de Nacimiento:</span>
                <span class="value">{paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'N/A'}</span>
            </div>
            <div class="row">
                <span class="label">Género:</span>
                <span class="value">{paciente.genero or 'N/A'}</span>
            </div>
            <div class="row">
                <span class="label">Teléfono:</span>
                <span class="value">{paciente.telefono or 'No registrado'}</span>
            </div>
            <div class="row">
                <span class="label">Email:</span>
                <span class="value">{paciente.email or 'No registrado'}</span>
            </div>
            <div class="row">
                <span class="label">FHIR Patient ID:</span>
                <span class="value">{paciente.fhir_patient_id or 'No sincronizado'}</span>
            </div>
        </div>
        
        <h2 style="color: #2196f3; margin-bottom: 15px; font-size: 18px;">Historial de Encuentros Médicos</h2>
    """
    
    if encuentros:
        for enc in encuentros:
            html_content += f"""
            <div class="encounter">
                <div class="encounter-header">
                    <h3>{enc.tipo.nombre if enc.tipo else 'Consulta'} 
                        {f'<span class="fhir-badge">FHIR: {enc.fhir_encounter_id}</span>' if enc.fhir_encounter_id else ''}
                    </h3>
                    <span>📅 {enc.fecha.strftime('%d/%m/%Y %H:%M')} | 🏢 {enc.sede.nombre if enc.sede else 'N/A'}</span>
                </div>
                <div class="encounter-body">
                    <div class="section">
                        <div class="section-title">👨‍⚕️ Médico Tratante</div>
                        <p>Dr(a). {enc.medico.nombres} {enc.medico.apellidos}</p>
                    </div>
            """
            
            if enc.diagnostico:
                html_content += f"""
                    <div class="section">
                        <div class="section-title">📋 Diagnóstico</div>
                        <p>{enc.diagnostico}</p>
                        {f'<p style="font-size: 11px; color: #666;">Código ICD-10: {enc.diagnostico_codigo_icd10}</p>' if enc.diagnostico_codigo_icd10 else ''}
                        {f'<p style="font-size: 11px; color: #666;">Código SNOMED: {enc.diagnostico_codigo_snomed}</p>' if enc.diagnostico_codigo_snomed else ''}
                    </div>
                """
            
            if enc.observaciones:
                html_content += """
                    <div class="section">
                        <div class="section-title">🔬 Observaciones Clínicas</div>
                """
                for obs in enc.observaciones:
                    html_content += f"""
                        <div class="observation">
                            <div class="obs-header">
                                <span class="obs-title">{obs.descripcion}</span>
                                <span class="obs-date">{obs.fecha.strftime('%d/%m/%Y %H:%M')}</span>
                            </div>
                            {f'<p><span class="obs-value">{obs.valor} {obs.unidad or ""}</span></p>' if obs.valor else ''}
                            {f'<p class="obs-interpretation">Interpretación: {obs.interpretacion}</p>' if obs.interpretacion else ''}
                            {f'<p style="font-size: 10px; color: #888;">LOINC: {obs.codigo_loinc}</p>' if obs.codigo_loinc else ''}
                        </div>
                    """
                html_content += "</div>"
            
            html_content += """
                </div>
            </div>
            """
    else:
        html_content += """
        <div class="no-records">
            <p>No hay registros médicos disponibles</p>
        </div>
        """
    
    html_content += f"""
        <div class="footer">
            <p>Este documento ha sido generado automáticamente por el Sistema Clínico Interoperable</p>
            <p>Datos almacenados en formato HL7 FHIR R4 para garantizar interoperabilidad</p>
            <p>Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer


def generar_carne_paciente_pdf(paciente):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: 8.5cm 5.5cm;
                margin: 0;
            }}
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 10px;
                margin: 0;
                padding: 0;
                background: #fff;
            }}
            .carne {{
                width: 8.5cm;
                height: 5.5cm;
                border: 2px solid #2196f3;
                border-radius: 10px;
                overflow: hidden;
                box-sizing: border-box;
            }}
            .header {{
                background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
                color: white;
                padding: 8px 12px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 14px;
            }}
            .header p {{
                margin: 2px 0 0 0;
                font-size: 8px;
                opacity: 0.9;
            }}
            .body {{
                padding: 10px 12px;
                display: flex;
                gap: 10px;
            }}
            .foto {{
                width: 60px;
                height: 70px;
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #888;
                font-size: 8px;
            }}
            .datos {{
                flex: 1;
            }}
            .datos p {{
                margin: 3px 0;
                font-size: 9px;
            }}
            .datos .label {{
                color: #666;
            }}
            .datos .value {{
                color: #333;
                font-weight: bold;
            }}
            .footer {{
                background: #f5f5f5;
                padding: 5px 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-top: 1px solid #eee;
            }}
            .footer .fhir {{
                font-size: 7px;
                color: #2196f3;
            }}
            .footer .id {{
                font-size: 8px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="carne">
            <div class="header">
                <h1>🏥 Sistema Clínico</h1>
                <p>Carné de Identificación del Paciente</p>
            </div>
            <div class="body">
                <div class="foto">
                    FOTO
                </div>
                <div class="datos">
                    <p><span class="label">Nombre:</span><br><span class="value">{paciente.nombres} {paciente.apellidos}</span></p>
                    <p><span class="label">Documento:</span><br><span class="value">{paciente.tipo_documento.prefijo if paciente.tipo_documento else ''} {paciente.numero_documento}</span></p>
                    <p><span class="label">Fecha Nac.:</span> <span class="value">{paciente.fecha_nacimiento.strftime('%d/%m/%Y') if paciente.fecha_nacimiento else 'N/A'}</span></p>
                    <p><span class="label">Género:</span> <span class="value">{paciente.genero or 'N/A'}</span></p>
                </div>
            </div>
            <div class="footer">
                <span class="fhir">FHIR ID: {paciente.fhir_patient_id or 'No sincronizado'}</span>
                <span class="id">ID: {paciente.id}</span>
            </div>
        </div>
    </body>
    </html>
    """
    
    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer
