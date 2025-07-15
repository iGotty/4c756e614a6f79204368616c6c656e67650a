from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any
from datetime import datetime

class ScoreComponents(BaseModel):
    """Componentes detallados del score de match"""
    # Componentes base
    availability_match: float = Field(0.0, ge=0, le=1)
    insurance_match: float = Field(0.0, ge=0, le=1)
    specialty_match: float = Field(0.0, ge=0, le=1)
    preference_match: float = Field(0.0, ge=0, le=1)
    load_balance_score: float = Field(0.0, ge=0, le=1)
    
    # Componentes adicionales para usuarios básicos/completos
    demographic_match: Optional[float] = Field(None, ge=0, le=1)
    experience_match: Optional[float] = Field(None, ge=0, le=1)
    success_prediction: Optional[float] = Field(None, ge=0, le=1)
    
    # Scores de ML
    collaborative_score: Optional[float] = Field(None, ge=0, le=1)
    content_score: Optional[float] = Field(None, ge=0, le=1)
    
    # Factores de ajuste
    diversity_boost: float = Field(1.0, ge=0, le=2)
    new_clinician_boost: float = Field(1.0, ge=0, le=2)
    overload_penalty: float = Field(1.0, ge=0, le=1)
    cluster_boost: Optional[float] = Field(None, ge=0, le=2)
    history_boost: Optional[float] = Field(None, ge=0, le=2)
    novelty_boost: Optional[float] = Field(None, ge=0, le=2)
    rating_boost: Optional[float] = Field(None, ge=0, le=2)
    critical_preference_boost: Optional[float] = Field(None, ge=0, le=2)
    rejection_risk: Optional[float] = Field(None, ge=0, le=1)
    trending_boost: Optional[float] = Field(None, ge=0, le=2)

class MatchExplanation(BaseModel):
    """Explicación del match para el usuario"""
    primary_reasons: List[str] = Field(..., description="Razones principales del match")
    matching_attributes: List[str] = Field(..., description="Atributos que coinciden")
    score_breakdown: Dict[str, float] = Field(..., description="Desglose del score")
    insights: List[str] = Field(default_factory=list, description="Insights adicionales")
    confidence_level: Literal["low", "medium", "high", "very_high"] = Field(
        "medium", 
        description="Nivel de confianza en la recomendación"
    )

class OverlappingAttributes(BaseModel):
    """Atributos específicos que coinciden entre el usuario y el clínico"""
    state: bool = Field(..., description="Si el clínico tiene licencia en el estado del usuario")
    language: bool = Field(..., description="Si el clínico habla el idioma preferido")
    gender_preference: bool = Field(..., description="Si el género coincide con la preferencia")
    insurance: bool = Field(..., description="Si el clínico acepta el seguro del usuario")
    specialties: List[str] = Field(default_factory=list, description="Lista de clinical_needs que coinciden")
    time_slots: List[str] = Field(default_factory=list, description="Lista de horarios preferidos que coinciden")
    appointment_type: bool = Field(..., description="Si ofrece el tipo de cita solicitado")

class MatchResult(BaseModel):
    """Resultado de un match individual"""
    # Identificación
    clinician_id: str
    clinician_name: str
    
    # Scoring
    match_score: float = Field(..., ge=0, le=1)
    rank_position: int = Field(..., ge=1)
    
    # Información del clínico
    is_available: bool
    accepts_insurance: bool
    specialties: List[str]
    languages: List[str]
    gender: str
    years_experience: int = Field(0, ge=0)
    
    # Atributos que coinciden (NUEVO CAMPO)
    overlapping_attributes: OverlappingAttributes = Field(
        ..., 
        description="Atributos específicos que coinciden con las preferencias del usuario"
    )
    
    # Detalles del match
    score_components: ScoreComponents
    explanation: Optional[MatchExplanation] = None
    matching_strategy: str = Field(..., description="Estrategia utilizada")
    
    # Metadata
    matched_at: datetime = Field(default_factory=datetime.utcnow)
    previous_interaction: Optional[Literal["viewed", "contacted", "booked"]] = None

