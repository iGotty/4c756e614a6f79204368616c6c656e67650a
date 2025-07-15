# app/core/filters.py
from typing import List, Dict, Optional
from app.models.user import User, StatedPreferences
import logging

logger = logging.getLogger(__name__)

class MatchingFilters:
    """
    Gestiona los filtros para el matching de clínicos.
    Incluye filtros duros (obligatorios) y filtros suaves (preferencias).
    """
    
    def apply_hard_filters(
        self,
        clinicians: List[Dict],
        preferences: StatedPreferences
    ) -> List[Dict]:
        """
        Aplica filtros obligatorios que deben cumplirse siempre.
        """
        filtered = clinicians
        initial_count = len(filtered)
        
        # Log inicial
        logger.debug(f"Aplicando filtros duros a {initial_count} clínicos")
        
        # Filtro 1: Estado (obligatorio)
        filtered = self._filter_by_state(filtered, preferences.state)
        logger.debug(f"Después de filtro estado: {len(filtered)} clínicos")
        
        # Filtro 2: Tipo de cita (obligatorio)
        filtered = self._filter_by_appointment_type(filtered, preferences.appointment_type)
        logger.debug(f"Después de filtro tipo cita: {len(filtered)} clínicos")
        
        # Filtro 3: Aceptando nuevos pacientes (obligatorio)
        filtered = self._filter_accepting_patients(filtered)
        logger.debug(f"Después de filtro nuevos pacientes: {len(filtered)} clínicos")
        
        # CORRECCIÓN: Filtro 4: Idioma - NO debe ser restrictivo según el challenge
        # El idioma es un criterio de matching, no un filtro duro
        # Solo marcar para que el scoring lo considere
        if preferences.language:
            self._mark_language_compatibility(filtered, preferences.language)
            logger.debug(f"Marcado compatibilidad de idioma para: {preferences.language}")
        
        # Log final
        reduction = initial_count - len(filtered)
        reduction_pct = (reduction / initial_count * 100) if initial_count > 0 else 0
        logger.info(f"Filtros duros aplicados: {initial_count} → {len(filtered)} "
                   f"(-{reduction}, -{reduction_pct:.1f}%)")
        
        return filtered
    
    def apply_soft_filters(
        self,
        clinicians: List[Dict],
        user: User,
        max_results: Optional[int] = None
    ) -> List[Dict]:
        """
        Aplica filtros suaves basados en el tipo de usuario.
        No elimina candidatos, solo los marca para scoring diferencial.
        """
        # Para usuarios con historial, marcar clínicos ya visitados
        if user.has_history() and user.interaction_history:
            visited_ids = set(user.interaction_history.clinicians_viewed)
            contacted_ids = set(user.interaction_history.clinicians_contacted)
            booked_ids = set(user.interaction_history.clinicians_booked)
            
            for clinician in clinicians:
                clinician_id = clinician.get('clinician_id')
                
                # Agregar metadata de interacciones previas
                clinician['_previous_interaction'] = None
                
                if clinician_id in booked_ids:
                    clinician['_previous_interaction'] = 'booked'
                elif clinician_id in contacted_ids:
                    clinician['_previous_interaction'] = 'contacted'
                elif clinician_id in visited_ids:
                    clinician['_previous_interaction'] = 'viewed'
        
        # Para usuarios urgentes, marcar clínicos con disponibilidad inmediata
        if user.is_urgent():
            for clinician in clinicians:
                availability = clinician.get('availability_features', {})
                clinician['_urgent_available'] = availability.get('immediate_availability', False)
        
        # Limitar resultados si se especifica
        if max_results and len(clinicians) > max_results:
            # Priorizar por disponibilidad si es urgente
            if user.is_urgent():
                clinicians.sort(
                    key=lambda c: c.get('_urgent_available', False), 
                    reverse=True
                )
            
            clinicians = clinicians[:max_results]
        
        return clinicians
    
    def _filter_by_state(self, clinicians: List[Dict], state: str) -> List[Dict]:
        """
        Filtra clínicos con licencia en el estado del paciente.
        """
        if not state:
            logger.warning("No se especificó estado para filtrar")
            return clinicians
        
        filtered = []
        for clinician in clinicians:
            license_states = clinician.get('basic_info', {}).get('license_states', [])
            if state in license_states:
                filtered.append(clinician)
        
        return filtered
    
    def _filter_by_appointment_type(
        self, 
        clinicians: List[Dict], 
        appointment_type: str
    ) -> List[Dict]:
        """
        Filtra clínicos que ofrecen el tipo de cita requerido.
        """
        if not appointment_type:
            return clinicians
        
        filtered = []
        for clinician in clinicians:
            appointment_types = clinician.get('basic_info', {}).get('appointment_types', [])
            if appointment_type in appointment_types:
                filtered.append(clinician)
        
        return filtered
    
    def _filter_accepting_patients(self, clinicians: List[Dict]) -> List[Dict]:
        """
        Filtra solo clínicos que están aceptando nuevos pacientes.
        """
        filtered = []
        for clinician in clinicians:
            availability = clinician.get('availability_features', {})
            if availability.get('accepting_new_patients', False):
                filtered.append(clinician)
        
        return filtered
    
    def _mark_language_compatibility(
        self, 
        clinicians: List[Dict], 
        language: str
    ) -> None:
        """
        Marca la compatibilidad de idioma sin filtrar.
        El scoring se encargará de penalizar/premiar según corresponda.
        """
        for clinician in clinicians:
            languages = clinician.get('profile_features', {}).get('languages', [])
            
            # Marcar compatibilidad exacta
            clinician['_speaks_requested_language'] = language in languages
            
            # Marcar si al menos habla inglés (para comunicación básica)
            clinician['_speaks_english'] = 'English' in languages
            
            # Guardar el idioma solicitado para referencia
            clinician['_requested_language'] = language
            
            # Calcular un score de compatibilidad de idioma
            if language in languages:
                clinician['_language_compatibility'] = 1.0
            elif 'English' in languages and language != 'English':
                clinician['_language_compatibility'] = 0.5  # Puede comunicarse en inglés
            else:
                clinician['_language_compatibility'] = 0.0  # No hay idioma común
                
        logger.info(f"Marcada compatibilidad de idioma para {language} en {len(clinicians)} clínicos")
    
    def _filter_by_language_strict(
        self, 
        clinicians: List[Dict], 
        language: str
    ) -> List[Dict]:
        """
        Filtra clínicos que hablan el idioma requerido (estricto).
        DEPRECADO: Usar _filter_by_language_improved
        """
        filtered = []
        for clinician in clinicians:
            languages = clinician.get('profile_features', {}).get('languages', [])
            if language in languages:
                filtered.append(clinician)
        
        # Si no hay suficientes resultados, relajar el filtro
        if len(filtered) < 5:
            logger.warning(f"Pocos clínicos hablan {language}, incluyendo bilingües con inglés")
            
            # Incluir clínicos que hablen inglés además del idioma solicitado
            for clinician in clinicians:
                languages = clinician.get('profile_features', {}).get('languages', [])
                if 'English' in languages and clinician not in filtered:
                    filtered.append(clinician)
        
        return filtered
    
    def apply_exclusion_filters(
        self,
        clinicians: List[Dict],
        excluded_ids: List[str]
    ) -> List[Dict]:
        """
        Excluye clínicos específicos (e.g., rechazados previamente).
        """
        if not excluded_ids:
            return clinicians
        
        excluded_set = set(excluded_ids)
        filtered = [
            c for c in clinicians 
            if c.get('clinician_id') not in excluded_set
        ]
        
        logger.debug(f"Excluidos {len(clinicians) - len(filtered)} clínicos")
        
        return filtered
    
    def apply_insurance_filter(
        self,
        clinicians: List[Dict],
        insurance_provider: Optional[str],
        strict: bool = False
    ) -> List[Dict]:
        """
        Filtra por seguro médico (puede ser estricto o suave).
        """
        if not insurance_provider:
            return clinicians
        
        # Por ahora es simulado, en producción vendría de la BD
        if strict:
            filtered = []
            for clinician in clinicians:
                if self._accepts_insurance(clinician, insurance_provider):
                    filtered.append(clinician)
            
            # Si muy pocos aceptan el seguro, incluir algunos sin seguro
            if len(filtered) < 3:
                logger.warning(f"Pocos clínicos aceptan {insurance_provider}")
                # Agregar algunos más sin filtro de seguro
                for clinician in clinicians[:5]:
                    if clinician not in filtered:
                        clinician['_insurance_warning'] = True
                        filtered.append(clinician)
            
            return filtered
        else:
            # Modo suave: solo marcar quién acepta el seguro
            for clinician in clinicians:
                clinician['_accepts_insurance'] = self._accepts_insurance(
                    clinician, 
                    insurance_provider
                )
            
            return clinicians
    
    def _accepts_insurance(self, clinician: Dict, insurance: str) -> bool:
        """
        Verifica si el clínico acepta el seguro (simulado).
        """
        # Simulación determinística
        import hashlib
        clinician_id = clinician.get('clinician_id', '')
        hash_val = int(hashlib.md5(f"{clinician_id}{insurance}".encode()).hexdigest()[:8], 16)
        
        # Probabilidad base del 70%, mayor para seguros comunes
        acceptance_prob = 70
        if insurance in ["Aetna", "Blue Cross", "United Healthcare"]:
            acceptance_prob = 85
        elif insurance in ["Medicaid", "Medicare"]:
            acceptance_prob = 60
        
        return (hash_val % 100) < acceptance_prob
    
    def apply_availability_window_filter(
        self,
        clinicians: List[Dict],
        preferred_slots: List[str],
        strict: bool = False
    ) -> List[Dict]:
        """
        Filtra por ventanas de disponibilidad preferidas.
        """
        if not preferred_slots:
            return clinicians
        
        # Por ahora es simulado
        slot_probabilities = {
            "mornings": 0.8,
            "afternoons": 0.9,
            "evenings": 0.7,
            "weekends": 0.5
        }
        
        for clinician in clinicians:
            clinician_id = clinician.get('clinician_id', '')
            availability_matches = []
            
            for slot in preferred_slots:
                # Simulación determinística
                import hashlib
                hash_val = int(hashlib.md5(f"{clinician_id}{slot}".encode()).hexdigest()[:8], 16)
                prob = slot_probabilities.get(slot, 0.5)
                
                if (hash_val % 100) < (prob * 100):
                    availability_matches.append(slot)
            
            clinician['_matching_time_slots'] = availability_matches
            clinician['_time_slot_match_ratio'] = (
                len(availability_matches) / len(preferred_slots) 
                if preferred_slots else 0
            )
        
        if strict:
            # Filtrar solo los que tienen al menos un slot coincidente
            filtered = [
                c for c in clinicians 
                if c.get('_time_slot_match_ratio', 0) > 0
            ]
            
            # Si muy pocos, relajar
            if len(filtered) < 5:
                return clinicians
            
            return filtered
        
        return clinicians
    
    def get_filter_statistics(
        self, 
        original_count: int, 
        filtered_count: int,
        filter_name: str
    ) -> Dict:
        """
        Calcula estadísticas sobre el impacto de un filtro.
        """
        removed = original_count - filtered_count
        removal_rate = (removed / original_count * 100) if original_count > 0 else 0
        
        return {
            "filter": filter_name,
            "original_count": original_count,
            "filtered_count": filtered_count,
            "removed": removed,
            "removal_rate": round(removal_rate, 1),
            "impact": "high" if removal_rate > 50 else "medium" if removal_rate > 20 else "low"
        }