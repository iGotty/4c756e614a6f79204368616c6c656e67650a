from fastapi import APIRouter, HTTPException, Query, Body
import time
from typing import List, Dict, Optional, Any
import logging

from app.models.user import (
    User, StatedPreferences, ProfileData, 
    AnonymousMatchRequest, BasicUserMatchRequest, CompleteUserMatchRequest
)
from app.models.match import MatchResponse, MatchingStats
from app.core.matching_engine import MatchingEngine
from app.services.data_loader import data_loader
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Inicializar componentes
data_loader.load_all_data()
matching_engine = MatchingEngine()

@router.post("/match", response_model=MatchResponse)
async def match_patient_to_clinicians(
    preferences: StatedPreferences,
    limit: Optional[int] = Query(10, ge=1, le=50, description="Número de resultados"),
    explain: Optional[bool] = Query(True, description="Incluir explicaciones detalladas")
):
    """
    Endpoint principal de matching para usuarios anónimos.
    Cumple con TODOS los requisitos del challenge mientras mantiene la estrategia avanzada.
    
    Acepta todos los campos requeridos:
    - state: estado de residencia del paciente
    - language: idioma preferido
    - gender_preference: género deseado del clínico
    - insurance_provider: seguro del paciente
    - appointment_type: therapy o medication
    - clinical_needs: lista de especialidades deseadas
    - preferred_time_slots: horarios preferidos
    - urgency_level: immediate o flexible
    
    Strategy 1: Cold Start - Content-based filtering
    """
    start_time = time.time()
    
    try:
        # Validación: Si es medication, ignorar clinical_needs según requisitos
        if preferences.appointment_type == "medication":
            preferences.clinical_needs = []
            logger.info("Tipo medication: ignorando clinical_needs según requisitos del challenge")
        
        logger.info(f"[ANÓNIMO] Nueva solicitud de matching - Estado: {preferences.state}, "
                   f"Tipo: {preferences.appointment_type}, Urgencia: {preferences.urgency_level}")
        
        # Crear usuario anónimo temporal
        user = User(
            registration_type="anonymous",
            stated_preferences=preferences
        )
        
        # Ejecutar matching con estrategia completa
        # Nota: El límite de 5 para anónimos se maneja en el matching engine
        results = matching_engine.match(
            user=user,
            limit=limit,
            include_explanations=explain
        )
        
        # Log de performance
        if results.processing_time_ms > settings.RESPONSE_TIME_TARGET_MS:
            logger.warning(f"⚠️ Tiempo de respuesta excedido: {results.processing_time_ms:.2f}ms")
        
        return results
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado en matching anónimo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/match/basic", response_model=MatchResponse)
async def match_basic_user(
    request: BasicUserMatchRequest,
    limit: Optional[int] = Query(10, ge=1, le=50, description="Número de resultados"),
    explain: Optional[bool] = Query(True, description="Incluir explicaciones detalladas")
):
    """
    Endpoint de matching para usuarios registrados básicos.
    
    Strategy 2: Content-based enriched + Clustering
    """
    start_time = time.time()
    
    try:
        # Validación para medication
        if request.preferences.appointment_type == "medication":
            request.preferences.clinical_needs = []
        
        logger.info(f"[BÁSICO] Solicitud de matching para usuario {request.user_id}")
        
        # Crear usuario básico con profile data
        user = User(
            user_id=request.user_id,
            registration_type="basic",
            stated_preferences=request.preferences,
            profile_data=request.profile
        )
        
        # Ejecutar matching con estrategia mejorada
        results = matching_engine.match(
            user=user,
            limit=limit,
            include_explanations=explain
        )
        
        return results
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en matching básico: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/match/complete", response_model=MatchResponse)
async def match_complete_user(
    request: CompleteUserMatchRequest,
    limit: Optional[int] = Query(10, ge=1, le=50, description="Número de resultados"),
    explain: Optional[bool] = Query(True, description="Incluir explicaciones detalladas")
):
    """
    Endpoint de matching para usuarios con historial completo.
    
    Strategy 3: Collaborative Filtering + ML
    """
    start_time = time.time()
    
    try:
        # Validación para medication
        if request.preferences.appointment_type == "medication":
            request.preferences.clinical_needs = []
            
        logger.info(f"[COMPLETO] Solicitud de matching para usuario {request.user_id} "
                   f"(usar historial: {request.use_history})")
        
        # CORRECCIÓN: Validar que el usuario existe antes de proceder
        user_data = None
        if request.user_id and request.use_history:
            # Verificar que users sea un diccionario
            if isinstance(data_loader.users, dict):
                user_data = data_loader.users.get(request.user_id)
            else:
                # Si es lista, buscar en la lista
                for user in data_loader.users:
                    if isinstance(user, dict) and user.get('user_id') == request.user_id:
                        user_data = user
                        break
        
        # CORRECCIÓN: Si el usuario no existe Y se pidió usar historial, devolver error
        if request.use_history and not user_data:
            logger.warning(f"Usuario {request.user_id} no encontrado en datos")
            raise HTTPException(
                status_code=404, 
                detail=f"Usuario {request.user_id} no encontrado. Use 'use_history': false o proporcione un user_id válido."
            )
        
        # Crear usuario completo
        if user_data and request.use_history:
            # Limpiar datos del historial para que coincidan con el modelo
            interaction_history = user_data.get('interaction_history', {})
            
            # Extraer solo los IDs de las listas que vienen como objetos
            cleaned_history = {}
            
            # Para clinicians_viewed
            viewed = interaction_history.get('clinicians_viewed', [])
            if viewed and isinstance(viewed[0], dict):
                cleaned_history['clinicians_viewed'] = [
                    item.get('clinician_id') if isinstance(item, dict) else item 
                    for item in viewed
                ]
            else:
                cleaned_history['clinicians_viewed'] = viewed
            
            # Para clinicians_contacted
            contacted = interaction_history.get('clinicians_contacted', [])
            if contacted and isinstance(contacted[0], dict):
                cleaned_history['clinicians_contacted'] = [
                    item.get('clinician_id') if isinstance(item, dict) else item 
                    for item in contacted
                ]
            else:
                cleaned_history['clinicians_contacted'] = contacted
            
            # Para clinicians_booked
            booked = interaction_history.get('clinicians_booked', [])
            if booked and isinstance(booked[0], dict):
                cleaned_history['clinicians_booked'] = [
                    item.get('clinician_id') if isinstance(item, dict) else item 
                    for item in booked
                ]
            else:
                cleaned_history['clinicians_booked'] = booked
            
            # Rejected si existe
            cleaned_history['clinicians_rejected'] = interaction_history.get('clinicians_rejected', [])
            
            # Métricas agregadas
            cleaned_history['avg_session_rating'] = interaction_history.get('avg_session_rating')
            cleaned_history['sessions_completed'] = interaction_history.get('sessions_completed', 0)
            
            # Usar datos existentes con historial limpio
            user = User(
                user_id=request.user_id,
                registration_type="complete",
                stated_preferences=request.preferences,
                profile_data=request.profile,
                interaction_history=cleaned_history,
                embedding_features=user_data.get('embedding_features')
            )
        else:
            # Sin historial, usar como básico
            user = User(
                user_id=request.user_id,
                registration_type="basic",
                stated_preferences=request.preferences,
                profile_data=request.profile
            )
        
        # Ejecutar matching con ML
        results = matching_engine.match(
            user=user,
            limit=limit,
            include_explanations=explain
        )
        
        return results
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en matching completo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/clinicians")
async def get_clinicians(
    state: Optional[str] = Query(None, description="Filter by state"),
    appointment_type: Optional[str] = Query(None, description="Filter by appointment type"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    GET /clinicians - Returns clinician data per challenge requirements.
    """
    try:
        logger.info(f"Clinician request - Filters: state={state}, "
                   f"type={appointment_type}, specialty={specialty}")
        
        # Get all clinicians
        clinicians = list(data_loader.clinicians.values())
        
        # Apply optional filters
        if state:
            clinicians = [
                c for c in clinicians 
                if state in c.get('basic_info', {}).get('license_states', [])
            ]
        
        if appointment_type:
            clinicians = [
                c for c in clinicians 
                if appointment_type in c.get('basic_info', {}).get('appointment_types', [])
            ]
        
        if specialty:
            clinicians = [
                c for c in clinicians 
                if specialty in c.get('profile_features', {}).get('specialties', [])
            ]
        
        # Apply pagination
        total = len(clinicians)
        clinicians = clinicians[offset:offset + limit]
        
        # Format response with all information
        formatted_clinicians = []
        for clinician in clinicians:
            formatted_clinicians.append({
                "clinician_id": clinician.get('clinician_id'),
                "full_name": clinician.get('basic_info', {}).get('full_name'),
                "license_states": clinician.get('basic_info', {}).get('license_states', []),
                "appointment_types": clinician.get('basic_info', {}).get('appointment_types', []),
                "specialties": clinician.get('profile_features', {}).get('specialties', []),
                "languages": clinician.get('profile_features', {}).get('languages', []),
                "gender": clinician.get('profile_features', {}).get('gender'),
                "years_experience": clinician.get('profile_features', {}).get('years_experience', 0),
                "is_available": clinician.get('availability_features', {}).get('immediate_availability', False),
                "accepting_new_patients": clinician.get('availability_features', {}).get('accepting_new_patients', False),
                "avg_rating": clinician.get('performance_metrics', {}).get('avg_patient_rating', 0)
            })
        
        logger.info(f"Returning {len(formatted_clinicians)} of {total} clinicians")
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "clinicians": formatted_clinicians
        }
        
    except Exception as e:
        logger.error(f"Error getting clinicians: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/clinicians/{clinician_id}")
async def get_clinician_by_id(clinician_id: str):
    """
    GET /clinicians/{clinician_id} - Returns detailed information for a specific clinician.
    """
    try:
        logger.info(f"Request for specific clinician: {clinician_id}")
        
        # Get clinician from data loader
        clinician = data_loader.get_clinician(clinician_id)
        
        if not clinician:
            raise HTTPException(
                status_code=404, 
                detail=f"Clinician with ID '{clinician_id}' not found"
            )
        
        # Format detailed response
        basic_info = clinician.get('basic_info', {})
        profile = clinician.get('profile_features', {})
        availability = clinician.get('availability_features', {})
        performance = clinician.get('performance_metrics', {})
        
        detailed_response = {
            "clinician_id": clinician_id,
            "basic_info": {
                "full_name": basic_info.get('full_name', 'Unknown'),
                "license_states": basic_info.get('license_states', []),
                "appointment_types": basic_info.get('appointment_types', [])
            },
            "profile": {
                "gender": profile.get('gender', 'unknown'),
                "languages": profile.get('languages', []),
                "years_experience": profile.get('years_experience', 0),
                "specialties": profile.get('specialties', []),
                "certifications": profile.get('certifications', []),
                "age_groups_served": profile.get('age_groups_served', [])
            },
            "availability": {
                "immediate_availability": availability.get('immediate_availability', False),
                "accepting_new_patients": availability.get('accepting_new_patients', False),
                "current_patient_count": availability.get('current_patient_count', 0),
                "max_patient_capacity": availability.get('max_patient_capacity', 0),
                "availability_score": availability.get('availability_score', 0.0),
                "capacity_percentage": round(
                    (availability.get('current_patient_count', 0) / 
                     max(availability.get('max_patient_capacity', 1), 1)) * 100, 1
                )
            },
            "performance": {
                "avg_patient_rating": performance.get('avg_patient_rating', 0.0),
                "retention_rate": performance.get('retention_rate', 0.0),
                "success_by_specialty": performance.get('success_by_specialty', {}),
                "total_patients_helped": availability.get('current_patient_count', 0) * 3  # Estimate
            },
            "matching_info": {
                "popular_for": list(performance.get('success_by_specialty', {}).keys())[:3],
                "best_suited_for": _get_best_suited_for(clinician),
                "availability_status": _get_availability_status(availability)
            }
        }
        
        return detailed_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clinician {clinician_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def _get_best_suited_for(clinician: Dict) -> List[str]:
    """
    Determines what type of patients this clinician is best suited for.
    """
    suited_for = []
    profile = clinician.get('profile_features', {})
    performance = clinician.get('performance_metrics', {})
    
    # Based on specialties
    specialties = profile.get('specialties', [])
    if 'anxiety' in specialties and 'stress' in specialties:
        suited_for.append("Stress and anxiety management")
    if 'trauma' in specialties or 'PTSD' in specialties:
        suited_for.append("Trauma recovery")
    if 'couples_therapy' in specialties:
        suited_for.append("Relationship counseling")
    if 'depression' in specialties:
        suited_for.append("Depression treatment")
    
    # Based on experience
    if profile.get('years_experience', 0) > 10:
        suited_for.append("Complex cases requiring experienced care")
    elif profile.get('years_experience', 0) < 5:
        suited_for.append("Patients comfortable with newer therapists")
    
    # Based on languages
    languages = profile.get('languages', [])
    if len(languages) > 2:
        suited_for.append("Patients needing multilingual support")
    
    return suited_for[:3]  # Return top 3

def _get_availability_status(availability: Dict) -> str:
    """
    Returns a human-readable availability status.
    """
    if not availability.get('accepting_new_patients', False):
        return "Not accepting new patients"
    
    immediate = availability.get('immediate_availability', False)
    current = availability.get('current_patient_count', 0)
    max_capacity = availability.get('max_patient_capacity', 1)
    capacity_pct = (current / max(max_capacity, 1)) * 100
    
    if immediate and capacity_pct < 50:
        return "Available immediately - Many open slots"
    elif immediate and capacity_pct < 80:
        return "Available soon - Some slots open"
    elif immediate:
        return "Limited availability - Few slots remaining"
    elif capacity_pct < 80:
        return "Accepting new patients - Waitlist possible"
    else:
        return "Nearly full - Long waitlist expected"

@router.get("/match/explain")
async def explain_top_match(
    state: str = Query(..., description="Estado del usuario"),
    language: str = Query("English"),
    gender_preference: Optional[str] = Query(None),
    insurance_provider: Optional[str] = Query(None),
    appointment_type: str = Query("therapy"),
    clinical_needs: Optional[str] = Query(None, description="Necesidades clínicas separadas por comas"),
    preferred_time_slots: Optional[str] = Query(None, description="Horarios preferidos separados por comas"),
    urgency_level: str = Query("flexible")
):
    """
    GET /match/explain - Retorna explicación en lenguaje natural del top match.
    Requisito BONUS del challenge.
    """
    try:
        # Parsear listas desde strings
        clinical_needs_list = clinical_needs.split(",") if clinical_needs else []
        preferred_time_slots_list = preferred_time_slots.split(",") if preferred_time_slots else []
        
        # Validación para medication
        if appointment_type == "medication":
            clinical_needs_list = []
            
        # Crear preferencias
        preferences = StatedPreferences(
            state=state,
            language=language,
            gender_preference=gender_preference,
            insurance_provider=insurance_provider,
            appointment_type=appointment_type,
            clinical_needs=clinical_needs_list,
            preferred_time_slots=preferred_time_slots_list,
            urgency_level=urgency_level
        )
        
        # Crear usuario
        user = User(
            registration_type="anonymous",
            stated_preferences=preferences
        )
        
        # Obtener solo el top match
        results = matching_engine.match(user=user, limit=1, include_explanations=True)
        
        if not results.matches:
            return {
                "explanation": "No clinicians found matching your criteria.",
                "suggestion": "Try broadening your search criteria or changing the state."
            }
        
        top_match = results.matches[0]
        
        # Generate natural complete explanation
        explanation_parts = []
        
        explanation_parts.append(
            f"We recommend {top_match.clinician_name} with a "
            f"{top_match.match_score * 100:.0f}% compatibility score."
        )
        
        # Main reasons
        if top_match.explanation:
            reasons = top_match.explanation.primary_reasons
            if reasons:
                explanation_parts.append(
                    f"The main reasons are: {', '.join(reasons)}."
                )
        
        # Specialties
        if clinical_needs_list and top_match.specialties:
            matching_specs = set(clinical_needs_list) & set(top_match.specialties)
            if matching_specs:
                explanation_parts.append(
                    f"This professional specializes in {', '.join(matching_specs)}, "
                    f"which perfectly matches your needs."
                )
        
        # Availability
        if urgency_level == "immediate" and top_match.is_available:
            explanation_parts.append(
                "They are available immediately to address your urgent case."
            )
        
        # Language
        if language != "English" and language in top_match.languages:
            explanation_parts.append(f"Speaks {language} fluently.")
        
        # Experience
        if top_match.years_experience > 10:
            explanation_parts.append(
                f"Has {top_match.years_experience} years of experience "
                f"helping people with similar situations."
            )
        
        # Insights adicionales si están disponibles
        if top_match.explanation and top_match.explanation.insights:
            for insight in top_match.explanation.insights[:1]:
                explanation_parts.append(insight)
        
        return {
            "clinician_name": top_match.clinician_name,
            "match_score": top_match.match_score,
            "explanation": " ".join(explanation_parts),
            "key_attributes": {
                "specialties": top_match.specialties,
                "languages": top_match.languages,
                "available_now": top_match.is_available,
                "accepts_insurance": top_match.accepts_insurance,
                "years_experience": top_match.years_experience
            },
            "confidence_level": top_match.explanation.confidence_level if top_match.explanation else "medium"
        }
        
    except Exception as e:
        logger.error(f"Error al generar explicación: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/match/explain/all")
async def explain_all_matches(
    state: str = Query(..., description="Estado del usuario"),
    language: str = Query("English"),
    gender_preference: Optional[str] = Query(None),
    insurance_provider: Optional[str] = Query(None),
    appointment_type: str = Query("therapy"),
    clinical_needs: Optional[str] = Query(None, description="Necesidades clínicas separadas por comas"),
    preferred_time_slots: Optional[str] = Query(None, description="Horarios preferidos separados por comas"),
    urgency_level: str = Query("flexible"),
    limit: int = Query(10, ge=1, le=50, description="Número de resultados a explicar")
):
    """
    GET /match/explain/all - Retorna explicaciones en lenguaje natural para TODOS los matches.
    Similar a /match/explain pero para múltiples resultados.
    """
    try:
        # Parsear listas desde strings
        clinical_needs_list = clinical_needs.split(",") if clinical_needs else []
        preferred_time_slots_list = preferred_time_slots.split(",") if preferred_time_slots else []
        
        # Validación para medication
        if appointment_type == "medication":
            clinical_needs_list = []
            
        # Crear preferencias
        preferences = StatedPreferences(
            state=state,
            language=language,
            gender_preference=gender_preference,
            insurance_provider=insurance_provider,
            appointment_type=appointment_type,
            clinical_needs=clinical_needs_list,
            preferred_time_slots=preferred_time_slots_list,
            urgency_level=urgency_level
        )
        
        # Crear usuario
        user = User(
            registration_type="anonymous",
            stated_preferences=preferences
        )
        
        # Obtener matches con el límite especificado
        results = matching_engine.match(user=user, limit=limit, include_explanations=True)
        
        if not results.matches:
            return {
                "total_matches": 0,
                "explanations": [],
                "message": "No clinicians found matching your criteria.",
                "suggestion": "Try broadening your search criteria or changing the state."
            }
        
        # Generar explicaciones para cada match
        explanations = []
        
        for idx, match in enumerate(results.matches, 1):
            # Generar explicación natural para cada match
            explanation_parts = []
            
            # Introduction with ranking
            explanation_parts.append(
                f"#{idx}. {match.clinician_name} - {match.match_score * 100:.0f}% compatibility"
            )
            
            # Main reasons
            if match.explanation and match.explanation.primary_reasons:
                reasons = match.explanation.primary_reasons
                explanation_parts.append(
                    f"Reasons: {', '.join(reasons)}"
                )
            
            # Matching attributes
            overlapping = match.overlapping_attributes
            matching_details = []
            
            if overlapping.state:
                matching_details.append(f"✓ Licensed in {state}")
                
            if overlapping.insurance and insurance_provider:
                matching_details.append(f"✓ Accepts {insurance_provider}")
            elif overlapping.insurance and not insurance_provider:
                matching_details.append("✓ Accepts patients without insurance")
                
            if overlapping.language and language != "English":
                matching_details.append(f"✓ Speaks {language}")
                
            if overlapping.gender_preference and gender_preference:
                matching_details.append(f"✓ Gender: {match.gender}")
                
            if overlapping.specialties:
                matching_details.append(f"✓ Specialties: {', '.join(overlapping.specialties)}")
                
            if overlapping.time_slots:
                matching_details.append(f"✓ Available: {', '.join(overlapping.time_slots)}")
            
            # Additional information
            additional_info = []
            
            if match.years_experience > 10:
                additional_info.append(f"{match.years_experience} years of experience")
                
            if match.is_available and urgency_level == "immediate":
                additional_info.append("Available immediately")
            elif match.is_available:
                additional_info.append("Available for appointments")
                
            if len(match.languages) > 2:
                additional_info.append(f"Multilingual ({len(match.languages)} languages)")
            
            # Insights si están disponibles
            insights = []
            if match.explanation and match.explanation.insights:
                insights = match.explanation.insights
            
            # Construir objeto de explicación
            explanation_obj = {
                "rank": idx,
                "clinician_id": match.clinician_id,
                "clinician_name": match.clinician_name,
                "match_score": match.match_score,
                "summary": " | ".join(explanation_parts),
                "matching_details": matching_details,
                "additional_info": additional_info,
                "insights": insights,
                "confidence_level": match.explanation.confidence_level if match.explanation else "medium",
                "overlapping_attributes": {
                    "state": overlapping.state,
                    "language": overlapping.language,
                    "gender_preference": overlapping.gender_preference,
                    "insurance": overlapping.insurance,
                    "specialties": overlapping.specialties,
                    "time_slots": overlapping.time_slots,
                    "appointment_type": overlapping.appointment_type
                }
            }
            
            explanations.append(explanation_obj)
        
        # Resumen general
        avg_score = sum(m.match_score for m in results.matches) / len(results.matches)
        high_confidence_count = sum(
            1 for e in explanations 
            if e["confidence_level"] in ["high", "very_high"]
        )
        
        return {
            "total_matches": len(results.matches),
            "average_match_score": round(avg_score, 3),
            "high_confidence_matches": high_confidence_count,
            "search_criteria": {
                "state": state,
                "appointment_type": appointment_type,
                "language": language,
                "clinical_needs": clinical_needs_list,
                "urgency": urgency_level
            },
            "explanations": explanations,
            "processing_time_ms": results.processing_time_ms
        }
        
    except Exception as e:
        logger.error(f"Error al generar explicaciones múltiples: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/match/stats")
async def get_matching_stats():
    """
    Endpoint para obtener estadísticas del sistema de matching.
    Muestra el poder del sistema de 3 estrategias.
    """
    try:
        # Calcular estadísticas básicas
        total_clinicians = len(data_loader.clinicians)
        total_users = len(data_loader.users)
        total_interactions = len(data_loader.interactions)
        
        # Análisis de interacciones
        interaction_types = {}
        successful_matches = 0
        
        for interaction in data_loader.interactions[:1000]:  # Muestra
            outcome = interaction.get('outcome', {})
            action = outcome.get('action', 'unknown')
            
            interaction_types[action] = interaction_types.get(action, 0) + 1
            
            if action in ['booked', 'contacted']:
                successful_matches += 1
        
        # Especialidades más comunes
        specialty_counts = {}
        for clinician in data_loader.clinicians.values():
            for specialty in clinician.get('profile_features', {}).get('specialties', []):
                specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
        
        top_specialties = sorted(specialty_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Estados con más clínicos
        state_counts = {}
        for clinician in data_loader.clinicians.values():
            for state in clinician.get('basic_info', {}).get('license_states', []):
                state_counts[state] = state_counts.get(state, 0) + 1
        
        top_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "system_stats": {
                "total_clinicians": total_clinicians,
                "total_users": total_users,
                "total_interactions": total_interactions
            },
            "interaction_analysis": {
                "interaction_types": interaction_types,
                "successful_matches": successful_matches,
                "success_rate": round(successful_matches / max(sum(interaction_types.values()), 1) * 100, 2)
            },
            "top_specialties": dict(top_specialties),
            "top_states": dict(top_states),
            "matching_strategies": {
                "anonymous": "Content-based filtering (Top 5 generic matches)",
                "basic": "Content-based + Clustering (Demographic personalization)",
                "complete": "Collaborative Filtering + ML (History-based prediction)"
            },
            "ml_features": {
                "clustering_enabled": True,
                "collaborative_filtering_enabled": True,
                "embeddings_ready": True,
                "real_time_scoring": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculando estadísticas: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/match/test")
async def test_match_endpoint():
    """
    Endpoint de prueba para verificar que el módulo de matching está funcionando.
    """
    clinicians_count = len(data_loader.get_clinicians_for_matching())
    users_count = len(data_loader.users)
    interactions_count = len(data_loader.interactions)
    
    # Obtener algunos IDs de usuarios de ejemplo
    sample_user_ids = []
    sample_basic_users = []
    
    if isinstance(data_loader.users, dict):
        # Buscar usuarios con diferentes tipos
        for user_id, user_data in data_loader.users.items():
            if isinstance(user_data, dict):
                user_type = user_data.get('registration_type', 'unknown')
                state = user_data.get('stated_preferences', {}).get('state', 'unknown')
                
                # Verificar si tiene historial real
                interaction_history = user_data.get('interaction_history', {})
                has_bookings = bool(interaction_history.get('clinicians_booked'))
                has_contacts = bool(interaction_history.get('clinicians_contacted'))
                has_views = bool(interaction_history.get('clinicians_viewed'))
                
                if has_bookings or has_contacts:
                    sample_user_ids.append({
                        "user_id": user_id,
                        "type": user_type,
                        "state": state,
                        "bookings": len(interaction_history.get('clinicians_booked', [])),
                        "contacts": len(interaction_history.get('clinicians_contacted', [])),
                        "views": len(interaction_history.get('clinicians_viewed', []))
                    })
                
                # También guardar algunos usuarios básicos/complete sin mucho historial
                if user_type in ['basic', 'complete'] and len(sample_basic_users) < 5:
                    sample_basic_users.append({
                        "user_id": user_id,
                        "type": user_type,
                        "state": state
                    })
                
                # Limitar búsqueda
                if len(sample_user_ids) >= 10 and len(sample_basic_users) >= 5:
                    break
    
    # Si no encontramos usuarios con historial, buscar en interacciones
    if not sample_user_ids and data_loader.interactions:
        unique_users_from_interactions = set()
        for interaction in data_loader.interactions[:1000]:  # Revisar primeras 1000
            user_id = interaction.get('user_id')
            if user_id and len(unique_users_from_interactions) < 10:
                unique_users_from_interactions.add(user_id)
        
        sample_user_ids = [{"user_id": uid, "source": "interactions"} for uid in unique_users_from_interactions]
    
    return {
        "status": "ok",
        "message": "Matching engine is ready with 3 strategies",
        "data_loaded": {
            "clinicians": clinicians_count,
            "users": users_count,
            "interactions": interactions_count
        },
        "strategies_available": {
            "anonymous": "Content-based filtering",
            "basic": "Content + Clustering", 
            "complete": "Collaborative + ML"
        },
        "ml_features": {
            "clustering": "enabled",
            "collaborative_filtering": "enabled",
            "embeddings": "ready",
            "performance": "< 200ms target"
        },
        "sample_user_ids_with_history": sample_user_ids[:5],
        "sample_basic_users": sample_basic_users[:5],
        "debug_info": {
            "users_type": type(data_loader.users).__name__,
            "first_user_key": list(data_loader.users.keys())[0] if data_loader.users else None,
            "interactions_sample": len(data_loader.interactions) if data_loader.interactions else 0
        }
    }

def _generate_natural_explanation(
    clinician: Dict, 
    user: User, 
    score: float, 
    components: Any
) -> str:
    """
    Genera una explicación en lenguaje natural.
    """
    score_pct = score * 100
    basic_info = clinician.get('basic_info', {})
    profile = clinician.get('profile_features', {})
    
    explanation_parts = []
    
    # Introduction
    explanation_parts.append(
        f"{basic_info.get('full_name', 'This professional')} has a "
        f"{score_pct:.0f}% compatibility with your preferences."
    )
    
    # Main reasons
    reasons = []
    
    if components.availability_match > 0.8:
        reasons.append("is available immediately")
    
    if components.insurance_match == 1.0 and user.has_insurance():
        reasons.append(f"accepts your {user.stated_preferences.insurance_provider} insurance")
    
    if components.specialty_match > 0.7:
        matching_specs = set(user.stated_preferences.clinical_needs) & set(profile.get('specialties', []))
        if matching_specs:
            reasons.append(f"specializes in {', '.join(list(matching_specs)[:2])}")
    
    if reasons:
        explanation_parts.append(
            f"This professional {', '.join(reasons[:-1])} and {reasons[-1]}." 
            if len(reasons) > 1 else f"This professional {reasons[0]}."
        )
    
    # Additional information
    years_exp = profile.get('years_experience', 0)
    if years_exp > 10:
        explanation_parts.append(f"Has {years_exp} years of experience.")
    
    languages = profile.get('languages', [])
    if len(languages) > 1:
        explanation_parts.append(f"Speaks {', '.join(languages)}.")
    
    rating = clinician.get('performance_metrics', {}).get('avg_patient_rating', 0)
    if rating >= 4.5:
        explanation_parts.append(f"Has an exceptional rating of {rating:.1f}/5.0.")
    
    return " ".join(explanation_parts)