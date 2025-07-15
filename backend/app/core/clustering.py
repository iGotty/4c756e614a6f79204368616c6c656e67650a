# app/core/clustering.py
from typing import List, Dict, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

from app.models.user import User
from app.services.data_loader import data_loader

logger = logging.getLogger(__name__)

class UserClusteringService:
    """
    Servicio de clustering para usuarios registrados básicos.
    Agrupa usuarios similares para mejorar recomendaciones.
    """
    
    def __init__(self):
        self._cluster_cache = {}
        self._similarity_cache = {}
    
    def get_user_cluster(self, user: User) -> int:
        """
        Obtiene el cluster al que pertenece el usuario.
        """
        # Si el usuario ya tiene cluster asignado
        if user.embedding_features and user.embedding_features.user_cluster_id is not None:
            return user.embedding_features.user_cluster_id
        
        # Calcular cluster basado en características
        user_features = self._extract_user_features(user)
        
        # Por ahora, clustering simple basado en características principales
        cluster_id = self._calculate_simple_cluster(user_features)
        
        logger.debug(f"Usuario asignado a cluster {cluster_id}")
        
        return cluster_id
    
    def get_similar_users(self, user: User, n: int = 20) -> List[Dict]:
        """
        Encuentra usuarios similares basándose en características y preferencias.
        """
        # Cache key
        cache_key = f"{user.user_id}_{n}" if user.user_id else None
        if cache_key and cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # Obtener todos los usuarios
        all_users = list(data_loader.users.values()) if isinstance(data_loader.users, dict) else data_loader.users
        if not all_users:
            logger.warning("No hay usuarios cargados para clustering")
            return []
        
        # Filtrar usuarios del mismo tipo y con historial
        similar_type_users = []
        for user_data in all_users:
            # Verificar que sea un diccionario
            if not isinstance(user_data, dict):
                continue
                
            # Solo usuarios básicos o completos
            if user_data.get('registration_type') in ['basic', 'complete']:
                # Misma región geográfica
                if user_data.get('stated_preferences', {}).get('state') == user.stated_preferences.state:
                    similar_type_users.append(user_data)
        
        if not similar_type_users:
            return []
        
        # Calcular similitud
        user_features = self._extract_user_features(user)
        similarities = []
        
        for other_user_data in similar_type_users:
            # Skip mismo usuario
            if other_user_data.get('user_id') == user.user_id:
                continue
            
            other_features = self._extract_user_features_from_dict(other_user_data)
            similarity = self._calculate_user_similarity(user_features, other_features)
            
            similarities.append({
                'user_data': other_user_data,
                'similarity': similarity
            })
        
        # Ordenar por similitud
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Tomar top N
        similar_users = [item['user_data'] for item in similarities[:n]]
        
        # Cachear resultado
        if cache_key:
            self._similarity_cache[cache_key] = similar_users
        
        logger.debug(f"Encontrados {len(similar_users)} usuarios similares")
        
        return similar_users
    
    def _extract_user_features(self, user: User) -> Dict:
        """
        Extrae características del usuario para clustering.
        """
        features = {
            # Preferencias básicas
            'state': user.stated_preferences.state,
            'appointment_type': user.stated_preferences.appointment_type,
            'urgency': 1 if user.is_urgent() else 0,
            'has_insurance': 1 if user.has_insurance() else 0,
            
            # Necesidades clínicas (top 3)
            'clinical_needs': user.stated_preferences.clinical_needs[:3],
            
            # Preferencias
            'gender_pref': user.stated_preferences.gender_preference,
            'language': user.stated_preferences.language,
            
            # Demográficos si existen
            'age_range': None,
            'therapy_experience': None,
            'therapy_goals': []
        }
        
        # Agregar datos del perfil si existe
        if user.profile_data:
            features['age_range'] = user.profile_data.age_range
            features['therapy_experience'] = user.profile_data.therapy_experience
            features['therapy_goals'] = user.profile_data.therapy_goals
        
        return features
    
    def _extract_user_features_from_dict(self, user_data: Dict) -> Dict:
        """
        Extrae características de un diccionario de usuario.
        """
        prefs = user_data.get('stated_preferences', {})
        profile = user_data.get('profile_data', {})
        
        features = {
            'state': prefs.get('state'),
            'appointment_type': prefs.get('appointment_type'),
            'urgency': 1 if prefs.get('urgency_level') == 'immediate' else 0,
            'has_insurance': 1 if prefs.get('insurance_provider') else 0,
            'clinical_needs': prefs.get('clinical_needs', [])[:3],
            'gender_pref': prefs.get('gender_preference'),
            'language': prefs.get('language', 'English'),
            'age_range': profile.get('age_range'),
            'therapy_experience': profile.get('therapy_experience'),
            'therapy_goals': profile.get('therapy_goals', [])
        }
        
        return features
    
    def _calculate_simple_cluster(self, features: Dict) -> int:
        """
        Calcula un cluster simple basado en características principales.
        
        Clusters:
        0: Jóvenes primera vez, ansiedad/estrés
        1: Adultos con experiencia, problemas complejos
        2: Urgentes con seguro
        3: Flexibles sin seguro
        4: Terapia de pareja/familia
        5: Medicación
        6: Trauma/PTSD
        7: Otros
        """
        # Cluster por tipo de cita
        if features['appointment_type'] == 'medication':
            return 5
        
        # Cluster por necesidades especiales
        needs = features.get('clinical_needs', [])
        if any(need in ['trauma', 'ptsd', 'abuse'] for need in needs):
            return 6
        if any(need in ['relationships', 'couples', 'family'] for need in needs):
            return 4
        
        # Cluster por urgencia y seguro
        if features['urgency'] and features['has_insurance']:
            return 2
        if not features['urgency'] and not features['has_insurance']:
            return 3
        
        # Cluster por experiencia y edad
        if features.get('therapy_experience') == 'first_time':
            if features.get('age_range') in ['18-24', '25-34']:
                return 0
        elif features.get('therapy_experience') in ['some_experience', 'experienced']:
            return 1
        
        # Default
        return 7
    
    def _calculate_user_similarity(self, features1: Dict, features2: Dict) -> float:
        """
        Calcula similitud entre dos conjuntos de características de usuario.
        """
        similarity_scores = []
        
        # Estado (debe coincidir)
        if features1['state'] == features2['state']:
            similarity_scores.append(1.0)
        else:
            return 0.0  # No similar si no comparten estado
        
        # Tipo de cita
        if features1['appointment_type'] == features2['appointment_type']:
            similarity_scores.append(1.0)
        else:
            similarity_scores.append(0.0)
        
        # Urgencia
        if features1['urgency'] == features2['urgency']:
            similarity_scores.append(0.8)
        else:
            similarity_scores.append(0.2)
        
        # Seguro
        if features1['has_insurance'] == features2['has_insurance']:
            similarity_scores.append(0.7)
        else:
            similarity_scores.append(0.3)
        
        # Necesidades clínicas (Jaccard similarity)
        needs1 = set(features1.get('clinical_needs', []))
        needs2 = set(features2.get('clinical_needs', []))
        
        if needs1 and needs2:
            jaccard = len(needs1 & needs2) / len(needs1 | needs2)
            similarity_scores.append(jaccard)
        elif not needs1 and not needs2:
            similarity_scores.append(0.5)
        else:
            similarity_scores.append(0.0)
        
        # Preferencia de género
        if features1.get('gender_pref') == features2.get('gender_pref'):
            similarity_scores.append(0.6)
        else:
            similarity_scores.append(0.4)
        
        # Idioma
        if features1.get('language') == features2.get('language'):
            similarity_scores.append(0.7)
        else:
            similarity_scores.append(0.3)
        
        # Características demográficas (si existen)
        if features1.get('age_range') and features2.get('age_range'):
            if features1['age_range'] == features2['age_range']:
                similarity_scores.append(0.8)
            else:
                # Rangos adyacentes
                age_ranges = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
                idx1 = age_ranges.index(features1['age_range']) if features1['age_range'] in age_ranges else -1
                idx2 = age_ranges.index(features2['age_range']) if features2['age_range'] in age_ranges else -1
                
                if idx1 >= 0 and idx2 >= 0 and abs(idx1 - idx2) == 1:
                    similarity_scores.append(0.5)
                else:
                    similarity_scores.append(0.2)
        
        # Experiencia en terapia
        if features1.get('therapy_experience') and features2.get('therapy_experience'):
            if features1['therapy_experience'] == features2['therapy_experience']:
                similarity_scores.append(0.9)
            else:
                similarity_scores.append(0.4)
        
        # Objetivos terapéuticos
        goals1 = set(features1.get('therapy_goals', []))
        goals2 = set(features2.get('therapy_goals', []))
        
        if goals1 and goals2:
            goal_overlap = len(goals1 & goals2) / len(goals1 | goals2)
            similarity_scores.append(goal_overlap)
        
        # Calcular promedio ponderado
        if similarity_scores:
            # Dar más peso a necesidades clínicas y tipo de cita
            weights = [1.0, 1.5, 0.8, 0.7, 1.3, 0.6, 0.7, 0.8, 0.9, 1.0]
            weighted_sum = sum(s * w for s, w in zip(similarity_scores, weights[:len(similarity_scores)]))
            total_weight = sum(weights[:len(similarity_scores)])
            
            return weighted_sum / total_weight
        
        return 0.0
    
    def get_cluster_popular_clinicians(self, cluster_id: int, limit: int = 10) -> List[str]:
        """
        Obtiene los clínicos más populares en un cluster específico.
        """
        # Obtener usuarios del cluster
        cluster_users = []
        
        for user_data in data_loader.users:
            if user_data.get('registration_type') in ['basic', 'complete']:
                user_features = self._extract_user_features_from_dict(user_data)
                user_cluster = self._calculate_simple_cluster(user_features)
                
                if user_cluster == cluster_id:
                    cluster_users.append(user_data)
        
        if not cluster_users:
            return []
        
        # Contar interacciones positivas con clínicos
        clinician_interactions = {}
        
        for user_data in cluster_users:
            history = user_data.get('interaction_history', {})
            
            # Contar bookings (peso 3)
            for clin_id in history.get('clinicians_booked', []):
                clinician_interactions[clin_id] = clinician_interactions.get(clin_id, 0) + 3
            
            # Contar contactos (peso 2)
            for clin_id in history.get('clinicians_contacted', []):
                clinician_interactions[clin_id] = clinician_interactions.get(clin_id, 0) + 2
            
            # Contar vistas (peso 1)
            for clin_id in history.get('clinicians_viewed', []):
                clinician_interactions[clin_id] = clinician_interactions.get(clin_id, 0) + 1
        
        # Ordenar por popularidad
        popular_clinicians = sorted(
            clinician_interactions.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Retornar IDs
        return [clin_id for clin_id, _ in popular_clinicians[:limit]]
    
    def calculate_user_embedding(self, user: User) -> List[float]:
        """
        Calcula un embedding vectorial para el usuario.
        Útil para futuras mejoras con ML.
        """
        # Vector de características
        embedding = []
        
        # One-hot encoding del estado (simplificado)
        states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
        state_vector = [1.0 if user.stated_preferences.state == s else 0.0 for s in states]
        embedding.extend(state_vector)
        
        # Tipo de cita
        embedding.append(1.0 if user.stated_preferences.appointment_type == 'therapy' else 0.0)
        
        # Urgencia
        embedding.append(1.0 if user.is_urgent() else 0.0)
        
        # Seguro
        embedding.append(1.0 if user.has_insurance() else 0.0)
        
        # Necesidades clínicas (top 10 más comunes)
        common_needs = ['anxiety', 'depression', 'stress', 'trauma', 'relationships', 
                       'adhd', 'bipolar', 'ocd', 'ptsd', 'addiction']
        needs_vector = [1.0 if need in user.stated_preferences.clinical_needs else 0.0 
                       for need in common_needs]
        embedding.extend(needs_vector)
        
        # Normalizar
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding