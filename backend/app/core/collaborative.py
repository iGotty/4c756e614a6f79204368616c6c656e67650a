# app/core/collaborative.py
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict
import logging

from app.models.user import User

logger = logging.getLogger(__name__)

class CollaborativeFilteringEngine:
    """
    Motor de filtrado colaborativo para usuarios con historial.
    Versión simplificada para evitar errores con datos faltantes.
    """
    
    def __init__(self):
        self._user_item_matrix = None
        self._similarity_matrix = None
        self._predictions_cache = {}
        # Inicialización diferida para evitar problemas
        self._initialized = False
    
    def _initialize_if_needed(self):
        """Inicializa las matrices solo cuando se necesitan."""
        if not self._initialized:
            try:
                self._build_matrices()
                self._initialized = True
            except Exception as e:
                logger.warning(f"No se pudo inicializar collaborative filtering: {e}")
                self._initialized = True  # Marcar como inicializado para no reintentar
    
    def get_predictions(
        self, 
        user: User, 
        candidate_clinicians: List[str]
    ) -> Dict[str, float]:
        """
        Obtiene predicciones de score para una lista de clínicos candidatos.
        """
        # Inicializar si es necesario
        self._initialize_if_needed()
        
        # Cache key
        cache_key = f"{user.user_id}_{','.join(sorted(candidate_clinicians[:10]))}" if user.user_id else "anonymous"
        if cache_key in self._predictions_cache:
            return self._predictions_cache[cache_key]
        
        predictions = {}
        
        # Si no hay suficiente historial o hubo error, usar predicciones neutrales
        if not user.has_history() or self._user_item_matrix is None:
            logger.debug("Sin historial suficiente para collaborative filtering")
            for clin_id in candidate_clinicians:
                predictions[clin_id] = 0.5  # Score neutral
            return predictions
        
        try:
            # Obtener predicciones usando método simplificado
            user_based_preds = self._user_based_predictions(user, candidate_clinicians)
            
            # Por ahora solo user-based para evitar complejidad
            for clin_id in candidate_clinicians:
                predictions[clin_id] = user_based_preds.get(clin_id, 0.5)
            
            # Cachear resultado
            self._predictions_cache[cache_key] = predictions
            
        except Exception as e:
            logger.warning(f"Error en predicciones colaborativas: {e}")
            # Fallback a predicciones neutrales
            for clin_id in candidate_clinicians:
                predictions[clin_id] = 0.5
        
        return predictions
    
    def _build_matrices(self):
        """
        Construye las matrices necesarias para collaborative filtering.
        Versión robusta que maneja datos faltantes.
        """
        try:
            from app.services.data_loader import data_loader
            
            # Obtener todas las interacciones
            all_interactions = data_loader.interactions
            if not all_interactions:
                logger.warning("No hay interacciones para collaborative filtering")
                return
            
            # Construir matriz usuario-item
            user_clinician_scores = defaultdict(lambda: defaultdict(float))
            
            for interaction in all_interactions:
                user_id = interaction.get('user_id')
                clinician_id = interaction.get('clinician_id')
                
                if not user_id or not clinician_id:
                    continue
                
                # Calcular score basado en el outcome
                score = self._interaction_to_score(interaction)
                
                # Solo procesar scores válidos
                if score is not None and -1 <= score <= 1:
                    # Actualizar matriz (mantener el máximo score)
                    current_score = user_clinician_scores[user_id][clinician_id]
                    user_clinician_scores[user_id][clinician_id] = max(current_score, score)
            
            # Convertir a diccionario regular
            self._user_item_matrix = dict(user_clinician_scores)
            
            logger.info(f"Matriz colaborativa construida: {len(self._user_item_matrix)} usuarios")
            
        except Exception as e:
            logger.error(f"Error construyendo matrices colaborativas: {e}")
            self._user_item_matrix = None
    
    def _interaction_to_score(self, interaction: Dict) -> float:
        """
        Convierte una interacción en un score numérico.
        Maneja casos donde faltan datos.
        """
        try:
            outcome = interaction.get('outcome', {})
            action = outcome.get('action', 'viewed')
            
            # Mapeo de acciones a scores
            action_scores = {
                'booked': 1.0,          # Máximo score por booking
                'contacted': 0.7,       # Alto score por contacto
                'clicked': 0.4,         # Score medio por click
                'viewed': 0.2,          # Score bajo por vista
                'ignored': 0.0,         # Sin score si fue ignorado
                'rejected': -0.5        # Score negativo si fue rechazado
            }
            
            base_score = action_scores.get(action, 0.1)
            
            # Ajustar por tiempo de decisión si existe
            time_to_action = outcome.get('time_to_action')
            if time_to_action is not None and isinstance(time_to_action, (int, float)):
                if time_to_action < 60:  # Menos de 1 minuto
                    base_score *= 1.2
                elif time_to_action < 180:  # Menos de 3 minutos
                    base_score *= 1.1
            
            # Ajustar por si agendó cita
            if outcome.get('appointment_scheduled') == True:
                base_score *= 1.3
            
            return min(max(base_score, -1.0), 1.0)
            
        except Exception as e:
            logger.debug(f"Error procesando interacción: {e}")
            return 0.1  # Score por defecto
    
    def _user_based_predictions(
        self, 
        user: User, 
        candidate_clinicians: List[str]
    ) -> Dict[str, float]:
        """
        Predicciones basadas en usuarios similares.
        Versión simplificada y robusta.
        """
        predictions = {}
        
        if not self._user_item_matrix or not user.user_id:
            return {clin_id: 0.5 for clin_id in candidate_clinicians}
        
        # Obtener historial del usuario
        user_scores = self._user_item_matrix.get(user.user_id, {})
        if not user_scores:
            return {clin_id: 0.5 for clin_id in candidate_clinicians}
        
        try:
            # Encontrar usuarios similares (versión simple)
            similar_users = self._find_similar_users_simple(user.user_id, n=10)
            
            if not similar_users:
                return {clin_id: 0.5 for clin_id in candidate_clinicians}
            
            # Para cada clínico candidato
            for clinician_id in candidate_clinicians:
                # Si el usuario ya interactuó con este clínico, skip
                if clinician_id in user_scores:
                    continue
                
                # Calcular predicción basada en usuarios similares
                scores = []
                
                for similar_user_id in similar_users:
                    similar_scores = self._user_item_matrix.get(similar_user_id, {})
                    
                    if clinician_id in similar_scores:
                        scores.append(similar_scores[clinician_id])
                
                if scores:
                    predictions[clinician_id] = sum(scores) / len(scores)
                else:
                    predictions[clinician_id] = 0.5
            
        except Exception as e:
            logger.debug(f"Error en predicciones user-based: {e}")
            return {clin_id: 0.5 for clin_id in candidate_clinicians}
        
        return predictions
    
    def _find_similar_users_simple(
        self, 
        user_id: str, 
        n: int = 10
    ) -> List[str]:
        """
        Encuentra usuarios similares de forma simple.
        """
        if not self._user_item_matrix or user_id not in self._user_item_matrix:
            return []
        
        user_scores = self._user_item_matrix[user_id]
        similar_users = []
        
        try:
            # Comparar con otros usuarios
            for other_user_id, other_scores in self._user_item_matrix.items():
                if other_user_id == user_id:
                    continue
                
                # Contar clínicos en común
                common_clinicians = set(user_scores.keys()) & set(other_scores.keys())
                
                if len(common_clinicians) >= 2:  # Al menos 2 clínicos en común
                    similar_users.append(other_user_id)
                
                if len(similar_users) >= n:
                    break
            
        except Exception as e:
            logger.debug(f"Error buscando usuarios similares: {e}")
        
        return similar_users[:n]
    
    def _calculate_clinician_similarity(self, clin1: Dict, clin2: Dict) -> float:
        """
        Calcula similitud entre dos clínicos de forma simple.
        """
        try:
            similarity_scores = []
            
            # Especialidades
            specs1 = set(clin1.get('profile_features', {}).get('specialties', []))
            specs2 = set(clin2.get('profile_features', {}).get('specialties', []))
            
            if specs1 and specs2:
                jaccard = len(specs1 & specs2) / len(specs1 | specs2)
                similarity_scores.append(jaccard)
            
            # Género
            if (clin1.get('profile_features', {}).get('gender') == 
                clin2.get('profile_features', {}).get('gender')):
                similarity_scores.append(0.7)
            
            return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
            
        except Exception:
            return 0.0