# app/models/user.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime

class StatedPreferences(BaseModel):
    """Preferencias declaradas por el usuario (todos los tipos)"""
    state: str = Field(..., description="Estado de residencia")
    insurance_provider: Optional[str] = Field(None, description="Proveedor de seguro")
    appointment_type: Literal["therapy", "medication"] = Field(..., description="Tipo de cita")
    language: str = Field("English", description="Idioma preferido")
    gender_preference: Optional[str] = Field(None, description="Preferencia de género del clínico")
    clinical_needs: List[str] = Field(default_factory=list, description="Necesidades clínicas")
    preferred_time_slots: List[str] = Field(default_factory=list, description="Horarios preferidos")
    urgency_level: Literal["immediate", "flexible"] = Field("flexible", description="Nivel de urgencia")

class ProfileData(BaseModel):
    """Datos del perfil (solo usuarios registrados)"""
    age_range: Optional[str] = Field(None, description="Rango de edad (e.g., '25-34')")
    therapy_experience: Optional[Literal["first_time", "some_experience", "experienced"]] = None
    therapy_goals: List[str] = Field(default_factory=list, description="Objetivos de terapia")
    occupation_category: Optional[str] = None
    relationship_status: Optional[str] = None

class InteractionHistory(BaseModel):
    """Historial de interacciones (solo usuarios con historial)"""
    clinicians_viewed: List[str] = Field(default_factory=list)
    clinicians_contacted: List[str] = Field(default_factory=list)
    clinicians_booked: List[str] = Field(default_factory=list)
    clinicians_rejected: List[str] = Field(default_factory=list)
    
    # Métricas agregadas
    avg_session_rating: Optional[float] = None
    sessions_completed: int = 0
    last_session_date: Optional[datetime] = None

class UserEmbedding(BaseModel):
    """Embeddings para clustering y ML (usuarios registrados/histórico)"""
    preference_vector: Optional[List[float]] = None
    user_cluster_id: Optional[int] = None
    similarity_scores: Optional[Dict[str, float]] = None

class User(BaseModel):
    """Modelo completo de usuario con soporte para los 3 tipos"""
    # Identificación
    user_id: Optional[str] = Field(None, description="ID único del usuario")
    registration_type: Literal["anonymous", "basic", "complete"] = Field(
        "anonymous", 
        description="Tipo de registro del usuario"
    )
    
    # Datos comunes
    stated_preferences: StatedPreferences
    
    # Datos opcionales según tipo
    profile_data: Optional[ProfileData] = None
    interaction_history: Optional[InteractionHistory] = None
    embedding_features: Optional[UserEmbedding] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    last_match_at: Optional[datetime] = None
    
    # Helpers
    def is_urgent(self) -> bool:
        """Determina si el usuario necesita atención urgente"""
        return self.stated_preferences.urgency_level == "immediate"
    
    def has_insurance(self) -> bool:
        """Verifica si el usuario tiene seguro"""
        return self.stated_preferences.insurance_provider is not None
    
    def is_anonymous(self) -> bool:
        """Verifica si es usuario anónimo"""
        return self.registration_type == "anonymous"
    
    def is_basic(self) -> bool:
        """Verifica si es usuario registrado básico"""
        return self.registration_type == "basic"
    
    def has_history(self) -> bool:
        """Verifica si tiene historial de interacciones"""
        return (self.registration_type == "complete" and 
                self.interaction_history is not None and
                len(self.interaction_history.clinicians_booked) > 0)
    
    def get_positive_clinicians(self) -> List[str]:
        """Obtiene IDs de clínicos con interacciones positivas"""
        if not self.interaction_history:
            return []
        
        positive = set(self.interaction_history.clinicians_booked)
        positive.update(self.interaction_history.clinicians_contacted)
        # Excluir rechazados
        positive -= set(self.interaction_history.clinicians_rejected)
        
        return list(positive)
    
    def get_rejected_clinicians(self) -> List[str]:
        """Obtiene IDs de clínicos rechazados/ignorados"""
        if not self.interaction_history:
            return []
        
        return self.interaction_history.clinicians_rejected

# Request models para los endpoints
class AnonymousMatchRequest(BaseModel):
    """Request para matching anónimo"""
    preferences: StatedPreferences
    
class BasicUserMatchRequest(BaseModel):
    """Request para matching de usuario básico"""
    user_id: str
    preferences: StatedPreferences
    profile: ProfileData
    
class CompleteUserMatchRequest(BaseModel):
    """Request para matching de usuario completo"""
    user_id: str
    preferences: StatedPreferences
    profile: ProfileData
    use_history: bool = Field(True, description="Si usar el historial para personalización")