class MatchResponse(BaseModel):
    """Respuesta completa del endpoint de matching"""
    # Resultados
    user_type: Literal["anonymous", "basic", "complete"]
    total_matches: int
    matches: List[MatchResult]
    
    # Metadata de procesamiento
    processing_time_ms: float
    filters_applied: Dict[str, Any]  # Cambiado de any a Any
    weights_used: Dict[str, float]
    matching_strategy: str
    
    # Información adicional
    message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    
    # Datos específicos por estrategia
    user_cluster_id: Optional[int] = None  # Para usuarios básicos
    predictions_used: Optional[int] = None  # Para usuarios con historial
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_type": "basic",
                "total_matches": 5,
                "matches": [
                    {
                        "clinician_id": "clin_0001_a1b2c3",
                        "clinician_name": "Dr. Sarah Johnson",
                        "match_score": 0.925,
                        "rank_position": 1,
                        "is_available": True,
                        "accepts_insurance": True,
                        "specialties": ["anxiety", "depression", "trauma"],
                        "languages": ["English", "Spanish"],
                        "gender": "female",
                        "years_experience": 8,
                        "overlapping_attributes": {
                            "state": True,
                            "language": True,
                            "gender_preference": True,
                            "insurance": True,
                            "specialties": ["anxiety", "depression"],
                            "time_slots": ["evenings"],
                            "appointment_type": True
                        },
                        "score_components": {
                            "availability_match": 1.0,
                            "insurance_match": 1.0,
                            "specialty_match": 0.8,
                            "preference_match": 0.9,
                            "load_balance_score": 0.7,
                            "demographic_match": 0.85,
                            "cluster_boost": 1.15
                        },
                        "explanation": {
                            "primary_reasons": [
                                "Available immediately",
                                "Accepts Aetna",
                                "Specializes in anxiety, depression"
                            ],
                            "matching_attributes": [
                                "state", "insurance", "anxiety", 
                                "depression", "gender_preference"
                            ],
                            "score_breakdown": {
                                "Availability": 100,
                                "Insurance": 100,
                                "Specialties": 80,
                                "Preferences": 90,
                                "Demographics": 85
                            },
                            "insights": [
                                "Popular among users similar to you"
                            ],
                            "confidence_level": "high"
                        },
                        "matching_strategy": "content_based_clustering",
                        "matched_at": "2024-07-15T10:30:00Z"
                    }
                ],
                "processing_time_ms": 67.3,
                "filters_applied": {
                    "state": "CA",
                    "appointment_type": "therapy",
                    "language": "English",
                    "insurance": "Aetna",
                    "urgency": "immediate"
                },
                "weights_used": {
                    "availability": 0.4,
                    "insurance": 0.2,
                    "specialties": 0.2,
                    "load_balance": 0.1,
                    "preferences": 0.1
                },
                "matching_strategy": "content_based_clustering",
                "user_cluster_id": 0
            }
        }

# Modelos para estadísticas y análisis
class MatchingStats(BaseModel):
    """Estadísticas del sistema de matching"""
    total_matches_served: int
    avg_match_score: float
    avg_processing_time_ms: float
    
    # Por tipo de usuario
    matches_by_user_type: Dict[str, int]
    avg_score_by_user_type: Dict[str, float]
    
    # Por estrategia
    strategy_usage: Dict[str, int]
    strategy_performance: Dict[str, float]
    
    # Filtros
    most_common_filters: List[Dict[str, Any]]  # Cambiado de any a Any
    filter_impact: Dict[str, float]
    
    # Tendencias
    trending_clinicians: List[str]
    popular_specialties: List[str]
    peak_hours: List[int]

class MatchFeedback(BaseModel):
    """Feedback del usuario sobre un match"""
    user_id: str
    clinician_id: str
    match_score: float
    
    # Feedback
    action_taken: Literal["viewed", "contacted", "booked", "ignored", "rejected"]
    satisfaction: Optional[Literal["very_satisfied", "satisfied", "neutral", "dissatisfied", "very_dissatisfied"]] = None
    would_recommend: Optional[bool] = None
    
    # Contexto
    matching_strategy_used: str
    user_type: Literal["anonymous", "basic", "complete"]
    
    # Timestamp
    feedback_at: datetime = Field(default_factory=datetime.utcnow)