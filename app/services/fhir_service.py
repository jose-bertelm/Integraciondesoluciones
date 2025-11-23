import httpx
from typing import Optional
from app.config import settings

class FHIRService:
    def __init__(self):
        self.base_url = settings.FHIR_SERVER_URL
    
    # ==================== PATIENT ====================
    async def create_patient(self, usuario: dict) -> Optional[str]:
        patient = {
            "resourceType": "Patient",
            "identifier": [{
                "system": "http://clinica.local/pacientes",
                "value": usuario["numero_documento"]
            }],
            "name": [{
                "use": "official",
                "family": usuario["apellidos"],
                "given": [usuario["nombres"]]
            }],
            "gender": "male" if usuario["genero"] == "Masculino" else "female",
            "birthDate": str(usuario["fecha_nacimiento"])
        }
        
        if usuario.get("telefono"):
            patient["telecom"] = [{"system": "phone", "value": usuario["telefono"]}]
        if usuario.get("email"):
            patient.setdefault("telecom", []).append({"system": "email", "value": usuario["email"]})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/Patient", json=patient)
            print(f"[FHIR] Create Patient - Status: {response.status_code}")
            if response.status_code == 201:
                return response.json().get("id")
        return None
    
    async def update_patient(self, fhir_id: str, usuario: dict) -> bool:
        patient = {
            "resourceType": "Patient",
            "id": fhir_id,
            "identifier": [{
                "system": "http://clinica.local/pacientes",
                "value": usuario["numero_documento"]
            }],
            "name": [{
                "use": "official",
                "family": usuario["apellidos"],
                "given": [usuario["nombres"]]
            }],
            "gender": "male" if usuario["genero"] == "Masculino" else "female",
            "birthDate": str(usuario["fecha_nacimiento"])
        }
        
        if usuario.get("telefono"):
            patient["telecom"] = [{"system": "phone", "value": usuario["telefono"]}]
        if usuario.get("email"):
            patient.setdefault("telecom", []).append({"system": "email", "value": usuario["email"]})
        
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{self.base_url}/Patient/{fhir_id}", json=patient)
            print(f"[FHIR] Update Patient - Status: {response.status_code}")
            return response.status_code == 200
    
    async def delete_patient(self, fhir_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/Patient/{fhir_id}")
            print(f"[FHIR] Delete Patient {fhir_id} - Status: {response.status_code}")
            return response.status_code in [200, 204]
    
    async def get_patient(self, fhir_id: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/Patient/{fhir_id}")
            if response.status_code == 200:
                return response.json()
        return None
    
    # ==================== PRACTITIONER ====================
    async def create_practitioner(self, usuario: dict) -> Optional[str]:
        practitioner = {
            "resourceType": "Practitioner",
            "identifier": [{
                "system": "http://clinica.local/medicos",
                "value": usuario["numero_documento"]
            }],
            "name": [{
                "use": "official",
                "family": usuario["apellidos"],
                "given": [usuario["nombres"]]
            }],
            "gender": "male" if usuario["genero"] == "Masculino" else "female",
            "birthDate": str(usuario["fecha_nacimiento"])
        }
        
        if usuario.get("telefono"):
            practitioner["telecom"] = [{"system": "phone", "value": usuario["telefono"]}]
        if usuario.get("email"):
            practitioner.setdefault("telecom", []).append({"system": "email", "value": usuario["email"]})
        
        print(f"[FHIR] Creating Practitioner: {practitioner}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/Practitioner", json=practitioner)
            print(f"[FHIR] Create Practitioner - Status: {response.status_code}, Response: {response.text}")
            if response.status_code == 201:
                return response.json().get("id")
        return None
    
    async def update_practitioner(self, fhir_id: str, usuario: dict) -> bool:
        practitioner = {
            "resourceType": "Practitioner",
            "id": fhir_id,
            "identifier": [{
                "system": "http://clinica.local/medicos",
                "value": usuario["numero_documento"]
            }],
            "name": [{
                "use": "official",
                "family": usuario["apellidos"],
                "given": [usuario["nombres"]]
            }],
            "gender": "male" if usuario["genero"] == "Masculino" else "female",
            "birthDate": str(usuario["fecha_nacimiento"])
        }
        
        if usuario.get("telefono"):
            practitioner["telecom"] = [{"system": "phone", "value": usuario["telefono"]}]
        if usuario.get("email"):
            practitioner.setdefault("telecom", []).append({"system": "email", "value": usuario["email"]})
        
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{self.base_url}/Practitioner/{fhir_id}", json=practitioner)
            print(f"[FHIR] Update Practitioner - Status: {response.status_code}")
            return response.status_code == 200
    
    async def delete_practitioner(self, fhir_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/Practitioner/{fhir_id}")
            print(f"[FHIR] Delete Practitioner {fhir_id} - Status: {response.status_code}")
            return response.status_code in [200, 204]
    
    # ==================== ENCOUNTER ====================
    async def create_encounter(self, encuentro: dict, paciente_fhir_id: str, medico_id: int) -> Optional[str]:
        encounter = {
            "resourceType": "Encounter",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": encuentro.get("codigo_fhir", "AMB"),
                "display": encuentro.get("tipo_nombre", "Consulta")
            },
            "subject": {
                "reference": f"Patient/{paciente_fhir_id}"
            },
            "participant": [{
                "individual": {
                    "display": f"Medico ID: {medico_id}"
                }
            }],
            "period": {
                "start": encuentro["fecha"]
            }
        }
        
        if encuentro.get("diagnostico"):
            encounter["reasonCode"] = [{
                "text": encuentro["diagnostico"]
            }]
            if encuentro.get("diagnostico_codigo_icd10"):
                encounter["reasonCode"][0]["coding"] = [{
                    "system": "http://hl7.org/fhir/sid/icd-10",
                    "code": encuentro["diagnostico_codigo_icd10"]
                }]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/Encounter", json=encounter)
            if response.status_code == 201:
                return response.json().get("id")
        return None
    
    # ==================== OBSERVATION ====================
    async def create_observation(self, observacion: dict, paciente_fhir_id: str, encounter_fhir_id: str) -> Optional[str]:
        obs = {
            "resourceType": "Observation",
            "status": "final",
            "subject": {
                "reference": f"Patient/{paciente_fhir_id}"
            },
            "encounter": {
                "reference": f"Encounter/{encounter_fhir_id}"
            },
            "effectiveDateTime": observacion["fecha"],
            "code": {
                "text": observacion["descripcion"]
            }
        }
        
        if observacion.get("codigo_loinc"):
            obs["code"]["coding"] = [{
                "system": "http://loinc.org",
                "code": observacion["codigo_loinc"]
            }]
        
        if observacion.get("valor"):
            if observacion.get("unidad"):
                obs["valueQuantity"] = {
                    "value": float(observacion["valor"]) if observacion["valor"].replace(".", "").isdigit() else 0,
                    "unit": observacion["unidad"]
                }
            else:
                obs["valueString"] = observacion["valor"]
        
        if observacion.get("interpretacion"):
            obs["interpretation"] = [{"text": observacion["interpretacion"]}]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/Observation", json=obs)
            if response.status_code == 201:
                return response.json().get("id")
        return None
    
    # ==================== HISTORY ====================
    async def get_patient_history(self, fhir_patient_id: str) -> dict:
        history = {"encounters": [], "observations": []}
        
        async with httpx.AsyncClient() as client:
            enc_response = await client.get(f"{self.base_url}/Encounter?subject=Patient/{fhir_patient_id}")
            if enc_response.status_code == 200:
                bundle = enc_response.json()
                history["encounters"] = [e["resource"] for e in bundle.get("entry", [])]
            
            obs_response = await client.get(f"{self.base_url}/Observation?subject=Patient/{fhir_patient_id}")
            if obs_response.status_code == 200:
                bundle = obs_response.json()
                history["observations"] = [o["resource"] for o in bundle.get("entry", [])]
        
        return history

fhir_service = FHIRService()
