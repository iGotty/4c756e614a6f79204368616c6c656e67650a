# app/api/routes/user.py
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from app.models.user import User, StatedPreferences, ProfileData
from app.models.match import MatchResult, MatchResponse
from app.services.data_loader import data_loader

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str = Path(..., description="ID único del usuario")
):
    """
    Obtiene los datos completos de un usuario.
    Incluye preferencias, perfil, historial y embeddings según el tipo.
    """
    try:
        # Buscar usuario en los datos
        user_data = data_loader.users.get(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Usuario {user_id} no encontrado"
            )
        
        # Enriquecer con información adicional
        enriched_data = {
            **user_data,
            "stats": _calculate_user_stats(user_data),
            "profile_completion": _calculate_profile_completion(user_data),
            "last_activity": _get_last_activity(user_data)
        }
        
        return enriched_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo usuario {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/users/login")
async def user_login(body: Dict[str, str]):
    """
    "Login" sin contraseña - solo verifica que el usuario existe.
    Retorna los datos básicos del usuario y un token de sesión mock.
    """
    try:
        user_id = body.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id es requerido"
            )
        
        # Verificar que el usuario existe
        user_data = data_loader.users.get(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"Usuario {user_id} no encontrado"
            )
        
        # Crear respuesta de "login"
        return {
            "success": True,
            "user": {
                "user_id": user_id,
                "registration_type": user_data.get("registration_type"),
                "state": user_data.get("stated_preferences", {}).get("state"),
                "profile_data": user_data.get("profile_data", {}),
                "last_activity": _get_last_activity(user_data)
            },
            "session_token": f"mock_token_{user_id}_{datetime.utcnow().timestamp()}",
            "expires_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/users/{user_id}/match-history")
