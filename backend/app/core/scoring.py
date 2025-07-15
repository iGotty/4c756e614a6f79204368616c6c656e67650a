# app/core/scoring.py
from typing import Dict, Tuple
from datetime import datetime, timedelta
import numpy as np

from app.models.user import User
from app.models.match import ScoreComponents
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Motor de scoring multi-criterio con diferentes estrategias por tipo de usuario.
    """
    
    def calculate_anonymous_score(
        self,
        clinician: Dict,
        user: User,
        weights: Dict[str, float]
    ) -> Tuple[float, ScoreComponents]:
        """
        Scoring para usuarios anónimos (Strategy 1).
        Solo content-based con información básica.
        """
        components = ScoreComponents(
            availability_match=self._score_availability(clinician, user),
            insurance_match=self._score_insurance(clinician, user),
            specialty_match=self._score_specialties_basic(clinician, user),
            preference_match=self._score_preferences_basic(clinician, user),
            load_balance_score=self._score_load_balance(clinician)
        )
        
        # Score base ponderado
        base_score = self._calculate_weighted_score(components, weights)
        
        # Aplicar ajustes básicos
        final_score = self._apply_basic_adjustments(
            base_score, 
            clinician, 
            components
        )
        
        return final_score, components
    
    def calculate_basic_score(
        self,
        clinician: Dict,
        user: User,
        weights: Dict[str, float]
    ) -> Tuple[float, ScoreComponents]:
        """
        Scoring para usuarios básicos (Strategy 2).
        Content-based enriquecido con datos demográficos.
        """
        # Componentes base
        components = ScoreComponents(
            availability_match=self._score_availability(clinician, user),
            insurance_match=self._score_insurance(clinician, user),
            specialty_match=self._score_specialties_enhanced(clinician, user),
            preference_match=self._score_preferences_enhanced(clinician, user),
            load_balance_score=self._score_load_balance(clinician),
            demographic_match=self._score_demographics(clinician, user)
        )
        
        # Agregar peso demográfico
        weights_enhanced = weights.copy()
        weights_enhanced['demographics'] = 0.15
        
        # Normalizar otros pesos
        total_weight = sum(weights_enhanced.values())
        weights_enhanced = {k: v/total_weight for k, v in weights_enhanced.items()}
        
        # Score ponderado
        base_score = self._calculate_weighted_score_enhanced(
            components, 
            weights_enhanced
        )
        
        # Aplicar ajustes mejorados
        final_score = self._apply_enhanced_adjustments(
            base_score, 
            clinician, 
            components,
            user
        )
        
        return final_score, components
    
    def calculate_complete_score(
        self,
        clinician: Dict,
        user: User,
        weights: Dict[str, float]
    ) -> Tuple[float, ScoreComponents]:
        """
        Scoring para usuarios con historial (Strategy 3).
        Incluye señales del comportamiento pasado.
        """
        # Todos los componentes
        components = ScoreComponents(
            availability_match=self._score_availability(clinician, user),
            insurance_match=self._score_insurance(clinician, user),
            specialty_match=self._score_specialties_ml(clinician, user),
            preference_match=self._score_preferences_ml(clinician, user),
            load_balance_score=self._score_load_balance(clinician),
            demographic_match=self._score_demographics(clinician, user),
            experience_match=self._score_experience_match(clinician, user),
            success_prediction=self._predict_success_rate(clinician, user)
        )
        
        # Pesos adaptados para ML
        weights_ml = self._adapt_weights_from_history(weights, user)
        
        # Score complejo
        base_score = self._calculate_ml_score(components, weights_ml)
        
        # Ajustes avanzados
        final_score = self._apply_ml_adjustments(
            base_score, 
            clinician, 
            components,
            user
        )
        
        return final_score, components
    
    def _score_availability(self, clinician: Dict, user: User) -> float:
        """
        Score de disponibilidad común para todos los usuarios.
        """
        availability = clinician.get('availability_features', {})
        
        if user.is_urgent():
            # Urgente: disponibilidad inmediata es crítica
            if availability.get('immediate_availability', False):
                return 1.0
            else:
                return 0.2
        else:
            # Flexible: usar score general de disponibilidad
            base_score = availability.get('availability_score', 0.5)
            
            # Bonus si tiene buena disponibilidad general
            if availability.get('accepting_new_patients', False):
                base_score = min(base_score + 0.2, 1.0)
            
            return base_score
    
    def _score_insurance(self, clinician: Dict, user: User) -> float:
        """
        Score de compatibilidad de seguro.
        """
        if not user.has_insurance():
            return 0.5  # Neutral si no tiene seguro
        
        # Simulación determinística de aceptación
        clinician_id = clinician.get('clinician_id', '')
        insurance = user.stated_preferences.insurance_provider
        
        import hashlib
        hash_val = int(hashlib.md5(f"{clinician_id}{insurance}".encode()).hexdigest()[:8], 16)
        
        # 70% de probabilidad base, ajustada por tipo de seguro
        acceptance_prob = 70
        if insurance in ["Aetna", "Blue Cross"]:
            acceptance_prob = 85
        elif insurance in ["Medicaid", "Medicare"]:
            acceptance_prob = 60
        
        return 1.0 if (hash_val % 100) < acceptance_prob else 0.0
    
    def _score_specialties_basic(self, clinician: Dict, user: User) -> float:
        """
        Score básico de especialidades para usuarios anónimos.
        """
        needs = user.stated_preferences.clinical_needs
        if not needs:
            return 0.5
        
        specialties = clinician.get('profile_features', {}).get('specialties', [])
        if not specialties:
            return 0.0
        
        # Match directo
        matching = set(needs) & set(specialties)
        match_ratio = len(matching) / len(needs)
        
        return match_ratio
    
    def _score_specialties_enhanced(self, clinician: Dict, user: User) -> float:
        """
        Score mejorado de especialidades para usuarios básicos.
        Considera éxito del clínico en esas especialidades.
        """
        base_score = self._score_specialties_basic(clinician, user)
        
        if base_score == 0:
            return 0.0
        
        # Mejorar con métricas de performance
        needs = user.stated_preferences.clinical_needs
        performance = clinician.get('performance_metrics', {})
        success_by_specialty = performance.get('success_by_specialty', {})
        
        if success_by_specialty and needs:
            success_scores = []
            for need in needs:
                if need in success_by_specialty:
                    success_scores.append(success_by_specialty[need])
            
            if success_scores:
                avg_success = sum(success_scores) / len(success_scores)
                # Combinar match ratio con éxito
                enhanced_score = (base_score * 0.6) + (avg_success * 0.4)
                return enhanced_score
        
        return base_score
    
    def _score_specialties_ml(self, clinician: Dict, user: User) -> float:
        """
        Score ML de especialidades para usuarios con historial.
        Usa embeddings y similitud semántica.
        """
        enhanced_score = self._score_specialties_enhanced(clinician, user)
        
        # Si hay embeddings, usar similitud semántica
        clinician_embedding = clinician.get('embedding_features', {}).get('specialty_vector')
        user_embedding = user.embedding_features.preference_vector if user.embedding_features else None
        
        if clinician_embedding and user_embedding:
            # Cosine similarity
            cosine_sim = np.dot(clinician_embedding, user_embedding) / (
                np.linalg.norm(clinician_embedding) * np.linalg.norm(user_embedding)
            )
            
            # Combinar con score tradicional
            ml_score = (enhanced_score * 0.5) + (max(0, cosine_sim) * 0.5)
            return ml_score
        
        return enhanced_score
    
    def _score_preferences_basic(self, clinician: Dict, user: User) -> float:
        """
        Score básico de preferencias (género, idioma).
        """
        profile = clinician.get('profile_features', {})
        prefs = user.stated_preferences
        
        scores = []
        
        # Género
        if prefs.gender_preference:
            gender_match = 1.0 if profile.get('gender') == prefs.gender_preference else 0.0
            scores.append(gender_match)
        
        # Idioma
        if prefs.language in profile.get('languages', []):
            scores.append(1.0)
        elif prefs.language == "English":  # Inglés por defecto
            scores.append(0.8)
        else:
            scores.append(0.0)
        
        # Horarios (simulado)
        if prefs.preferred_time_slots:
            # Por ahora, asumimos 60% de probabilidad de match
            scores.append(0.6)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _score_preferences_enhanced(self, clinician: Dict, user: User) -> float:
        """
        Score mejorado de preferencias para usuarios básicos.
        """
        base_score = self._score_preferences_basic(clinician, user)
        
        # Considerar edad del usuario y experiencia del clínico
        if user.profile_data and user.profile_data.age_range:
            age_groups = clinician.get('profile_features', {}).get('age_groups_served', [])
            
            # Mapear rangos de edad a grupos
            age_range_map = {
                "18-24": "young_adults",
                "25-34": "adults", 
                "35-44": "adults",
                "45-54": "adults",
                "55-64": "older_adults",
                "65+": "seniors"
            }
            
            user_group = age_range_map.get(user.profile_data.age_range, "adults")
            
            # Bonus si sirve al grupo de edad
            if user_group in age_groups or "adults" in age_groups:
                base_score = min(base_score + 0.1, 1.0)
        
        return base_score
    
    def _score_preferences_ml(self, clinician: Dict, user: User) -> float:
        """
        Score ML de preferencias basado en patrones históricos.
        """
        enhanced_score = self._score_preferences_enhanced(clinician, user)
        
        # Si el usuario tiene historial, aprender sus preferencias implícitas
        if user.interaction_history and user.get_positive_clinicians():
            # Analizar características comunes de clínicos exitosos
            positive_patterns = self._extract_preference_patterns(user)
            
            # Comparar con el clínico actual
            pattern_match = self._match_preference_patterns(
                clinician, 
                positive_patterns
            )
            
            # Combinar con score explícito
            ml_score = (enhanced_score * 0.4) + (pattern_match * 0.6)
            return ml_score
        
        return enhanced_score
    
    def _score_demographics(self, clinician: Dict, user: User) -> float:
        """
        Score demográfico para usuarios básicos y completos.
        """
        if not user.profile_data:
            return 0.5
        
        score = 0.0
        factors = 0
        
        # Experiencia con el tipo de terapia
        if user.profile_data.therapy_experience:
            years_exp = clinician.get('profile_features', {}).get('years_experience', 0)
            
            if user.profile_data.therapy_experience == "first_time":
                # Principiantes pueden preferir clínicos con experiencia media
                if 3 <= years_exp <= 10:
                    score += 1.0
                elif years_exp > 10:
                    score += 0.7
                else:
                    score += 0.5
            else:
                # Experimentados pueden preferir más experiencia
                if years_exp > 5:
                    score += min(years_exp / 20, 1.0)
                else:
                    score += 0.5
            
            factors += 1
        
        # Match de objetivos terapéuticos
        if user.profile_data.therapy_goals:
            specialties = clinician.get('profile_features', {}).get('specialties', [])
            
            # Mapear objetivos a especialidades
            goal_specialty_map = {
                "manage_symptoms": ["anxiety", "depression", "stress"],
                "personal_growth": ["self_esteem", "life_coaching", "mindfulness"],
                "relationship_issues": ["relationships", "couples", "family"],
                "trauma_healing": ["trauma", "ptsd", "abuse"]
            }
            
            matched_goals = 0
            for goal in user.profile_data.therapy_goals:
                related_specs = goal_specialty_map.get(goal, [])
                if any(spec in specialties for spec in related_specs):
                    matched_goals += 1
            
            if user.profile_data.therapy_goals:
                score += matched_goals / len(user.profile_data.therapy_goals)
                factors += 1
        
        return score / factors if factors > 0 else 0.5
    
    def _score_experience_match(self, clinician: Dict, user: User) -> float:
        """
        Score basado en match de experiencia para usuarios con historial.
        """
        if not user.interaction_history:
            return 0.5
        
        # Analizar si el usuario prefiere cierto nivel de experiencia
        positive_clinicians = user.get_positive_clinicians()
        if not positive_clinicians:
            return 0.5
        
        # Obtener años de experiencia promedio de clínicos exitosos
        from app.services.data_loader import data_loader
        
        exp_values = []
        for clin_id in positive_clinicians[:5]:
            clin_data = data_loader.get_clinician(clin_id)
            if clin_data:
                exp = clin_data.get('profile_features', {}).get('years_experience', 0)
                exp_values.append(exp)
        
        if not exp_values:
            return 0.5
        
        avg_preferred_exp = sum(exp_values) / len(exp_values)
        clinician_exp = clinician.get('profile_features', {}).get('years_experience', 0)
        
        # Score basado en cercanía a la preferencia
        exp_diff = abs(clinician_exp - avg_preferred_exp)
        if exp_diff <= 2:
            return 1.0
        elif exp_diff <= 5:
            return 0.8
        elif exp_diff <= 10:
            return 0.6
        else:
            return 0.4
    
    def _predict_success_rate(self, clinician: Dict, user: User) -> float:
        """
        Predice la probabilidad de éxito basada en historial.
        """
        if not user.interaction_history or not user.has_history():
            return 0.5
        
        # Factores de predicción
        factors = []
        weights_used = []
        
        # 1. Rating promedio del clínico
        avg_rating = clinician.get('performance_metrics', {}).get('avg_patient_rating')
        if avg_rating is not None and avg_rating > 0:
            factors.append(avg_rating / 5.0)
            weights_used.append(0.2)
        
        # 2. Tasa de retención del clínico
        retention = clinician.get('performance_metrics', {}).get('retention_rate')
        if retention is not None:
            factors.append(retention)
            weights_used.append(0.3)
        
        # 3. Match de especialidades con necesidades
        specialty_match = self._score_specialties_ml(clinician, user)
        if specialty_match is not None:
            factors.append(specialty_match)
            weights_used.append(0.3)
        
        # 4. Similitud con clínicos exitosos previos
        similarity_score = self._calculate_historical_similarity(clinician, user)
        if similarity_score is not None:
            factors.append(similarity_score)
            weights_used.append(0.2)
        
        # Promedio ponderado
        if factors and weights_used:
            # Normalizar pesos para que sumen 1
            total_weight = sum(weights_used)
            normalized_weights = [w / total_weight for w in weights_used]
            
            weighted_sum = sum(f * w for f, w in zip(factors, normalized_weights) if f is not None)
            return min(weighted_sum, 1.0)
        
        return 0.5
    
    def _score_load_balance(self, clinician: Dict) -> float:
        """
        Score para balancear la carga entre clínicos.
        """
        availability = clinician.get('availability_features', {})
        
        current_count = availability.get('current_patient_count', 0)
        max_capacity = availability.get('max_patient_capacity', 1)
        
        if max_capacity == 0:
            return 0.0
        
        load_ratio = current_count / max_capacity
        
        # Invertir para dar más score a menos cargados
        if load_ratio < 0.5:
            return 1.0
        elif load_ratio < 0.7:
            return 0.8
        elif load_ratio < 0.85:
            return 0.6
        elif load_ratio < 0.95:
            return 0.3
        else:
            return 0.1
    
    def _calculate_weighted_score(
        self, 
        components: ScoreComponents, 
        weights: Dict[str, float]
    ) -> float:
        """
        Calcula score ponderado básico.
        """
        score = (
            weights.get('availability', 0.25) * components.availability_match +
            weights.get('insurance', 0.20) * components.insurance_match +
            weights.get('specialties', 0.25) * components.specialty_match +
            weights.get('load_balance', 0.15) * components.load_balance_score +
            weights.get('preferences', 0.15) * components.preference_match
        )
        
        return score
    
    def _calculate_weighted_score_enhanced(
        self, 
        components: ScoreComponents, 
        weights: Dict[str, float]
    ) -> float:
        """
        Calcula score ponderado mejorado.
        """
        base_score = self._calculate_weighted_score(components, weights)
        
        # Agregar componente demográfico si existe
        if hasattr(components, 'demographic_match') and components.demographic_match is not None:
            demo_weight = weights.get('demographics', 0.0)
            base_score += demo_weight * components.demographic_match
        
        return min(base_score, 1.0)
    
    def _calculate_ml_score(
        self, 
        components: ScoreComponents, 
        weights: Dict[str, float]
    ) -> float:
        """
        Calcula score complejo para ML.
        """
        # Componentes base
        base_score = self._calculate_weighted_score_enhanced(components, weights)
        
        # Agregar componentes ML
        ml_components = 0.0
        ml_weight = 0.0
        
        if hasattr(components, 'experience_match') and components.experience_match is not None:
            ml_components += components.experience_match * 0.1
            ml_weight += 0.1
        
        if hasattr(components, 'success_prediction') and components.success_prediction is not None:
            ml_components += components.success_prediction * 0.2
            ml_weight += 0.2
        
        # Normalizar
        if ml_weight > 0:
            total_weight = 1.0 + ml_weight
            final_score = (base_score + ml_components) / total_weight
        else:
            final_score = base_score
        
        return min(final_score, 1.0)
    
    def _apply_basic_adjustments(
        self, 
        base_score: float, 
        clinician: Dict, 
        components: ScoreComponents
    ) -> float:
        """
        Ajustes básicos para usuarios anónimos.
        """
        final_score = base_score
        
        # Boost para clínicos nuevos (primeros 30 días)
        if settings.ENABLE_NEW_CLINICIAN_BOOST:
            if self._is_new_clinician(clinician):
                components.new_clinician_boost = settings.NEW_CLINICIAN_BOOST_FACTOR
                final_score *= components.new_clinician_boost
        
        # Penalización por sobrecarga
        load_factor = self._get_load_factor(clinician)
        if load_factor > settings.OVERLOAD_THRESHOLD:
            components.overload_penalty = settings.OVERLOAD_PENALTY_FACTOR
            final_score *= components.overload_penalty
        
        return min(final_score, 1.0)
    
    def _apply_enhanced_adjustments(
        self, 
        base_score: float, 
        clinician: Dict, 
        components: ScoreComponents,
        user: User
    ) -> float:
        """
        Ajustes mejorados para usuarios básicos.
        """
        # Aplicar ajustes básicos primero
        final_score = self._apply_basic_adjustments(base_score, clinician, components)
        
        # Boost por alta calificación
        avg_rating = clinician.get('performance_metrics', {}).get('avg_patient_rating')
        if avg_rating is not None and avg_rating >= 4.5:
            rating_boost = 1.05
            components.rating_boost = rating_boost
            final_score *= rating_boost
        
        # Boost por match perfecto de preferencias críticas
        if user.stated_preferences.gender_preference:
            if clinician.get('profile_features', {}).get('gender') == user.stated_preferences.gender_preference:
                if user.profile_data and user.profile_data.therapy_experience == "first_time":
                    # Mayor boost para principiantes
                    components.critical_preference_boost = 1.1
                    final_score *= 1.1
        
        return min(final_score, 1.0)
    
    def _apply_ml_adjustments(
        self, 
        base_score: float, 
        clinician: Dict, 
        components: ScoreComponents,
        user: User
    ) -> float:
        """
        Ajustes ML para usuarios con historial.
        """
        # Aplicar ajustes mejorados primero
        final_score = self._apply_enhanced_adjustments(
            base_score, 
            clinician, 
            components, 
            user
        )
        
        # Penalización si es similar a clínicos rechazados
        if user.interaction_history:
            rejected_similarity = self._calculate_rejected_similarity(
                clinician, 
                user
            )
            
            if rejected_similarity > 0.7:
                components.rejection_risk = 0.7
                final_score *= 0.7
        
        # Boost por tendencia positiva reciente
        if self._has_positive_trend(clinician):
            components.trending_boost = 1.05
            final_score *= 1.05
        
        return min(final_score, 1.0)
    
    def _is_new_clinician(self, clinician: Dict) -> bool:
        """
        Verifica si el clínico es nuevo.
        """
        # Por ahora, simulación basada en ID
        clinician_id = clinician.get('clinician_id', '')
        
        # Simular que 10% son nuevos
        import hashlib
        hash_val = int(hashlib.md5(f"{clinician_id}new".encode()).hexdigest()[:8], 16)
        return (hash_val % 100) < 10
    
    def _get_load_factor(self, clinician: Dict) -> float:
        """
        Obtiene el factor de carga actual.
        """
        availability = clinician.get('availability_features', {})
        
        current = availability.get('current_patient_count', 0)
        maximum = availability.get('max_patient_capacity', 1)
        
        return current / maximum if maximum > 0 else 1.0
    
    def _extract_preference_patterns(self, user: User) -> Dict:
        """
        Extrae patrones de preferencias del historial.
        """
        from app.services.data_loader import data_loader
        
        patterns = {
            'genders': {},
            'languages': {},
            'experience_ranges': [],
            'common_specialties': {}
        }
        
        positive_ids = user.get_positive_clinicians()[:10]
        
        for clin_id in positive_ids:
            clinician = data_loader.get_clinician(clin_id)
            if not clinician:
                continue
            
            profile = clinician.get('profile_features', {})
            
            # Contar géneros
            gender = profile.get('gender')
            if gender:
                patterns['genders'][gender] = patterns['genders'].get(gender, 0) + 1
            
            # Contar idiomas
            for lang in profile.get('languages', []):
                patterns['languages'][lang] = patterns['languages'].get(lang, 0) + 1
            
            # Experiencia
            exp = profile.get('years_experience', 0)
            patterns['experience_ranges'].append(exp)
            
            # Especialidades
            for spec in profile.get('specialties', []):
                patterns['common_specialties'][spec] = patterns['common_specialties'].get(spec, 0) + 1
        
        return patterns
    
    def _match_preference_patterns(self, clinician: Dict, patterns: Dict) -> float:
        """
        Calcula qué tan bien coincide un clínico con los patrones.
        """
        if not patterns:
            return 0.5
        
        profile = clinician.get('profile_features', {})
        scores = []
        
        # Género preferido
        if patterns['genders']:
            preferred_gender = max(patterns['genders'], key=patterns['genders'].get)
            if profile.get('gender') == preferred_gender:
                scores.append(1.0)
            else:
                scores.append(0.5)
        
        # Idiomas preferidos
        if patterns['languages']:
            clinician_langs = set(profile.get('languages', []))
            preferred_langs = set([lang for lang, count in patterns['languages'].items() if count >= 2])
            
            if clinician_langs & preferred_langs:
                scores.append(1.0)
            else:
                scores.append(0.3)
        
        # Rango de experiencia
        if patterns['experience_ranges']:
            avg_exp = sum(patterns['experience_ranges']) / len(patterns['experience_ranges'])
            clinician_exp = profile.get('years_experience', 0)
            
            exp_diff = abs(clinician_exp - avg_exp)
            if exp_diff <= 3:
                scores.append(1.0)
            elif exp_diff <= 6:
                scores.append(0.7)
            else:
                scores.append(0.4)
        
        # Especialidades comunes
        if patterns['common_specialties']:
            clinician_specs = set(profile.get('specialties', []))
            top_specs = set([spec for spec, count in patterns['common_specialties'].items() if count >= 2])
            
            if clinician_specs & top_specs:
                overlap_ratio = len(clinician_specs & top_specs) / len(top_specs)
                scores.append(min(overlap_ratio * 1.5, 1.0))
            else:
                scores.append(0.3)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _calculate_historical_similarity(self, clinician: Dict, user: User) -> float:
        """
        Calcula similitud con clínicos exitosos del historial.
        """
        from app.services.data_loader import data_loader
        
        positive_ids = user.get_positive_clinicians()[:5]
        if not positive_ids:
            return 0.5
        
        similarities = []
        
        for pos_id in positive_ids:
            pos_clinician = data_loader.get_clinician(pos_id)
            if not pos_clinician:
                continue
            
            # Calcular similitud entre clínicos
            sim = self._calculate_clinician_similarity(clinician, pos_clinician)
            similarities.append(sim)
        
        return sum(similarities) / len(similarities) if similarities else 0.5
    
    def _calculate_clinician_similarity(self, clin1: Dict, clin2: Dict) -> float:
        """
        Calcula similitud entre dos clínicos.
        """
        similarity_scores = []
        
        prof1 = clin1.get('profile_features', {})
        prof2 = clin2.get('profile_features', {})
        
        # Especialidades (Jaccard similarity)
        specs1 = set(prof1.get('specialties', []))
        specs2 = set(prof2.get('specialties', []))
        
        if specs1 and specs2:
            jaccard = len(specs1 & specs2) / len(specs1 | specs2)
            similarity_scores.append(jaccard)
        
        # Género
        if prof1.get('gender') == prof2.get('gender'):
            similarity_scores.append(0.8)
        else:
            similarity_scores.append(0.2)
        
        # Experiencia
        exp1 = prof1.get('years_experience', 0)
        exp2 = prof2.get('years_experience', 0)
        exp_sim = 1.0 - (abs(exp1 - exp2) / max(exp1, exp2, 1))
        similarity_scores.append(exp_sim)
        
        # Idiomas
        langs1 = set(prof1.get('languages', []))
        langs2 = set(prof2.get('languages', []))
        
        if langs1 and langs2:
            lang_overlap = len(langs1 & langs2) / len(langs1 | langs2)
            similarity_scores.append(lang_overlap)
        
        # Embeddings si están disponibles
        emb1 = clin1.get('embedding_features', {}).get('specialty_vector')
        emb2 = clin2.get('embedding_features', {}).get('specialty_vector')
        
        if emb1 and emb2 and len(emb1) == len(emb2):
            cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            similarity_scores.append(max(0, cosine_sim))
        
        return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    
    def _calculate_rejected_similarity(self, clinician: Dict, user: User) -> float:
        """
        Calcula similitud con clínicos rechazados.
        """
        from app.services.data_loader import data_loader
        
        rejected_ids = user.get_rejected_clinicians()[:3]
        if not rejected_ids:
            return 0.0
        
        similarities = []
        
        for rej_id in rejected_ids:
            rej_clinician = data_loader.get_clinician(rej_id)
            if not rej_clinician:
                continue
            
            sim = self._calculate_clinician_similarity(clinician, rej_clinician)
            similarities.append(sim)
        
        return max(similarities) if similarities else 0.0
    
    def _has_positive_trend(self, clinician: Dict) -> bool:
        """
        Verifica si el clínico tiene una tendencia positiva reciente.
        """
        # Por ahora, simulación basada en métricas
        performance = clinician.get('performance_metrics', {})
        
        avg_rating = performance.get('avg_patient_rating')
        retention = performance.get('retention_rate', 0)
        
        # Considerar positivo si tiene buenas métricas
        return (avg_rating is not None and avg_rating >= 4.3) and retention >= 0.8
    
    def _adapt_weights_from_history(self, base_weights: Dict[str, float], user: User) -> Dict[str, float]:
        """
        Adapta los pesos basándose en el historial del usuario.
        """
        if not user.interaction_history or not user.has_history():
            return base_weights
        
        adapted_weights = base_weights.copy()
        
        # Analizar qué factores fueron importantes en matches exitosos
        patterns = self._extract_preference_patterns(user)
        
        # Si el usuario siempre elige el mismo género, aumentar peso de preferencias
        if patterns['genders'] and len(patterns['genders']) == 1:
            adapted_weights['preferences'] *= 1.3
        
        # Si el usuario prioriza especialidades específicas, aumentar su peso
        if patterns['common_specialties']:
            top_spec_count = max(patterns['common_specialties'].values())
            if top_spec_count >= 3:
                adapted_weights['specialties'] *= 1.2
        
        # Normalizar para que sumen 1
        total = sum(adapted_weights.values())
        adapted_weights = {k: v/total for k, v in adapted_weights.items()}
        
        logger.debug(f"Pesos adaptados para usuario: {adapted_weights}")
        
        return adapted_weights