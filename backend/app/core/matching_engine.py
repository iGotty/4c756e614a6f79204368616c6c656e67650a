from typing import List, Dict, Optional, Tuple
import time
from datetime import datetime, timedelta
import numpy as np

from app.models.user import User, StatedPreferences
from app.models.match import MatchResult, MatchResponse, ScoreComponents, MatchExplanation, OverlappingAttributes
from app.services.data_loader import data_loader
from app.core.filters import MatchingFilters
from app.core.scoring import ScoringEngine
from app.core.clustering import UserClusteringService
from app.core.collaborative import CollaborativeFilteringEngine
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MatchingEngine:
    """
    Motor principal de matching con soporte para los 3 tipos de usuario.
    """
    
    def __init__(self):
        self.filters = MatchingFilters()
        self.scoring = ScoringEngine()
        self.clustering = UserClusteringService()
        self.collaborative = CollaborativeFilteringEngine()
        
    def match(
        self, 
        user: User, 
        limit: int = 10,
        include_explanations: bool = True
    ) -> MatchResponse:
        """
        Pipeline principal que delega según el tipo de usuario.
        """
        start_time = time.time()
        
        print(f"\n=== DEBUG MATCH PRINCIPAL ===")
        print(f"Tipo de usuario: {user.registration_type}")
        print(f"Limit recibido: {limit}")
        
        # Logging del tipo de matching
        logger.info(f"Iniciando matching para usuario {user.registration_type}")
        logger.info(f"Estado: {user.stated_preferences.state}, "
                   f"Tipo: {user.stated_preferences.appointment_type}, "
                   f"Urgencia: {user.stated_preferences.urgency_level}")
        
        # Delegar según tipo de usuario
        if user.is_anonymous():
            print(f"Delegando a _match_anonymous con limit={limit}")
            response = self._match_anonymous(user, limit, include_explanations)
        elif user.is_basic():
            response = self._match_basic(user, limit, include_explanations)
        else:  # complete/with history
            response = self._match_complete(user, limit, include_explanations)
        
        # Agregar tiempo de procesamiento
        response.processing_time_ms = (time.time() - start_time) * 1000
        
        # Logging de performance
        if response.processing_time_ms > settings.RESPONSE_TIME_TARGET_MS:
            logger.warning(f"⚠️ Tiempo excedido: {response.processing_time_ms:.2f}ms")
        
        logger.info(f"Matching completado: {response.total_matches} resultados "
                   f"en {response.processing_time_ms:.2f}ms")
        
        print(f"Respuesta final: {response.total_matches} matches")
        print("=== FIN DEBUG PRINCIPAL ===\n")
        
        return response
    
    def _match_anonymous(
        self, 
        user: User, 
        limit: int,
        include_explanations: bool
    ) -> MatchResponse:
        """
        Estrategia 1: Usuario Anónimo (Cold Start)
        - Solo content-based filtering
        - Top 5 matches genéricos
        """
        logger.debug("Ejecutando matching para usuario anónimo")
        print(f"\n=== DEBUG MATCHING ANÓNIMO ===")
        print(f"Limit solicitado: {limit}")
        
        # 1. Obtener clínicos y aplicar filtros duros
        all_clinicians = data_loader.get_clinicians_for_matching()
        print(f"Total clínicos en sistema: {len(all_clinicians)}")
        
        filtered_clinicians = self.filters.apply_hard_filters(
            clinicians=all_clinicians,
            preferences=user.stated_preferences
        )
        
        print(f"Después de filtros duros: {len(filtered_clinicians)} clínicos")
        
        if not filtered_clinicians:
            return self._empty_response(user, 0)
        
        # 2. Scoring básico (content-based)
        weights = self._get_weights_for_user(user)
        scored_clinicians = []
        
        for clinician in filtered_clinicians:
            score, components = self.scoring.calculate_anonymous_score(
                clinician=clinician,
                user=user,
                weights=weights
            )
            scored_clinicians.append((clinician, score, components))
        
        print(f"Después de scoring: {len(scored_clinicians)} clínicos")
        
        # 3. Ordenar y limitar según el parámetro limit
        scored_clinicians.sort(key=lambda x: x[1], reverse=True)
        print(f"Aplicando límite de {limit}...")
        top_clinicians = scored_clinicians[:limit]
        
        print(f"Top clínicos seleccionados: {len(top_clinicians)}")
        
        # 4. Generar respuesta
        matches = self._create_match_results(
            top_clinicians, 
            user, 
            include_explanations,
            strategy="content_based"
        )
        
        print(f"Matches finales generados: {len(matches)}")
        print("=== FIN DEBUG ===\n")
        
        return MatchResponse(
            user_type=user.registration_type,
            total_matches=len(matches),
            matches=matches,
            processing_time_ms=0,  # Se actualiza en el método principal
            filters_applied=self._get_filters_summary(user),
            weights_used=weights,
            matching_strategy="content_based_anonymous"
        )
    
    def _match_basic(
        self, 
        user: User, 
        limit: int,
        include_explanations: bool
    ) -> MatchResponse:
        """
        Estrategia 2: Usuario Registrado Básico
        - Content-based enriquecido + clustering
        - Matches personalizados usando perfil demográfico
        """
        logger.debug("Ejecutando matching para usuario básico")
        
        # 1. Filtros duros
        all_clinicians = data_loader.get_clinicians_for_matching()
        filtered_clinicians = self.filters.apply_hard_filters(
            clinicians=all_clinicians,
            preferences=user.stated_preferences
        )
        
        if not filtered_clinicians:
            return self._empty_response(user, 0)
        
        # 2. Obtener cluster del usuario y usuarios similares
        user_cluster = self.clustering.get_user_cluster(user)
        similar_users = self.clustering.get_similar_users(user, n=20)
        
        logger.debug(f"Usuario en cluster {user_cluster}, "
                    f"{len(similar_users)} usuarios similares encontrados")
        
        # 3. Scoring enriquecido (content + demografía + clustering)
        weights = self._get_weights_for_user(user)
        scored_clinicians = []
        
        for clinician in filtered_clinicians:
            # Score base content-based
            base_score, components = self.scoring.calculate_basic_score(
                clinician=clinician,
                user=user,
                weights=weights
            )
            
            # Boost por popularidad en el cluster
            cluster_boost = self._calculate_cluster_boost(
                clinician, 
                similar_users
            )
            
            # Score final
            final_score = base_score * (1 + cluster_boost * 0.2)
            components.cluster_boost = 1 + cluster_boost * 0.2
            
            scored_clinicians.append((clinician, final_score, components))
        
        # 4. Ordenar y diversificar
        scored_clinicians.sort(key=lambda x: x[1], reverse=True)
        
        if settings.ENABLE_DIVERSITY_BOOST:
            scored_clinicians = self._apply_diversity(scored_clinicians)
        
        # 5. Limitar resultados
        top_clinicians = scored_clinicians[:limit]
        
        # 6. Generar respuesta
        matches = self._create_match_results(
            top_clinicians, 
            user, 
            include_explanations,
            strategy="content_clustering"
        )
        
        return MatchResponse(
            user_type=user.registration_type,
            total_matches=len(matches),
            matches=matches,
            processing_time_ms=0,
            filters_applied=self._get_filters_summary(user),
            weights_used=weights,
            matching_strategy="content_based_clustering",
            user_cluster_id=user_cluster
        )
    
    def _match_complete(
        self, 
        user: User, 
        limit: int,
        include_explanations: bool
    ) -> MatchResponse:
        """
        Estrategia 3: Usuario con Historial (Warm Start)
        - Collaborative filtering + ML
        - Predicciones basadas en comportamiento
        """
        logger.debug("Ejecutando matching para usuario con historial")
        
        # 1. Filtros duros
        all_clinicians = data_loader.get_clinicians_for_matching()
        filtered_clinicians = self.filters.apply_hard_filters(
            clinicians=all_clinicians,
            preferences=user.stated_preferences
        )
        
        # Excluir clínicos ya vistos/rechazados
        excluded_ids = set(user.get_rejected_clinicians())
        if user.interaction_history:
            # Opcionalmente excluir los ya contactados
            excluded_ids.update(user.interaction_history.clinicians_booked)
        
        filtered_clinicians = [
            c for c in filtered_clinicians 
            if c.get('clinician_id') not in excluded_ids
        ]
        
        if not filtered_clinicians:
            return self._empty_response(user, 0)
        
        # 2. Obtener predicciones collaborative filtering
        cf_predictions = self.collaborative.get_predictions(
            user=user,
            candidate_clinicians=[c.get('clinician_id') for c in filtered_clinicians]
        )
        
        # 3. Scoring híbrido (content + collaborative + histórico)
        weights = self._get_weights_for_user(user)
        scored_clinicians = []
        
        for clinician in filtered_clinicians:
            clinician_id = clinician.get('clinician_id')
            
            # Score content-based
            content_score, components = self.scoring.calculate_complete_score(
                clinician=clinician,
                user=user,
                weights=weights
            )
            
            # Score collaborative filtering
            cf_score = cf_predictions.get(clinician_id, 0.5)
            
            # Combinar scores (60% content, 40% collaborative)
            final_score = (content_score * 0.6) + (cf_score * 0.4)
            
            # Agregar componentes
            components.collaborative_score = cf_score
            components.content_score = content_score
            
            # Boost por éxito histórico similar
            history_boost = self._calculate_history_boost(clinician, user)
            final_score *= (1 + history_boost * 0.15)
            components.history_boost = 1 + history_boost * 0.15
            
            scored_clinicians.append((clinician, final_score, components))
        
        # 4. Ordenar y aplicar estrategias avanzadas
        scored_clinicians.sort(key=lambda x: x[1], reverse=True)
        
        # Diversificar para evitar "filter bubble"
        if settings.ENABLE_DIVERSITY_BOOST:
            scored_clinicians = self._apply_advanced_diversity(
                scored_clinicians, 
                user
            )
        
        # 5. Limitar resultados
        top_clinicians = scored_clinicians[:limit]
        
        # 6. Generar respuesta
        matches = self._create_match_results(
            top_clinicians, 
            user, 
            include_explanations,
            strategy="collaborative_ml"
        )
        
        return MatchResponse(
            user_type=user.registration_type,
            total_matches=len(matches),
            matches=matches,
            processing_time_ms=0,
            filters_applied=self._get_filters_summary(user),
            weights_used=weights,
            matching_strategy="collaborative_filtering_ml",
            predictions_used=len(cf_predictions)
        )
    
    def _calculate_cluster_boost(
        self, 
        clinician: Dict, 
        similar_users: List[Dict]
    ) -> float:
        """
        Calcula boost basado en popularidad del clínico entre usuarios similares.
        """
        if not similar_users:
            return 0.0
        
        clinician_id = clinician.get('clinician_id')
        interactions_count = 0
        positive_count = 0
        
        for user_data in similar_users:
            history = user_data.get('interaction_history', {})
            
            # Contar interacciones
            if clinician_id in history.get('clinicians_viewed', []):
                interactions_count += 1
            
            if clinician_id in history.get('clinicians_booked', []):
                positive_count += 2  # Peso doble para bookings
            
            if clinician_id in history.get('clinicians_contacted', []):
                positive_count += 1
        
        if interactions_count == 0:
            return 0.0
        
        # Boost proporcional a interacciones positivas
        return min(positive_count / len(similar_users), 1.0)
    
    def _calculate_history_boost(
        self, 
        clinician: Dict, 
        user: User
    ) -> float:
        """
        Calcula boost basado en éxito histórico con pacientes similares.
        """
        if not user.interaction_history:
            return 0.0
        
        # Obtener clínicos exitosos previos
        successful_clinicians = user.get_positive_clinicians()
        if not successful_clinicians:
            return 0.0
        
        # Comparar características
        similarity_scores = []
        
        for success_id in successful_clinicians[:5]:  # Top 5 más recientes
            success_clinician = data_loader.get_clinician(success_id)
            if not success_clinician:
                continue
            
            # Calcular similitud
            similarity = self._calculate_clinician_similarity(
                clinician, 
                success_clinician
            )
            similarity_scores.append(similarity)
        
        if not similarity_scores:
            return 0.0
        
        # Retornar promedio de similitud
        return sum(similarity_scores) / len(similarity_scores)
    
    def _calculate_clinician_similarity(
        self, 
        clinician1: Dict, 
        clinician2: Dict
    ) -> float:
        """
        Calcula similitud entre dos clínicos.
        """
        similarity = 0.0
        factors = 0
        
        # Especialidades compartidas
        spec1 = set(clinician1.get('profile_features', {}).get('specialties', []))
        spec2 = set(clinician2.get('profile_features', {}).get('specialties', []))
        
        if spec1 and spec2:
            jaccard = len(spec1 & spec2) / len(spec1 | spec2)
            similarity += jaccard
            factors += 1
        
        # Género
        if (clinician1.get('profile_features', {}).get('gender') == 
            clinician2.get('profile_features', {}).get('gender')):
            similarity += 0.5
            factors += 1
        
        # Años de experiencia (similar rango)
        exp1 = clinician1.get('profile_features', {}).get('years_experience', 0)
        exp2 = clinician2.get('profile_features', {}).get('years_experience', 0)
        
        if abs(exp1 - exp2) <= 3:
            similarity += 0.7
            factors += 1
        
        # Embeddings si están disponibles
        emb1 = clinician1.get('embedding_features', {}).get('specialty_vector')
        emb2 = clinician2.get('embedding_features', {}).get('specialty_vector')
        
        if emb1 and emb2:
            # Cosine similarity
            cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            similarity += max(0, cosine_sim)
            factors += 1
        
        return similarity / factors if factors > 0 else 0.0
    
    def _apply_diversity(
        self, 
        scored_clinicians: List[Tuple[Dict, float, ScoreComponents]]
    ) -> List[Tuple[Dict, float, ScoreComponents]]:
        """
        Aplica diversificación básica para usuarios anónimos/básicos.
        """
        # No limitar el número de resultados aquí
        if len(scored_clinicians) <= 3:  # Solo aplicar diversidad si hay más de 3
            return scored_clinicians
        
        diversified = []
        seen_attributes = {
            'genders': set(),
            'specialties': set(),
            'languages': set()
        }
        
        # Top 3 sin cambios
        for item in scored_clinicians[:3]:
            diversified.append(item)
            self._update_seen_attributes(item[0], seen_attributes)
        
        # Resto con boost de diversidad
        for clinician, score, components in scored_clinicians[3:]:
            diversity_boost = self._calculate_diversity_boost(
                clinician, 
                seen_attributes
            )
            
            components.diversity_boost = diversity_boost
            adjusted_score = score * diversity_boost
            
            diversified.append((clinician, adjusted_score, components))
            self._update_seen_attributes(clinician, seen_attributes)
        
        # Re-ordenar
        diversified[3:] = sorted(diversified[3:], key=lambda x: x[1], reverse=True)
        
        return diversified
    
    def _apply_advanced_diversity(
        self, 
        scored_clinicians: List[Tuple[Dict, float, ScoreComponents]],
        user: User
    ) -> List[Tuple[Dict, float, ScoreComponents]]:
        """
        Aplica diversificación avanzada para usuarios con historial.
        Evita "filter bubble" introduciendo exploración.
        """
        if len(scored_clinicians) <= 5:
            return scored_clinicians
        
        # Separar en exploitation (top 70%) y exploration (30%)
        exploitation_size = int(len(scored_clinicians) * 0.7)
        
        exploitation = scored_clinicians[:exploitation_size]
        exploration = scored_clinicians[exploitation_size:]
        
        # Aplicar diversidad a exploitation
        exploitation_diverse = self._apply_diversity(exploitation)
        
        # Para exploration, boost clínicos muy diferentes al historial
        if user.interaction_history and exploration:
            positive_clinicians = [
                data_loader.get_clinician(cid) 
                for cid in user.get_positive_clinicians()[:5]
            ]
            positive_clinicians = [c for c in positive_clinicians if c]
            
            exploration_boosted = []
            for clinician, score, components in exploration:
                # Calcular "novedad" (qué tan diferente es)
                novelty = 1.0
                if positive_clinicians:
                    similarities = [
                        self._calculate_clinician_similarity(clinician, pos)
                        for pos in positive_clinicians
                    ]
                    avg_similarity = sum(similarities) / len(similarities)
                    novelty = 1.0 - avg_similarity
                
                # Boost por novedad
                novelty_boost = 1 + (novelty * 0.3)
                components.novelty_boost = novelty_boost
                
                exploration_boosted.append(
                    (clinician, score * novelty_boost, components)
                )
            
            # Ordenar exploration por nuevo score
            exploration_boosted.sort(key=lambda x: x[1], reverse=True)
            
            # Combinar: 70% exploitation, 30% exploration
            result = exploitation_diverse[:7] + exploration_boosted[:3]
        else:
            result = exploitation_diverse
        
        return result
    
    def _update_seen_attributes(
        self, 
        clinician: Dict, 
        seen_attributes: Dict
    ):
        """
        Actualiza los atributos vistos para diversificación.
        """
        profile = clinician.get('profile_features', {})
        
        seen_attributes['genders'].add(profile.get('gender'))
        seen_attributes['specialties'].update(profile.get('specialties', [])[:2])
        seen_attributes['languages'].update(profile.get('languages', [])[:1])
    
    def _calculate_diversity_boost(
        self, 
        clinician: Dict, 
        seen_attributes: Dict
    ) -> float:
        """
        Calcula boost de diversidad basado en atributos no vistos.
        """
        boost = 1.0
        profile = clinician.get('profile_features', {})
        
        # Boost por género diferente
        if profile.get('gender') not in seen_attributes['genders']:
            boost *= 1.05
        
        # Boost por especialidades nuevas
        new_specialties = (set(profile.get('specialties', [])) - 
                          seen_attributes['specialties'])
        if new_specialties:
            boost *= 1.03
        
        # Boost por idiomas nuevos
        new_languages = (set(profile.get('languages', [])) - 
                        seen_attributes['languages'])
        if new_languages:
            boost *= 1.02
        
        return boost
    
    def _calculate_overlapping_attributes(
        self,
        clinician: Dict,
        user: User
    ) -> OverlappingAttributes:
        """
        Calcula qué atributos del usuario coinciden con el clínico.
        """
        preferences = user.stated_preferences
        basic_info = clinician.get('basic_info', {})
        profile = clinician.get('profile_features', {})
        
        # 1. Estado - siempre debe ser True porque pasó los filtros duros
        state_match = preferences.state in basic_info.get('license_states', [])
        
        # 2. Idioma - verificar si habla el idioma preferido
        language_match = False
        if preferences.language:
            clinician_languages = profile.get('languages', [])
            language_match = preferences.language in clinician_languages
        else:
            # Si no hay preferencia de idioma, considerarlo como match
            language_match = True
        
        # 3. Género - verificar si coincide con la preferencia
        gender_match = True  # Por defecto es True si no hay preferencia
        if preferences.gender_preference:
            clinician_gender = profile.get('gender', '')
            gender_match = clinician_gender == preferences.gender_preference
        
        # 4. Seguro - verificar si acepta el seguro del usuario
        insurance_match = self._accepts_insurance(clinician, user)
        
        # 5. Especialidades - encontrar las que coinciden
        matching_specialties = []
        if preferences.clinical_needs:
            clinician_specialties = set(profile.get('specialties', []))
            user_needs = set(preferences.clinical_needs)
            matching_specialties = list(user_needs & clinician_specialties)
        
        # 6. Horarios - encontrar los que coinciden (simulado)
        matching_time_slots = []
        if preferences.preferred_time_slots:
            # Usar los datos marcados por filters si existen
            matching_time_slots = clinician.get('_matching_time_slots', [])
            
            # Si no hay datos marcados, simular
            if not matching_time_slots:
                import hashlib
                clinician_id = clinician.get('clinician_id', '')
                for slot in preferences.preferred_time_slots:
                    # Simulación determinística de disponibilidad
                    hash_val = int(hashlib.md5(f"{clinician_id}{slot}".encode()).hexdigest()[:8], 16)
                    slot_probabilities = {
                        "mornings": 80,
                        "afternoons": 90,
                        "evenings": 70,
                        "weekends": 50
                    }
                    if (hash_val % 100) < slot_probabilities.get(slot, 50):
                        matching_time_slots.append(slot)
        
        # 7. Tipo de cita - siempre debe ser True porque pasó los filtros duros
        appointment_type_match = preferences.appointment_type in basic_info.get('appointment_types', [])
        
        return OverlappingAttributes(
            state=state_match,
            language=language_match,
            gender_preference=gender_match,
            insurance=insurance_match,
            specialties=matching_specialties,
            time_slots=matching_time_slots,
            appointment_type=appointment_type_match
        )
    
    def _create_match_results(
        self,
        scored_clinicians: List[Tuple[Dict, float, ScoreComponents]],
        user: User,
        include_explanations: bool,
        strategy: str
    ) -> List[MatchResult]:
        """
        Crea los objetos MatchResult para la respuesta.
        """
        matches = []
        
        for rank, (clinician, score, components) in enumerate(scored_clinicians, 1):
            basic_info = clinician.get('basic_info', {})
            profile = clinician.get('profile_features', {})
            availability = clinician.get('availability_features', {})
            
            # Normalizar score para que nunca exceda 1.0
            normalized_score = min(score, 1.0)
            
            # Calcular atributos coincidentes
            overlapping_attrs = self._calculate_overlapping_attributes(clinician, user)
            
            # Generar explicación
            explanation = None
            if include_explanations:
                explanation = self._generate_explanation(
                    clinician=clinician,
                    user=user,
                    components=components,
                    strategy=strategy,
                    overlapping_attrs=overlapping_attrs
                )
            
            # Crear match result
            match = MatchResult(
                clinician_id=clinician.get('clinician_id'),
                clinician_name=basic_info.get('full_name', 'Unknown'),
                match_score=normalized_score,  # Score normalizado
                rank_position=rank,
                is_available=availability.get('immediate_availability', False),
                accepts_insurance=self._accepts_insurance(clinician, user),
                specialties=profile.get('specialties', []),
                languages=profile.get('languages', []),
                gender=profile.get('gender', 'unknown'),
                years_experience=profile.get('years_experience', 0),
                overlapping_attributes=overlapping_attrs,
                score_components=components,
                explanation=explanation,
                matching_strategy=strategy
            )
            
            matches.append(match)
        
        return matches
    
    def _generate_explanation(
        self,
        clinician: Dict,
        user: User,
        components: ScoreComponents,
        strategy: str,
        overlapping_attrs: OverlappingAttributes
    ) -> MatchExplanation:
        """
        Genera explicación adaptada al tipo de usuario y estrategia.
        """
        primary_reasons = []
        matching_attributes = []
        insights = []
        
        basic_info = clinician.get('basic_info', {})
        profile = clinician.get('profile_features', {})
        availability = clinician.get('availability_features', {})
        
        # Common reasons
        if availability.get('immediate_availability') and user.is_urgent():
            primary_reasons.append("Available immediately")
            matching_attributes.append("availability")
        elif availability.get('immediate_availability'):
            primary_reasons.append("Available for appointments")
            matching_attributes.append("availability")
        
        # Only add insurance message if user has insurance
        if overlapping_attrs.insurance and user.has_insurance():
            primary_reasons.append(f"Accepts your {user.stated_preferences.insurance_provider} insurance")
            matching_attributes.append("insurance")
        elif overlapping_attrs.insurance and not user.has_insurance():
            primary_reasons.append("Accepts patients without insurance")
            matching_attributes.append("no_insurance")
        
        # Specialties
        if overlapping_attrs.specialties:
            spec_list = overlapping_attrs.specialties[:2]
            primary_reasons.append(f"Specializes in {', '.join(spec_list)}")
            matching_attributes.extend(spec_list)
        elif profile.get('specialties'):
            # If no specific needs, mention general specialties
            specs = profile.get('specialties', [])[:2]
            if specs:
                primary_reasons.append(f"Specializes in {', '.join(specs)}")
        
        # Gender preference if matches
        if overlapping_attrs.gender_preference and user.stated_preferences.gender_preference:
            matching_attributes.append("gender_preference")
        
        # Language if matches
        if overlapping_attrs.language and user.stated_preferences.language:
            matching_attributes.append("language")
        
        # Time slots if match
        if overlapping_attrs.time_slots:
            matching_attributes.extend([f"time_{slot}" for slot in overlapping_attrs.time_slots[:2]])
        
        # If no specific reasons, add generic ones
        if not primary_reasons:
            if availability.get('accepting_new_patients'):
                primary_reasons.append("Accepting new patients")
            if profile.get('years_experience', 0) > 5:
                primary_reasons.append(f"{profile.get('years_experience')} years of experience")
            if len(profile.get('languages', [])) > 1:
                primary_reasons.append("Multilingual")
        
        # Insights by strategy
        if strategy == "content_based":
            insights.append("Recommended based on profile compatibility")
            
        elif strategy == "content_clustering":
            cluster_boost = getattr(components, 'cluster_boost', None)
            if cluster_boost is not None and cluster_boost > 1.1:
                insights.append("Popular among users similar to you")
                
        elif strategy == "collaborative_ml":
            collaborative_score = getattr(components, 'collaborative_score', None)
            if collaborative_score is not None and collaborative_score > 0.7:
                insights.append("High success probability based on your history")
            
            novelty_boost = getattr(components, 'novelty_boost', None)
            if novelty_boost is not None and novelty_boost > 1.2:
                insights.append("Different profile to expand your options")
        
        # Score breakdown
        score_breakdown = {
            "Availability": round(components.availability_match * 100),
            "Compatibility": round(components.specialty_match * 100),
            "Preferences": round(components.preference_match * 100)
        }
        
        collaborative_score = getattr(components, 'collaborative_score', None)
        if collaborative_score is not None:
            score_breakdown["ML Prediction"] = round(collaborative_score * 100)
        
        return MatchExplanation(
            primary_reasons=primary_reasons[:3],
            matching_attributes=list(set(matching_attributes)),
            score_breakdown=score_breakdown,
            insights=insights,
            confidence_level=self._calculate_confidence(components, strategy)
        )
    
    def _calculate_confidence(
        self, 
        components: ScoreComponents, 
        strategy: str
    ) -> str:
        """
        Calcula el nivel de confianza de la recomendación.
        """
        if strategy == "collaborative_ml":
            collaborative_score = getattr(components, 'collaborative_score', None)
            if collaborative_score is not None:
                if collaborative_score > 0.8:
                    return "very_high"
                elif collaborative_score > 0.6:
                    return "high"
        
        # Para otros casos, usar score general
        avg_score = (components.availability_match + 
                    components.specialty_match + 
                    components.preference_match) / 3
        
        if avg_score > 0.8:
            return "high"
        elif avg_score > 0.6:
            return "medium"
        else:
            return "low"
    
    def _accepts_insurance(self, clinician: Dict, user: User) -> bool:
        """
        Verifica si el clínico acepta el seguro del usuario.
        """
        if not user.has_insurance():
            return True
        
        # Simulación determinística
        import hashlib
        hash_input = f"{clinician.get('clinician_id')}{user.stated_preferences.insurance_provider}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        return (hash_value % 100) < 70
    
    def _get_weights_for_user(self, user: User) -> Dict[str, float]:
        """
        Obtiene los pesos según tipo de usuario y urgencia.
        """
        if user.is_urgent():
            return settings.WEIGHTS_ANONYMOUS_URGENT
        else:
            return settings.WEIGHTS_ANONYMOUS_FLEXIBLE
    
    def _get_filters_summary(self, user: User) -> Dict[str, any]:
        """
        Resume los filtros aplicados.
        """
        return {
            "state": user.stated_preferences.state,
            "appointment_type": user.stated_preferences.appointment_type,
            "language": user.stated_preferences.language,
            "insurance": user.stated_preferences.insurance_provider,
            "urgency": user.stated_preferences.urgency_level
        }
    
    def _empty_response(self, user: User, processing_time: float) -> MatchResponse:
        """
        Respuesta cuando no hay matches.
        """
        return MatchResponse(
            user_type=user.registration_type,
            total_matches=0,
            matches=[],
            processing_time_ms=processing_time,
            filters_applied=self._get_filters_summary(user),
            weights_used={},
            matching_strategy="content_based_anonymous",  # Agregado
            message="No clinicians found matching the specified criteria",
            warnings=["Consider broadening your search criteria"]
        )