async def get_user_match_history(
    user_id: str = Path(..., description="ID único del usuario"),
    limit: int = Query(20, ge=1, le=100, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    Obtiene el historial de matches del usuario.
    Incluye todos los matches generados y las interacciones con cada uno.
    """
    try:
        # Verificar que el usuario existe
        user_data = data_loader.users.get(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"Usuario {user_id} no encontrado"
            )
        
        # Obtener historial de interacciones
        interaction_history = user_data.get("interaction_history", {})
        
        # Construir historial de matches
        match_history = []
        
        # Procesar clínicos vistos
        for view in interaction_history.get("clinicians_viewed", []):
            clinician_id = view.get("clinician_id") if isinstance(view, dict) else view
            clinician_data = data_loader.get_clinician(clinician_id)
            
            if clinician_data:
                match_entry = _create_match_history_entry(
                    clinician_data, 
                    view, 
                    "viewed",
                    interaction_history
                )
                match_history.append(match_entry)
        
        # Procesar clínicos contactados (si no están en viewed)
        viewed_ids = {v.get("clinician_id") if isinstance(v, dict) else v 
                     for v in interaction_history.get("clinicians_viewed", [])}
        
        for clinician_id in interaction_history.get("clinicians_contacted", []):
            if clinician_id not in viewed_ids:
                clinician_data = data_loader.get_clinician(clinician_id)
                if clinician_data:
                    match_entry = _create_match_history_entry(
                        clinician_data,
                        {"clinician_id": clinician_id},
                        "contacted",
                        interaction_history
                    )
                    match_history.append(match_entry)
        
        # Ordenar por timestamp (más reciente primero)
        match_history.sort(
            key=lambda x: x.get("last_interaction_at", ""), 
            reverse=True
        )
        
        # Aplicar paginación
        total = len(match_history)
        match_history = match_history[offset:offset + limit]
        
        return {
            "user_id": user_id,
            "total_matches": total,
            "limit": limit,
            "offset": offset,
            "matches": match_history,
            "summary": {
                "total_viewed": len(interaction_history.get("clinicians_viewed", [])),
                "total_contacted": len(interaction_history.get("clinicians_contacted", [])),
                "total_booked": len(interaction_history.get("clinicians_booked", [])),
                "conversion_rate": _calculate_conversion_rate(interaction_history)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo historial de matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/interactions/view")
async def register_view_interaction(body: Dict[str, Any]):
    """
    Registra cuando un usuario ve el perfil de un clínico.
    """
    try:
        user_id = body.get("user_id")
        clinician_id = body.get("clinician_id")
        context = body.get("context", "unknown")
        
        if not user_id or not clinician_id:
            raise HTTPException(
                status_code=400,
                detail="user_id y clinician_id son requeridos"
            )
        
        # Verificar que ambos existen
        user_data = data_loader.users.get(user_id)
        clinician_data = data_loader.get_clinician(clinician_id)
        
        if not user_data:
            raise HTTPException(status_code=404, detail=f"Usuario {user_id} no encontrado")
        
        if not clinician_data:
            raise HTTPException(status_code=404, detail=f"Clínico {clinician_id} no encontrado")
        
        # Registrar la interacción (en producción esto iría a la BD)
        interaction = {
            "interaction_id": f"int_{user_id}_{clinician_id}_{datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "clinician_id": clinician_id,
            "action": "viewed",
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "session_data": {
                "user_type": user_data.get("registration_type"),
                "user_state": user_data.get("stated_preferences", {}).get("state"),
                "clinician_specialties": clinician_data.get("profile_features", {}).get("specialties", [])
            }
        }
        
        # En producción, aquí se guardaría en la base de datos
        # Por ahora, solo simulamos el registro
        logger.info(f"Interacción registrada: {interaction['interaction_id']}")
        
        return {
            "success": True,
            "interaction_id": interaction["interaction_id"],
            "message": "Interacción registrada exitosamente",
            "timestamp": interaction["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando interacción: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/clinicians/{clinician_id}")
async def get_clinician_details(
    clinician_id: str = Path(..., description="ID único del clínico"),
    user_id: Optional[str] = Query(None, description="ID del usuario para personalización")
):
    """
    Obtiene el perfil completo de un clínico.
    Si se proporciona user_id, incluye información personalizada de compatibilidad.
    """
    try:
        # Obtener datos del clínico
        clinician_data = data_loader.get_clinician(clinician_id)
        
        if not clinician_data:
            raise HTTPException(
                status_code=404,
                detail=f"Clínico {clinician_id} no encontrado"
            )
        
        # Formatear respuesta base
        response = {
            "clinician_id": clinician_id,
            "basic_info": clinician_data.get("basic_info", {}),
            "profile_features": clinician_data.get("profile_features", {}),
            "availability_features": clinician_data.get("availability_features", {}),
            "performance_metrics": clinician_data.get("performance_metrics", {}),
            "additional_info": {
                "total_patients": clinician_data.get("availability_features", {}).get("current_patient_count", 0),
                "accepts_new_patients": clinician_data.get("availability_features", {}).get("accepting_new_patients", False),
                "response_time": "Within 24 hours",  # Mock
                "session_format": ["video", "phone"],  # Mock
                "approach_description": _generate_approach_description(clinician_data)
            }
        }
        
        # Si hay user_id, agregar información de compatibilidad
        if user_id:
            user_data = data_loader.users.get(user_id)
            if user_data:
                # Calcular compatibilidad básica
                compatibility = _calculate_basic_compatibility(user_data, clinician_data)
                response["user_compatibility"] = compatibility
                
                # Verificar interacciones previas
                interaction_history = user_data.get("interaction_history", {})
                previous_interaction = _check_previous_interaction(
                    clinician_id, 
                    interaction_history
                )
                if previous_interaction:
                    response["previous_interaction"] = previous_interaction
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalles del clínico: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Funciones auxiliares

def _calculate_user_stats(user_data: Dict) -> Dict:
    """Calcula estadísticas del usuario."""
    history = user_data.get("interaction_history", {})
    
    return {
        "total_clinicians_viewed": len(history.get("clinicians_viewed", [])),
        "total_clinicians_contacted": len(history.get("clinicians_contacted", [])),
        "total_clinicians_booked": len(history.get("clinicians_booked", [])),
        "engagement_level": _calculate_engagement_level(user_data),
        "activity_streak": 0  # Mock por ahora
    }

def _calculate_profile_completion(user_data: Dict) -> float:
    """Calcula el porcentaje de completitud del perfil."""
    if user_data.get("registration_type") == "anonymous":
        return 0.25
    
    completed_fields = 0
    total_fields = 0
    
    # Verificar stated_preferences
    prefs = user_data.get("stated_preferences", {})
    for field in ["state", "language", "appointment_type", "clinical_needs"]:
        total_fields += 1
        if prefs.get(field):
            completed_fields += 1
    
    # Verificar profile_data si existe
    if user_data.get("registration_type") in ["basic", "complete"]:
        profile = user_data.get("profile_data", {})
        for field in ["age_range", "therapy_experience", "therapy_goals"]:
            total_fields += 1
            if profile.get(field):
                completed_fields += 1
    
    return completed_fields / total_fields if total_fields > 0 else 0.0

def _get_last_activity(user_data: Dict) -> Optional[str]:
    """Obtiene la última actividad del usuario."""
    history = user_data.get("interaction_history", {})
    
    # Buscar la interacción más reciente
    latest_timestamp = None
    
    for view in history.get("clinicians_viewed", []):
        if isinstance(view, dict) and "timestamp" in view:
            timestamp = view["timestamp"]
            if not latest_timestamp or timestamp > latest_timestamp:
                latest_timestamp = timestamp
    
    return latest_timestamp

def _calculate_engagement_level(user_data: Dict) -> str:
    """Calcula el nivel de engagement del usuario."""
    if user_data.get("registration_type") == "anonymous":
        return "exploring"
    
    history = user_data.get("interaction_history", {})
    behavioral = user_data.get("behavioral_signals", {})
    
    views = len(history.get("clinicians_viewed", []))
    contacts = len(history.get("clinicians_contacted", []))
    bookings = len(history.get("clinicians_booked", []))
    engagement_score = behavioral.get("engagement_score", 0)
    
    if bookings > 0:
        return "highly_engaged"
    elif contacts > 0 or engagement_score > 0.7:
        return "engaged"
    elif views > 5 or engagement_score > 0.5:
        return "active"
    elif views > 0:
        return "browsing"
    else:
        return "new"

def _create_match_history_entry(
    clinician_data: Dict,
    interaction_data: Dict,
    interaction_type: str,
    full_history: Dict
) -> Dict:
    """Crea una entrada de historial de match."""
    clinician_id = interaction_data.get("clinician_id", "")
    
    # Determinar el estado de la interacción
    status = "viewed"
    if clinician_id in full_history.get("clinicians_booked", []):
        status = "booked"
    elif clinician_id in full_history.get("clinicians_contacted", []):
        status = "contacted"
    
    return {
        "clinician_id": clinician_id,
        "clinician_name": clinician_data.get("basic_info", {}).get("full_name", "Unknown"),
        "specialties": clinician_data.get("profile_features", {}).get("specialties", []),
        "languages": clinician_data.get("profile_features", {}).get("languages", []),
        "interaction_type": interaction_type,
        "status": status,
        "viewed_at": interaction_data.get("timestamp", ""),
        "view_duration": interaction_data.get("duration", 0),
        "last_interaction_at": interaction_data.get("timestamp", ""),
        "clinician_availability": clinician_data.get("availability_features", {}).get("immediate_availability", False)
    }

def _calculate_conversion_rate(interaction_history: Dict) -> float:
    """Calcula la tasa de conversión vista -> booking."""
    views = len(interaction_history.get("clinicians_viewed", []))
    bookings = len(interaction_history.get("clinicians_booked", []))
    
    if views == 0:
        return 0.0
    
    return round(bookings / views * 100, 2)

def _generate_approach_description(clinician_data: Dict) -> str:
    """Genera una descripción del enfoque terapéutico."""
    specialties = clinician_data.get("profile_features", {}).get("specialties", [])
    
    if "trauma" in specialties or "ptsd" in specialties:
        return "Enfoque trauma-informado con técnicas de procesamiento emocional y mindfulness."
    elif "anxiety" in specialties or "depression" in specialties:
        return "Terapia cognitivo-conductual combinada con técnicas de regulación emocional."
    elif "family" in specialties or "relationships" in specialties:
        return "Terapia sistémica enfocada en dinámicas relacionales y comunicación."
    elif "addiction" in specialties:
        return "Enfoque integrativo para recuperación con prevención de recaídas."
    else:
        return "Enfoque personalizado adaptado a las necesidades individuales del paciente."

def _calculate_basic_compatibility(user_data: Dict, clinician_data: Dict) -> Dict:
    """Calcula compatibilidad básica entre usuario y clínico."""
    user_prefs = user_data.get("stated_preferences", {})
    clinician_profile = clinician_data.get("profile_features", {})
    clinician_basic = clinician_data.get("basic_info", {})
    
    compatibility = {
        "overall_score": 0.0,
        "matching_factors": [],
        "potential_barriers": []
    }
    
    score = 0.0
    factors = 0
    
    # Estado
    if user_prefs.get("state") in clinician_basic.get("license_states", []):
        score += 1.0
        factors += 1
        compatibility["matching_factors"].append("Licencia en tu estado")
    else:
        compatibility["potential_barriers"].append("No tiene licencia en tu estado")
    
    # Tipo de cita
    if user_prefs.get("appointment_type") in clinician_basic.get("appointment_types", []):
        score += 1.0
        factors += 1
        compatibility["matching_factors"].append(f"Ofrece {user_prefs.get('appointment_type')}")
    
    # Especialidades
    user_needs = set(user_prefs.get("clinical_needs", []))
    clinician_specs = set(clinician_profile.get("specialties", []))
    if user_needs & clinician_specs:
        score += 0.8
        factors += 1
        matching_specs = list(user_needs & clinician_specs)
        compatibility["matching_factors"].append(f"Especialista en {', '.join(matching_specs)}")
    
    # Idioma
    if user_prefs.get("language") in clinician_profile.get("languages", []):
        score += 0.7
        factors += 1
        compatibility["matching_factors"].append(f"Habla {user_prefs.get('language')}")
    
    # Género
    if (user_prefs.get("gender_preference") and 
        user_prefs.get("gender_preference") == clinician_profile.get("gender")):
        score += 0.5
        factors += 1
        compatibility["matching_factors"].append("Género preferido")
    
    compatibility["overall_score"] = round(score / max(factors, 1), 2)
    
    return compatibility

def _check_previous_interaction(clinician_id: str, interaction_history: Dict) -> Optional[Dict]:
    """Verifica si hubo interacciones previas con el clínico."""
    # Verificar vistas
    for view in interaction_history.get("clinicians_viewed", []):
        view_id = view.get("clinician_id") if isinstance(view, dict) else view
        if view_id == clinician_id:
            return {
                "type": "viewed",
                "timestamp": view.get("timestamp") if isinstance(view, dict) else None,
                "duration": view.get("duration") if isinstance(view, dict) else None
            }
    
    # Verificar contactos
    if clinician_id in interaction_history.get("clinicians_contacted", []):
        return {"type": "contacted"}
    
    # Verificar bookings
    if clinician_id in interaction_history.get("clinicians_booked", []):
        return {"type": "booked"}
    
    return None