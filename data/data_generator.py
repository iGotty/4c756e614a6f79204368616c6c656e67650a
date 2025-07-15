#!/usr/bin/env python3
"""
Generador de Datos Mock para Sistema de Matcheo LunaJoy
Genera datos sintéticos realistas para pruebas y desarrollo
"""

import json
import random
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict, Any, Tuple
import uuid
from collections import defaultdict

# Intentar importar faker, si no está instalado, usar alternativas
try:
    from faker import Faker
    fake = Faker()
    Faker.seed(42)
    USE_FAKER = True
except ImportError:
    print("⚠️  Faker no está instalado. Usando generación básica de nombres.")
    print("   Para mejores resultados, instala: pip install faker")
    USE_FAKER = False
    fake = None

# Configuración de semillas para reproducibilidad
random.seed(42)
np.random.seed(42)

# =============================================================================
# ENCODER PARA NUMPY
# =============================================================================

class NumpyEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar tipos de NumPy en JSON"""
    def default(self, obj):
        if isinstance(obj, (np.int8, np.int16, np.int32, np.int64,
                          np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif hasattr(obj, 'item'):  # Para otros tipos numpy
            return obj.item()
        return super(NumpyEncoder, self).default(obj)

# =============================================================================
# DATOS BASE Y CONSTANTES
# =============================================================================

# Estados más poblados de USA con distribución realista
STATES_WEIGHTS = {
    'CA': 12.0, 'TX': 9.0, 'FL': 7.0, 'NY': 6.5, 'PA': 4.0,
    'IL': 4.0, 'OH': 3.5, 'GA': 3.5, 'NC': 3.5, 'MI': 3.0,
    'NJ': 3.0, 'VA': 2.8, 'WA': 2.5, 'AZ': 2.5, 'MA': 2.3,
    'TN': 2.3, 'IN': 2.2, 'MO': 2.0, 'MD': 2.0, 'WI': 1.9,
}

LANGUAGES = {
    'English': 78.0, 'Spanish': 13.0, 'Mandarin': 1.1, 'French': 0.7,
    'Portuguese': 0.6, 'Hindi': 0.5, 'Arabic': 0.4, 'Russian': 0.3,
    'Korean': 0.3, 'Vietnamese': 0.3
}

INSURANCE_PROVIDERS = {
    'BlueCross BlueShield': 22.0, 'UnitedHealth': 18.0, 'Aetna': 15.0,
    'Cigna': 12.0, 'Kaiser': 10.0, 'Humana': 8.0, 'Anthem': 6.0,
    'Centene': 4.0, 'Molina': 3.0, 'WellCare': 2.0,
}

# Especialidades agrupadas por correlación
SPECIALTY_GROUPS = {
    'common_mental_health': {
        'specialties': ['anxiety', 'depression', 'stress'],
        'weight': 35.0,
        'co_occurrence': 0.8
    },
    'trauma_related': {
        'specialties': ['trauma', 'ptsd', 'grief'],
        'weight': 20.0,
        'co_occurrence': 0.7
    },
    'behavioral': {
        'specialties': ['adhd', 'ocd', 'bipolar'],
        'weight': 15.0,
        'co_occurrence': 0.5
    },
    'relational': {
        'specialties': ['relationship', 'family', 'parenting'],
        'weight': 15.0,
        'co_occurrence': 0.7
    },
    'addiction': {
        'specialties': ['addiction', 'substance_abuse'],
        'weight': 10.0,
        'co_occurrence': 0.6
    },
    'self_growth': {
        'specialties': ['self_esteem', 'anger', 'life_transitions'],
        'weight': 5.0,
        'co_occurrence': 0.6
    }
}

CERTIFICATIONS = ['LMFT', 'LCSW', 'PhD', 'PsyD', 'LMHC', 'LPC', 'LCPC', 
                 'MD', 'NP', 'LPCC', 'LAC', 'LCADC']

TREATMENT_MODALITIES = ['CBT', 'DBT', 'EMDR', 'Psychodynamic', 'Humanistic', 
                       'ACT', 'Mindfulness', 'Solution-Focused', 'Narrative', 
                       'Gestalt', 'Art Therapy', 'Play Therapy', 
                       'Family Systems', 'IFS']

GENDER_OPTIONS = ['male', 'female', 'non_binary']
GENDER_WEIGHTS = [48.0, 48.0, 4.0]

AGE_GROUPS = ['children', 'teens', 'adults', 'seniors']

SPECIAL_POPULATIONS = ['LGBTQ+', 'veterans', 'first_responders', 
                      'healthcare_workers', 'students', 'new_parents', 
                      'immigrants', 'disabled', 'chronic_illness']

TIME_SLOTS = ['morning', 'afternoon', 'evening', 'weekends']

# Nombres de respaldo si Faker no está disponible
FIRST_NAMES_MALE = ['John', 'Michael', 'David', 'James', 'Robert', 'William', 
                    'Joseph', 'Charles', 'Thomas', 'Daniel']
FIRST_NAMES_FEMALE = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 
                      'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
              'Miller', 'Davis', 'Rodriguez', 'Martinez']

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def weighted_choice(choices, weights=None):
    """Selección ponderada de elementos"""
    if isinstance(choices, dict):
        items = list(choices.keys())
        weights_list = list(choices.values())
    else:
        items = choices
        weights_list = weights if weights is not None else [1] * len(items)
    
    result = np.random.choice(items, p=np.array(weights_list)/np.sum(weights_list))
    
    # Convertir tipos numpy a tipos nativos
    if isinstance(result, (np.int8, np.int16, np.int32, np.int64)):
        return int(result)
    elif isinstance(result, (np.float16, np.float32, np.float64)):
        return float(result)
    elif hasattr(result, 'item'):  # Para otros tipos numpy
        return result.item()
    return result

def generate_embedding(dim, seed=None):
    """Genera un embedding vector normalizado"""
    if seed:
        np.random.seed(seed)
    vec = np.random.randn(dim)
    return (vec / np.linalg.norm(vec)).tolist()

def calculate_availability_score(clinician):
    """Calcula score de disponibilidad basado en carga actual"""
    load_ratio = clinician['availability_features']['current_patient_count'] / \
                 clinician['availability_features']['max_patient_capacity']
    
    immediate = 1.0 if clinician['availability_features']['immediate_availability'] else 0.5
    return round(immediate * (1 - load_ratio), 3)

def generate_correlated_specialties(primary_group=None):
    """Genera especialidades con correlaciones realistas"""
    if not primary_group:
        primary_group = weighted_choice(
            list(SPECIALTY_GROUPS.keys()),
            [g['weight'] for g in SPECIALTY_GROUPS.values()]
        )
    
    specialties = SPECIALTY_GROUPS[primary_group]['specialties'].copy()
    
    # Agregar especialidades correlacionadas
    for group_name, group_data in SPECIALTY_GROUPS.items():
        if group_name != primary_group and random.random() < group_data['co_occurrence'] * 0.3:
            additional = random.sample(
                group_data['specialties'], 
                random.randint(1, min(2, len(group_data['specialties'])))
            )
            specialties.extend(additional)
    
    return list(set(specialties))

# =============================================================================
# GENERADOR DE CLÍNICOS
# =============================================================================

class ClinicianGenerator:
    def __init__(self):
        self.generated_names = set()
        self.name_counter = 0
        
    def _generate_unique_name(self, gender):
        """Genera nombre único usando Faker o alternativa"""
        attempts = 0
        while attempts < 100:
            if USE_FAKER:
                if gender == 'male':
                    first_name = fake.first_name_male()
                elif gender == 'female':
                    first_name = fake.first_name_female()
                else:
                    first_name = fake.first_name()
                last_name = fake.last_name()
            else:
                # Alternativa sin Faker
                if gender == 'male':
                    first_name = random.choice(FIRST_NAMES_MALE)
                elif gender == 'female':
                    first_name = random.choice(FIRST_NAMES_FEMALE)
                else:
                    first_name = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
                last_name = random.choice(LAST_NAMES)
            
            full_name = f"{first_name} {last_name}"
            
            if full_name not in self.generated_names:
                self.generated_names.add(full_name)
                return first_name, last_name
            attempts += 1
        
        # Fallback con número
        self.name_counter += 1
        return f"{first_name}_{self.name_counter}", last_name
    
    def generate_clinician(self, index):
        """Genera un clínico con características realistas"""
        # Género del clínico
        gender = weighted_choice(GENDER_OPTIONS, GENDER_WEIGHTS)
        first_name, last_name = self._generate_unique_name(gender)
        
        # Tipo de clínico
        clinician_type = weighted_choice({
            'therapy_only': 65.0,
            'medication_only': 15.0,
            'both': 20.0
        })
        
        # Configuración según tipo
        if clinician_type == 'therapy_only':
            appointment_types = ['therapy']
            base_certifications = ['LMFT', 'LCSW', 'PhD', 'PsyD', 'LMHC', 'LPC']
            title_prefix = random.choice(['', 'Dr.']) if random.random() < 0.3 else ''
        elif clinician_type == 'medication_only':
            appointment_types = ['medication']
            base_certifications = ['MD', 'NP']
            title_prefix = 'Dr.' if 'MD' in random.sample(base_certifications, 1) else ''
        else:
            appointment_types = ['therapy', 'medication']
            base_certifications = ['MD', 'PhD', 'PsyD']
            title_prefix = 'Dr.'
        
        # ID único
        clinician_id = f"clin_{index:04d}_{uuid.uuid4().hex[:6]}"
        
        # Estados con licencia
        primary_state = weighted_choice(STATES_WEIGHTS)
        licensed_states = [primary_state]
        
        num_additional_states = weighted_choice([0, 1, 2, 3], [40, 35, 20, 5])
        if num_additional_states > 0:
            additional_states = random.sample(
                [s for s in STATES_WEIGHTS.keys() if s != primary_state],
                num_additional_states
            )
            licensed_states.extend(additional_states)
        
        # Experiencia
        years_exp = weighted_choice({
            1: 5.0, 2: 8.0, 3: 10.0, 5: 15.0, 8: 20.0,
            10: 15.0, 15: 12.0, 20: 10.0, 25: 3.0, 30: 2.0
        })
        
        # Especialidades
        primary_focus = weighted_choice(
            list(SPECIALTY_GROUPS.keys()),
            [g['weight'] for g in SPECIALTY_GROUPS.values()]
        )
        specialties = generate_correlated_specialties(primary_focus)
        
        if years_exp > 10:
            for _ in range(random.randint(1, 3)):
                new_specs = generate_correlated_specialties()
                specialties.extend(random.sample(new_specs, 1))
        
        specialties = list(set(specialties))[:8]
        
        # Certificaciones
        num_certs = min(len(base_certifications), 1 + int(years_exp / 5))
        certifications = random.sample(base_certifications, num_certs)
        
        # Modalidades
        num_modalities = min(
            weighted_choice([2, 3, 4, 5, 6], [10, 25, 35, 20, 10]),
            2 + int(years_exp / 4)
        )
        modalities = random.sample(TREATMENT_MODALITIES, num_modalities)
        
        # Disponibilidad y carga
        busy_probability = min(0.2 + (years_exp / 50), 0.7)
        is_busy = random.random() < busy_probability
        
        if 'medication' in appointment_types and 'therapy' not in appointment_types:
            max_capacity = weighted_choice([40, 50, 60, 70], [20, 40, 30, 10])
        else:
            max_capacity = weighted_choice([15, 20, 25, 30, 35], [15, 30, 30, 20, 5])
        
        if is_busy:
            current_patients = int(max_capacity * random.uniform(0.75, 0.95))
            immediate_avail = random.random() < 0.1
            accepting_new = random.random() < 0.3
        else:
            current_patients = int(max_capacity * random.uniform(0.2, 0.6))
            immediate_avail = random.random() < 0.7
            accepting_new = True
        
        # Seguros
        accepts_insurance = random.random() < 0.85
        if accepts_insurance:
            base_insurances = min(3, 1 + int(years_exp / 7))
            num_insurances = random.randint(base_insurances, min(8, base_insurances + 4))
            insurances = random.sample(list(INSURANCE_PROVIDERS.keys()), num_insurances)
        else:
            insurances = []
        
        insurances.append('Private Pay')
        insurances = list(set(insurances))
        
        # Métricas de desempeño
        is_new = years_exp <= 2
        
        if is_new:
            performance_metrics = {
                'total_patients_seen': random.randint(0, 20),
                'avg_patient_rating': None,
                'retention_rate': None,
                'avg_session_count': None,
                'success_by_specialty': {},
                'success_by_demographics': {}
            }
        else:
            base_patients = years_exp * 20
            total_patients = int(base_patients * random.uniform(0.7, 1.3))
            
            base_rating = min(4.0 + (years_exp * 0.03), 4.7)
            avg_rating = round(base_rating + random.uniform(-0.2, 0.3), 2)
            avg_rating = max(3.8, min(5.0, avg_rating))
            
            base_retention = min(0.65 + (years_exp * 0.015), 0.85)
            retention = round(base_retention + random.uniform(-0.1, 0.1), 3)
            retention = max(0.5, min(0.95, retention))
            
            success_by_spec = {}
            for spec in specialties[:4]:
                base_success = 0.7 + (years_exp * 0.01)
                success_by_spec[spec] = round(
                    min(0.95, base_success + random.uniform(-0.1, 0.15)), 3
                )
            
            performance_metrics = {
                'total_patients_seen': total_patients,
                'avg_patient_rating': avg_rating,
                'retention_rate': retention,
                'avg_session_count': round(random.uniform(8, 16), 1),
                'success_by_specialty': success_by_spec,
                'success_by_demographics': {
                    'adults': round(random.uniform(0.7, 0.9), 3),
                    'teens': round(random.uniform(0.6, 0.85), 3),
                    'children': round(random.uniform(0.65, 0.85), 3) if 'children' in random.sample(AGE_GROUPS, 3) else None
                }
            }
        
        # Horarios
        schedule_patterns = {
            'standard': {'morning': True, 'afternoon': True, 'evening': False, 'weekends': False},
            'flexible': {'morning': True, 'afternoon': True, 'evening': True, 'weekends': False},
            'evening_focus': {'morning': False, 'afternoon': True, 'evening': True, 'weekends': False},
            'weekend_available': {'morning': True, 'afternoon': True, 'evening': False, 'weekends': True},
            'full_availability': {'morning': True, 'afternoon': True, 'evening': True, 'weekends': True}
        }
        
        schedule_type = weighted_choice(
            list(schedule_patterns.keys()),
            [40, 30, 15, 10, 5]
        )
        typical_availability = schedule_patterns[schedule_type].copy()
        
        # Siguiente slot disponible
        if immediate_avail:
            hours_until_available = random.randint(1, 4)
        else:
            hours_until_available = weighted_choice(
                [24, 48, 72, 96, 120, 168],
                [20, 25, 20, 15, 10, 10]
            )
        
        next_available = datetime.now() + timedelta(hours=hours_until_available)
        
        # Grupos de edad
        age_groups_served = ['adults']
        if any(spec in ['adhd', 'family', 'parenting'] for spec in specialties):
            age_groups_served.extend(['children', 'teens'])
        elif random.random() < 0.3:
            age_groups_served.append(random.choice(['teens', 'seniors']))
        
        # Poblaciones especiales
        special_pops = []
        if 'trauma' in specialties and random.random() < 0.5:
            special_pops.extend(['veterans', 'first_responders'])
        if random.random() < 0.3:
            special_pops.append('LGBTQ+')
        if random.random() < 0.2:
            special_pops.extend(random.sample(SPECIAL_POPULATIONS, random.randint(1, 2)))
        special_pops = list(set(special_pops))[:4]
        
        # Idiomas
        languages_spoken = ['English']
        if primary_state in ['CA', 'TX', 'FL', 'NY'] and random.random() < 0.3:
            languages_spoken.append('Spanish')
        if random.random() < 0.1:
            additional_lang = weighted_choice(LANGUAGES)
            if additional_lang not in languages_spoken:
                languages_spoken.append(additional_lang)
        
        # Tarifas
        base_rate = 120 if primary_state in ['CA', 'NY', 'MA', 'WA'] else 100
        therapy_rate = base_rate + (years_exp * 3) + random.randint(-20, 40)
        medication_rate = therapy_rate + random.randint(30, 70)
        
        # Cluster
        cluster_id = hash(f"{primary_focus}_{schedule_type}_{clinician_type}") % 15
        
        # Fecha de creación
        if USE_FAKER:
            created_at = fake.date_time_between(start_date='-3y', end_date='now')
        else:
            days_ago = random.randint(30, 1095)
            created_at = datetime.now() - timedelta(days=days_ago)
        
        # Construir objeto
        clinician = {
            'clinician_id': clinician_id,
            'basic_info': {
                'full_name': f"{title_prefix} {first_name} {last_name}".strip(),
                'license_states': licensed_states,
                'license_numbers': {
                    state: f"{state}-{random.randint(100000, 999999)}" 
                    for state in licensed_states
                },
                'appointment_types': appointment_types
            },
            'profile_features': {
                'gender': gender,
                'languages': languages_spoken,
                'years_experience': int(years_exp),
                'specialties': specialties,
                'certifications': certifications,
                'treatment_modalities': modalities,
                'age_groups_served': age_groups_served,
                'special_populations': special_pops
            },
            'availability_features': {
                'immediate_availability': immediate_avail,
                'next_available_slot': next_available.isoformat(),
                'typical_availability': typical_availability,
                'current_patient_count': current_patients,
                'max_patient_capacity': max_capacity,
                'accepting_new_patients': accepting_new
            },
            'performance_metrics': performance_metrics,
            'embedding_features': {
                'specialty_vector': generate_embedding(50, seed=index),
                'style_vector': generate_embedding(30, seed=index+1000),
                'clinician_cluster_id': int(cluster_id),
                'practice_style_category': weighted_choice({
                    'directive': 15.0,
                    'collaborative': 40.0,
                    'supportive': 30.0,
                    'eclectic': 15.0
                })
            },
            'admin_data': {
                'insurances_accepted': insurances,
                'rates': {
                    'individual_therapy': therapy_rate if 'therapy' in appointment_types else None,
                    'medication_management': medication_rate if 'medication' in appointment_types else None
                },
                'created_at': created_at.isoformat(),
                'last_updated': datetime.now().isoformat(),
                'active_status': True
            }
        }
        
        # Calcular score de disponibilidad
        clinician['availability_features']['availability_score'] = \
            calculate_availability_score(clinician)
        
        return clinician

# =============================================================================
# GENERADOR DE USUARIOS
# =============================================================================

class UserGenerator:
    def __init__(self, clinicians):
        self.clinicians = clinicians
        self.user_personas = self._define_personas()
        self.state_distribution = self._calculate_state_distribution()
        
    def _calculate_state_distribution(self):
        """Calcula distribución de estados basada en clínicos disponibles"""
        state_counts = defaultdict(int)
        for clinician in self.clinicians:
            for state in clinician['basic_info']['license_states']:
                state_counts[state] += 1
        
        total = sum(state_counts.values())
        return {state: count/total for state, count in state_counts.items()}
        
    def _define_personas(self):
        """Define arquetipos de usuarios"""
        return {
            'stressed_professional': {
                'weight': 25.0,
                'age_range': ['25-34', '35-44'],
                'clinical_needs_groups': ['common_mental_health'],
                'urgency': [0.7, 0.3],
                'therapy_experience': ['first_time', 'returning'],
                'goals': ['manage_symptoms', 'find_balance', 'cope_with_change'],
                'insurance_likelihood': 0.9,
                'gender_preference_likelihood': 0.3
            },
            'relationship_seeker': {
                'weight': 20.0,
                'age_range': ['25-34', '35-44', '45-54'],
                'clinical_needs_groups': ['relational'],
                'urgency': [0.3, 0.7],
                'therapy_experience': ['returning', 'experienced'],
                'goals': ['improve_relationships', 'personal_growth'],
                'insurance_likelihood': 0.85,
                'gender_preference_likelihood': 0.4
            },
            'trauma_survivor': {
                'weight': 15.0,
                'age_range': ['18-24', '25-34', '35-44'],
                'clinical_needs_groups': ['trauma_related', 'common_mental_health'],
                'urgency': [0.5, 0.5],
                'therapy_experience': ['returning', 'experienced'],
                'goals': ['process_trauma', 'develop_skills', 'build_confidence'],
                'insurance_likelihood': 0.8,
                'gender_preference_likelihood': 0.6
            },
            'young_adult': {
                'weight': 20.0,
                'age_range': ['18-24', '25-34'],
                'clinical_needs_groups': ['common_mental_health', 'behavioral'],
                'urgency': [0.6, 0.4],
                'therapy_experience': ['first_time', 'returning'],
                'goals': ['explore_identity', 'manage_symptoms', 'personal_growth'],
                'insurance_likelihood': 0.7,
                'gender_preference_likelihood': 0.35
            },
            'parent_support': {
                'weight': 10.0,
                'age_range': ['25-34', '35-44', '45-54'],
                'clinical_needs_groups': ['relational', 'common_mental_health'],
                'urgency': [0.4, 0.6],
                'therapy_experience': ['first_time', 'returning'],
                'goals': ['improve_relationships', 'develop_skills', 'find_balance'],
                'insurance_likelihood': 0.9,
                'gender_preference_likelihood': 0.25
            },
            'senior_wellness': {
                'weight': 10.0,
                'age_range': ['55-64', '65+'],
                'clinical_needs_groups': ['common_mental_health', 'self_growth'],
                'urgency': [0.3, 0.7],
                'therapy_experience': ['first_time', 'returning'],
                'goals': ['cope_with_change', 'manage_symptoms', 'find_purpose'],
                'insurance_likelihood': 0.95,
                'gender_preference_likelihood': 0.3
            }
        }
    
    def generate_user(self, index, user_type='registered'):
        """Genera un usuario con características realistas"""
        user_id = f"user_{index:05d}_{uuid.uuid4().hex[:6]}"
        
        # Seleccionar persona
        persona_name = weighted_choice(
            list(self.user_personas.keys()),
            [p['weight'] for p in self.user_personas.values()]
        )
        persona = self.user_personas[persona_name]
        
        # Estado
        if self.state_distribution:
            state = weighted_choice(
                list(self.state_distribution.keys()),
                list(self.state_distribution.values())
            )
        else:
            state = weighted_choice(STATES_WEIGHTS)
        
        # Seguro
        has_insurance = random.random() < persona['insurance_likelihood']
        if has_insurance:
            insurance = weighted_choice(INSURANCE_PROVIDERS)
        else:
            insurance = 'Private Pay'
        
        # Necesidades clínicas
        all_needs = []
        for group_name in persona['clinical_needs_groups']:
            group_needs = SPECIALTY_GROUPS[group_name]['specialties']
            num_needs = weighted_choice([1, 2, 3], [50, 35, 15])
            selected_needs = random.sample(group_needs, min(num_needs, len(group_needs)))
            all_needs.extend(selected_needs)
        
        clinical_needs = list(set(all_needs))[:4]
        
        # Tipo de cita
        if any(need in ['bipolar', 'adhd'] for need in clinical_needs):
            appointment_type = weighted_choice(['therapy', 'medication'], [60, 40])
        else:
            appointment_type = weighted_choice(['therapy', 'medication'], [85, 15])
        
        # Preferencias
        has_gender_pref = random.random() < persona['gender_preference_likelihood']
        if has_gender_pref:
            user_gender = weighted_choice(GENDER_OPTIONS, GENDER_WEIGHTS)
            if user_gender == 'female':
                gender_pref = weighted_choice(['female', 'male', None], [60, 20, 20])
            elif user_gender == 'male':
                gender_pref = weighted_choice(['male', 'female', None], [40, 30, 30])
            else:
                gender_pref = weighted_choice(['non_binary', None], [70, 30])
        else:
            gender_pref = None
        
        # Idioma
        primary_language = weighted_choice(LANGUAGES)
        
        # Urgencia
        urgency = weighted_choice(['immediate', 'flexible'], persona['urgency'])
        
        # Horarios preferidos
        if '18-24' in persona['age_range'] or '25-34' in persona['age_range']:
            time_preferences = {
                'evening': 0.4, 'afternoon': 0.3,
                'weekends': 0.2, 'morning': 0.1
            }
        else:
            time_preferences = {
                'morning': 0.3, 'afternoon': 0.35,
                'evening': 0.25, 'weekends': 0.1
            }
        
        num_time_prefs = weighted_choice([1, 2, 3], [40, 45, 15])
        time_prefs = []
        for _ in range(num_time_prefs):
            pref = weighted_choice(time_preferences)
            if pref not in time_prefs:
                time_prefs.append(pref)
        
        # Preferencias declaradas
        stated_preferences = {
            'state': state,
            'insurance_provider': insurance,
            'appointment_type': appointment_type,
            'language': primary_language,
            'gender_preference': gender_pref,
            'clinical_needs': clinical_needs,
            'preferred_time_slots': time_prefs,
            'urgency_level': urgency
        }
        
        user = {
            'user_id': user_id,
            'registration_type': user_type,
            'stated_preferences': stated_preferences
        }
        
        # Datos adicionales para usuarios registrados
        if user_type in ['basic', 'complete']:
            age_range = random.choice(persona['age_range'])
            
            # Email
            if USE_FAKER:
                email = fake.email()
                city = fake.city()
                zip_code = fake.zipcode()
            else:
                email = f"user{index}@email.com"
                city = f"City{random.randint(1, 100)}"
                zip_code = f"{random.randint(10000, 99999)}"
            
            metro_area = weighted_choice({
                'urban': 45.0, 'suburban': 40.0, 'rural': 15.0
            })
            
            user['profile_data'] = {
                'age_range': age_range,
                'gender': weighted_choice(GENDER_OPTIONS, GENDER_WEIGHTS),
                'email': email,
                'location_details': {
                    'state': state,
                    'city': city,
                    'zip_code': zip_code,
                    'metro_area': metro_area
                },
                'therapy_experience': random.choice(persona['therapy_experience']),
                'previous_diagnoses': random.sample(
                    clinical_needs, 
                    random.randint(0, min(2, len(clinical_needs)))
                ),
                'medication_history': appointment_type == 'medication' or random.random() < 0.3,
                'communication_style': weighted_choice({
                    'formal': 25.0, 'casual': 35.0, 'adaptive': 40.0
                }),
                'therapy_goals': random.sample(
                    persona['goals'], 
                    random.randint(1, min(2, len(persona['goals'])))
                ),
                'barriers_to_treatment': random.sample(
                    ['cost', 'time', 'stigma', 'access', 'trust', 'schedule'],
                    weighted_choice([0, 1, 2], [30, 50, 20])
                )
            }
            
            # Señales comportamentales
            user['behavioral_signals'] = {
                'form_completion_time': int(np.random.lognormal(6, 0.5)),
                'fields_reconsidered': random.sample(
                    ['clinical_needs', 'gender_preference', 'insurance', 'appointment_type'],
                    weighted_choice([0, 1, 2], [40, 45, 15])
                ),
                'search_refinements': weighted_choice([0, 1, 2, 3, 4], [30, 35, 20, 10, 5]),
                'login_frequency': round(random.betavariate(2, 5), 2),
                'feature_usage': {
                    'search': weighted_choice([0, 1, 3, 5, 10], [20, 30, 25, 15, 10]),
                    'messaging': weighted_choice([0, 1, 2, 3, 5], [35, 30, 20, 10, 5]),
                    'scheduling': weighted_choice([0, 1, 2, 3], [40, 35, 20, 5])
                },
                'engagement_score': round(random.betavariate(3, 2), 2)
            }
            
            # Embeddings
            user['user_embeddings'] = {
                'needs_vector': generate_embedding(30, seed=index),
                'preference_vector': generate_embedding(20, seed=index+5000),
                'behavior_vector': generate_embedding(25, seed=index+10000),
                'user_cluster_id': hash(persona_name) % 12
            }
        
        # Historia de interacciones
        if user_type == 'complete' and random.random() < 0.6:
            user['interaction_history'] = self._generate_interaction_history(user, persona)
        else:
            user['interaction_history'] = {
                'clinicians_viewed': [],
                'clinicians_contacted': [],
                'clinicians_booked': [],
                'clinicians_retained': []
            }
        
        return user
    
    def _generate_interaction_history(self, user, persona):
        """Genera historial de interacciones"""
        state = user['stated_preferences']['state']
        insurance = user['stated_preferences']['insurance_provider']
        appointment_type = user['stated_preferences']['appointment_type']
        
        available_clinicians = []
        for c in self.clinicians:
            if state not in c['basic_info']['license_states']:
                continue
            if appointment_type not in c['basic_info']['appointment_types']:
                continue
            if insurance != 'Private Pay' and insurance not in c['admin_data']['insurances_accepted']:
                if random.random() > 0.2:
                    continue
            available_clinicians.append(c)
        
        if not available_clinicians:
            return {
                'clinicians_viewed': [],
                'clinicians_contacted': [],
                'clinicians_booked': [],
                'clinicians_retained': []
            }
        
        # Número de clínicos vistos
        if user['stated_preferences']['urgency_level'] == 'immediate':
            num_viewed = weighted_choice([2, 3, 5, 8], [40, 35, 20, 5])
        else:
            num_viewed = weighted_choice([3, 5, 8, 12, 15], [20, 30, 25, 15, 10])
        
        num_viewed = min(num_viewed, len(available_clinicians))
        
        # Simular búsqueda
        viewed_clinicians = self._simulate_search_behavior(
            available_clinicians, user, num_viewed
        )
        
        viewed = []
        base_time = datetime.now() - timedelta(days=random.randint(7, 60))
        
        for i, clinician in enumerate(viewed_clinicians):
            view_time = base_time + timedelta(hours=i * random.randint(1, 24))
            duration = random.randint(30, 300) if i < 3 else random.randint(10, 120)
            
            viewed.append({
                'clinician_id': clinician['clinician_id'],
                'timestamp': view_time.isoformat(),
                'duration': duration
            })
        
        # Contactados
        base_contact_rate = 0.4 if user['stated_preferences']['urgency_level'] == 'immediate' else 0.25
        if persona['therapy_experience'][0] == 'first_time':
            contact_rate = base_contact_rate * 0.7
        else:
            contact_rate = base_contact_rate * 1.2
        
        num_contacted = max(1, int(len(viewed) * contact_rate))
        contact_weights = [1.0 / (i + 1) for i in range(len(viewed))]
        contacted_indices = np.random.choice(
            range(len(viewed)), 
            size=num_contacted, 
            replace=False,
            p=contact_weights/np.sum(contact_weights)
        )
        contacted_ids = [viewed[int(i)]['clinician_id'] for i in contacted_indices]
        
        # Agendados
        book_rate = weighted_choice([0.3, 0.5, 0.7, 0.9], [20, 40, 30, 10])
        num_booked = max(1, int(len(contacted_ids) * book_rate))
        booked_ids = random.sample(contacted_ids, num_booked)
        
        # Retenidos
        retained_ids = []
        for booked_id in booked_ids:
            clinician = next(c for c in available_clinicians if c['clinician_id'] == booked_id)
            
            retention_prob = 0.6
            needs_match = len(set(user['stated_preferences']['clinical_needs']) & 
                            set(clinician['profile_features']['specialties']))
            if needs_match > 0:
                retention_prob += 0.1 * needs_match
            
            if clinician['performance_metrics']['retention_rate']:
                retention_prob *= clinician['performance_metrics']['retention_rate']
            
            if random.random() < min(0.95, retention_prob):
                retained_ids.append(booked_id)
        
        return {
            'clinicians_viewed': viewed,
            'clinicians_contacted': contacted_ids,
            'clinicians_booked': booked_ids,
            'clinicians_retained': retained_ids
        }
    
    def _simulate_search_behavior(self, clinicians, user, num_to_view):
        """Simula comportamiento de búsqueda"""
        scored_clinicians = []
        
        for clinician in clinicians:
            score = 0
            
            if user['stated_preferences']['urgency_level'] == 'immediate':
                if clinician['availability_features']['immediate_availability']:
                    score += 0.4
            
            needs_match = len(set(user['stated_preferences']['clinical_needs']) & 
                            set(clinician['profile_features']['specialties']))
            if user['stated_preferences']['clinical_needs']:
                score += 0.3 * (needs_match / len(user['stated_preferences']['clinical_needs']))
            
            if user['stated_preferences']['gender_preference']:
                if clinician['profile_features']['gender'] == user['stated_preferences']['gender_preference']:
                    score += 0.2
            
            if clinician['performance_metrics']['avg_patient_rating']:
                score += 0.1 * (clinician['performance_metrics']['avg_patient_rating'] / 5.0)
            
            scored_clinicians.append((clinician, score))
        
        scored_clinicians.sort(key=lambda x: x[1], reverse=True)
        
        selected = []
        for i in range(min(num_to_view, len(scored_clinicians))):
            if random.random() < 0.7 or i < 2:
                selected.append(scored_clinicians[i][0])
            else:
                random_idx = random.randint(i, min(i + 5, len(scored_clinicians) - 1))
                selected.append(scored_clinicians[random_idx][0])
        
        return selected

# =============================================================================
# GENERADOR DE INTERACCIONES
# =============================================================================

class InteractionGenerator:
    def __init__(self, users, clinicians):
        self.users = users
        self.clinicians = clinicians
        self.clinician_index = self._build_clinician_index()
        
    def _build_clinician_index(self):
        """Construye índices para búsqueda rápida"""
        index = {
            'by_state': defaultdict(list),
            'by_state_insurance': defaultdict(list),
            'by_state_type': defaultdict(list)
        }
        
        for clinician in self.clinicians:
            for state in clinician['basic_info']['license_states']:
                index['by_state'][state].append(clinician)
                
                for insurance in clinician['admin_data']['insurances_accepted']:
                    key = f"{state}_{insurance}"
                    index['by_state_insurance'][key].append(clinician)
                
                for appt_type in clinician['basic_info']['appointment_types']:
                    key = f"{state}_{appt_type}"
                    index['by_state_type'][key].append(clinician)
        
        return index
    
    def generate_interactions(self, num_interactions):
        """Genera interacciones realistas"""
        interactions = []
        
        time_weights = {
            'morning': 0.15,
            'afternoon': 0.35,
            'evening': 0.40,
            'night': 0.10
        }
        
        for i in range(num_interactions):
            # Seleccionar usuario
            user_weights = []
            for u in self.users:
                if u['registration_type'] == 'anonymous':
                    user_weights.append(1.0)
                elif u['registration_type'] == 'basic':
                    user_weights.append(2.0)
                else:
                    user_weights.append(3.0)
            
            user = self.users[weighted_choice(range(len(self.users)), user_weights)]
            
            # Encontrar clínicos
            state = user['stated_preferences']['state']
            insurance = user['stated_preferences']['insurance_provider']
            appt_type = user['stated_preferences']['appointment_type']
            
            if insurance != 'Private Pay':
                key = f"{state}_{insurance}"
                candidates = self.clinician_index['by_state_insurance'].get(key, [])
            else:
                candidates = self.clinician_index['by_state'].get(state, [])
            
            available_clinicians = [
                c for c in candidates 
                if appt_type in c['basic_info']['appointment_types']
            ]
            
            if not available_clinicians:
                available_clinicians = [
                    c for c in self.clinician_index['by_state'].get(state, [])
                    if appt_type in c['basic_info']['appointment_types']
                ]
            
            if not available_clinicians:
                continue
            
            # Matching
            matched_clinicians = self._simulate_matching(user, available_clinicians)
            
            if not matched_clinicians:
                continue
            
            # Timestamp
            time_period = weighted_choice(list(time_weights.keys()), list(time_weights.values()))
            hour_ranges = {
                'morning': (6, 12),
                'afternoon': (12, 18),
                'evening': (18, 22),
                'night': (22, 6)
            }
            
            hour_range = hour_ranges[time_period]
            if hour_range[1] < hour_range[0]:
                hour = random.randint(hour_range[0], 24) % 24
            else:
                hour = random.randint(hour_range[0], hour_range[1] - 1)
            
            base_time = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            base_time = base_time.replace(hour=hour)
            
            # Generar interacciones
            session_id = f"session_{i:06d}_{uuid.uuid4().hex[:4]}"
            num_to_show = weighted_choice([3, 5, 8, 10], [25, 40, 25, 10])
            
            for rank, (clinician, score, components) in enumerate(matched_clinicians[:num_to_show]):
                interaction = self._create_interaction(
                    user, clinician, score, components, rank + 1, 
                    len(matched_clinicians), session_id, base_time
                )
                interactions.append(interaction)
                base_time += timedelta(seconds=random.randint(2, 10))
        
        return interactions
    
    def _simulate_matching(self, user, clinicians):
        """Simula el algoritmo de matching"""
        scored_clinicians = []
        
        for clinician in clinicians:
            components = self._calculate_match_components(user, clinician)
            
            if user['stated_preferences']['urgency_level'] == 'immediate':
                weights = {
                    'availability_match': 0.40,
                    'insurance_match': 0.20,
                    'specialty_match': 0.20,
                    'load_balance': 0.10,
                    'preference_match': 0.10
                }
            else:
                weights = {
                    'availability_match': 0.25,
                    'insurance_match': 0.25,
                    'specialty_match': 0.25,
                    'load_balance': 0.15,
                    'preference_match': 0.10
                }
            
            total_score = sum(components[key] * weights[key] for key in weights)
            
            # Boost para clínicos nuevos
            created_date = datetime.fromisoformat(clinician['admin_data']['created_at'])
            days_since_creation = (datetime.now() - created_date).days
            if days_since_creation <= 30:
                total_score *= 1.1
            
            scored_clinicians.append((clinician, total_score, components))
        
        scored_clinicians.sort(key=lambda x: x[1], reverse=True)
        
        if len(scored_clinicians) > 10:
            diversified = self._diversify_results(scored_clinicians[:10])
            return diversified + scored_clinicians[10:]
        
        return scored_clinicians
    
    def _diversify_results(self, top_clinicians):
        """Diversifica resultados"""
        if len(top_clinicians) <= 3:
            return top_clinicians
        
        diversified = [top_clinicians[0]]
        
        seen_genders = set()
        seen_specialties = set()
        seen_availability = set()
        
        first_clinician = top_clinicians[0][0]
        seen_genders.add(first_clinician['profile_features']['gender'])
        seen_specialties.update(first_clinician['profile_features']['specialties'][:2])
        seen_availability.add(first_clinician['availability_features']['immediate_availability'])
        
        remaining = top_clinicians[1:]
        
        while len(diversified) < len(top_clinicians) and remaining:
            best_diversity_score = -1
            best_candidate = None
            best_index = -1
            
            for i, (clinician, score, components) in enumerate(remaining):
                diversity_score = 0
                
                if clinician['profile_features']['gender'] not in seen_genders:
                    diversity_score += 0.3
                
                new_specialties = set(clinician['profile_features']['specialties']) - seen_specialties
                diversity_score += 0.4 * (len(new_specialties) / len(clinician['profile_features']['specialties']))
                
                if clinician['availability_features']['immediate_availability'] not in seen_availability:
                    diversity_score += 0.3
                
                rank_penalty = (i + 1) * 0.05
                final_diversity_score = diversity_score - rank_penalty
                
                if final_diversity_score > best_diversity_score:
                    best_diversity_score = final_diversity_score
                    best_candidate = (clinician, score, components)
                    best_index = i
            
            if best_candidate:
                diversified.append(best_candidate)
                remaining.pop(best_index)
                
                clinician = best_candidate[0]
                seen_genders.add(clinician['profile_features']['gender'])
                seen_specialties.update(clinician['profile_features']['specialties'][:2])
                seen_availability.add(clinician['availability_features']['immediate_availability'])
            else:
                diversified.extend(remaining)
                break
        
        return diversified
    
    def _calculate_match_components(self, user, clinician):
        """Calcula componentes del match"""
        prefs = user['stated_preferences']
        
        # Insurance
        if prefs['insurance_provider'] == 'Private Pay':
            insurance_match = 1.0
        elif prefs['insurance_provider'] in clinician['admin_data']['insurances_accepted']:
            insurance_match = 1.0
        elif 'Private Pay' in clinician['admin_data']['insurances_accepted']:
            insurance_match = 0.5
        else:
            insurance_match = 0.0
        
        # Specialty
        if prefs['clinical_needs']:
            direct_matches = set(prefs['clinical_needs']) & set(clinician['profile_features']['specialties'])
            
            related_matches = 0
            specialty_groups_rev = {}
            for group, data in SPECIALTY_GROUPS.items():
                for spec in data['specialties']:
                    specialty_groups_rev[spec] = group
            
            for need in prefs['clinical_needs']:
                if need not in direct_matches and need in specialty_groups_rev:
                    need_group = specialty_groups_rev[need]
                    for clinician_spec in clinician['profile_features']['specialties']:
                        if clinician_spec in specialty_groups_rev:
                            if specialty_groups_rev[clinician_spec] == need_group:
                                related_matches += 0.5
                                break
            
            total_matches = len(direct_matches) + (related_matches * 0.5)
            specialty_match = min(1.0, total_matches / len(prefs['clinical_needs']))
        else:
            specialty_match = 0.5
        
        # Availability
        if prefs['urgency_level'] == 'immediate':
            if clinician['availability_features']['immediate_availability']:
                availability_match = 1.0
            else:
                next_slot = datetime.fromisoformat(clinician['availability_features']['next_available_slot'])
                hours_until = (next_slot - datetime.now()).total_seconds() / 3600
                
                if hours_until <= 24:
                    availability_match = 0.8
                elif hours_until <= 48:
                    availability_match = 0.6
                elif hours_until <= 72:
                    availability_match = 0.4
                else:
                    availability_match = 0.2
        else:
            availability_match = clinician['availability_features']['availability_score']
        
        # Time slots
        if prefs['preferred_time_slots']:
            time_matches = 0
            time_weights = {
                'morning': 1.0, 'afternoon': 1.0,
                'evening': 1.2, 'weekends': 1.5
            }
            
            for slot in prefs['preferred_time_slots']:
                if clinician['availability_features']['typical_availability'].get(slot, False):
                    time_matches += time_weights.get(slot, 1.0)
            
            max_possible = sum(time_weights.get(slot, 1.0) for slot in prefs['preferred_time_slots'])
            time_match = time_matches / max_possible
        else:
            time_match = 1.0
        
        # Load balance
        load_ratio = clinician['availability_features']['current_patient_count'] / \
                    clinician['availability_features']['max_patient_capacity']
        
        if load_ratio < 0.3:
            load_balance = 0.7
        elif load_ratio < 0.7:
            load_balance = 1.0
        elif load_ratio < 0.85:
            load_balance = 0.8
        else:
            load_balance = 0.5
        
        # Gender preference
        if prefs['gender_preference']:
            if prefs['gender_preference'] == clinician['profile_features']['gender']:
                gender_match = 1.0
            else:
                gender_match = 0.0
        else:
            gender_match = 1.0
        
        # Language
        if prefs['language'] in clinician['profile_features']['languages']:
            language_match = 1.0
        elif 'English' in clinician['profile_features']['languages']:
            language_match = 0.7
        else:
            language_match = 0.0
        
        preference_match = (time_match * 0.4 + gender_match * 0.3 + language_match * 0.3)
        
        return {
            'insurance_match': round(insurance_match, 3),
            'specialty_match': round(specialty_match, 3),
            'availability_match': round(availability_match, 3),
            'load_balance': round(load_balance, 3),
            'preference_match': round(preference_match, 3)
        }
    
    def _create_interaction(self, user, clinician, score, components, rank, total_shown, session_id, timestamp):
        """Crea registro de interacción"""
        interaction_id = f"int_{uuid.uuid4().hex[:12]}"
        
        action_probs = self._calculate_action_probability(
            user, clinician, score, components, rank
        )
        
        action = weighted_choice(
            ['viewed', 'clicked', 'contacted', 'booked', 'ignored'],
            action_probs
        )
        
        # Tiempo hasta acción
        if action == 'ignored':
            time_to_action = None
        elif action == 'viewed':
            time_to_action = random.randint(1, 5)
        elif action == 'clicked':
            time_to_action = random.randint(3, 30)
        elif action == 'contacted':
            if user['stated_preferences']['urgency_level'] == 'immediate':
                time_to_action = random.randint(60, 600)
            else:
                time_to_action = random.randint(300, 3600)
        else:  # booked
            time_to_action = random.randint(600, 7200)
        
        # Outcomes
        if action == 'booked':
            appointment_scheduled = True
            completion_prob = 0.85
            
            if user['stated_preferences']['urgency_level'] == 'immediate':
                completion_prob += 0.05
            if score > 0.8:
                completion_prob += 0.05
            
            appointment_completed = random.random() < min(0.95, completion_prob)
            
            if appointment_completed:
                short_term = weighted_choice(
                    ['completed', 'no_show'],
                    [completion_prob * 100, (1 - completion_prob) * 100]
                )
                
                if components['specialty_match'] > 0.7 and components['preference_match'] > 0.7:
                    long_term_weights = [70, 20, 10]
                elif components['specialty_match'] > 0.5:
                    long_term_weights = [50, 30, 20]
                else:
                    long_term_weights = [30, 40, 30]
                
                long_term = weighted_choice(
                    ['retained', 'switched', 'dropped'],
                    long_term_weights
                )
            else:
                short_term = 'cancelled'
                long_term = None
        else:
            appointment_scheduled = False
            appointment_completed = False
            short_term = None
            long_term = None
        
        # Wait time
        if clinician['availability_features']['immediate_availability']:
            wait_days = 0
        else:
            next_slot = datetime.fromisoformat(clinician['availability_features']['next_available_slot'])
            wait_days = max(0, (next_slot - datetime.now()).days)
        
        user_flexibility = self._calculate_user_flexibility(user)
        
        interaction = {
            'interaction_id': interaction_id,
            'user_id': user['user_id'],
            'clinician_id': clinician['clinician_id'],
            'session_id': session_id,
            'match_context': {
                'timestamp': timestamp.isoformat(),
                'match_score': round(score, 3),
                'score_components': {k: round(v, 3) for k, v in components.items()},
                'ranking_position': rank,
                'total_results_shown': total_shown,
                'user_state': user['registration_type']
            },
            'snapshot_features': {
                'user_urgency': user['stated_preferences']['urgency_level'],
                'user_flexibility': round(user_flexibility, 2),
                'stated_needs': user['stated_preferences']['clinical_needs'],
                'clinician_availability': clinician['availability_features']['availability_score'],
                'clinician_load': round(
                    clinician['availability_features']['current_patient_count'] / 
                    clinician['availability_features']['max_patient_capacity'], 2
                ),
                'wait_time_days': wait_days,
                'specialty_overlap': components['specialty_match'],
                'insurance_match': bool(components['insurance_match'] == 1.0),
                'preference_alignment': components['preference_match']
            },
            'outcome': {
                'action': action,
                'action_timestamp': (timestamp + 
                    timedelta(seconds=time_to_action if time_to_action else 0)).isoformat(),
                'time_to_action': time_to_action,
                'appointment_scheduled': appointment_scheduled,
                'appointment_completed': appointment_completed,
                'short_term_outcome': short_term,
                'long_term_outcome': long_term
            },
            'experiment_data': {
                'algorithm_version': 'v1.0',
                'experiment_groups': ['baseline'],
                'model_confidence': round(min(0.95, score + random.uniform(-0.05, 0.05)), 3)
            }
        }
        
        return interaction
    
    def _calculate_user_flexibility(self, user):
        """Calcula flexibilidad del usuario"""
        flexibility = 0.5
        
        if user['stated_preferences']['urgency_level'] == 'flexible':
            flexibility += 0.2
        else:
            flexibility -= 0.1
        
        if user['stated_preferences']['gender_preference']:
            flexibility -= 0.1
        
        if len(user['stated_preferences']['preferred_time_slots']) == 1:
            flexibility -= 0.1
        elif len(user['stated_preferences']['preferred_time_slots']) >= 3:
            flexibility += 0.1
        
        if user['registration_type'] == 'complete':
            flexibility += 0.1
        
        return max(0.0, min(1.0, flexibility + random.uniform(-0.1, 0.1)))
    
    def _calculate_action_probability(self, user, clinician, score, components, rank):
        """Calcula probabilidades de acción"""
        if rank == 1:
            base_probs = {'viewed': 15, 'clicked': 35, 'contacted': 30, 'booked': 15, 'ignored': 5}
        elif rank == 2:
            base_probs = {'viewed': 20, 'clicked': 35, 'contacted': 25, 'booked': 12, 'ignored': 8}
        elif rank <= 5:
            base_probs = {'viewed': 30, 'clicked': 30, 'contacted': 20, 'booked': 8, 'ignored': 12}
        else:
            base_probs = {'viewed': 40, 'clicked': 25, 'contacted': 15, 'booked': 5, 'ignored': 15}
        
        # Ajustes por score
        if score >= 0.85:
            base_probs['booked'] *= 2.0
            base_probs['contacted'] *= 1.5
            base_probs['ignored'] *= 0.3
        elif score >= 0.7:
            base_probs['booked'] *= 1.5
            base_probs['contacted'] *= 1.3
            base_probs['ignored'] *= 0.5
        elif score < 0.5:
            base_probs['booked'] *= 0.5
            base_probs['contacted'] *= 0.7
            base_probs['ignored'] *= 2.0
        
        # Ajustes por urgencia
        if user['stated_preferences']['urgency_level'] == 'immediate':
            base_probs['booked'] *= 1.4
            base_probs['contacted'] *= 1.3
            base_probs['viewed'] *= 0.7
        
        # Ajustes por tipo de usuario
        if user['registration_type'] == 'anonymous':
            base_probs['booked'] = 0
            base_probs['contacted'] *= 0.5
            base_probs['clicked'] *= 1.5
        elif user['registration_type'] == 'basic':
            base_probs['booked'] *= 0.8
        
        # Ajustes por componentes
        if components['insurance_match'] == 0:
            base_probs['booked'] *= 0.3
            base_probs['contacted'] *= 0.5
        
        if components['specialty_match'] < 0.3:
            base_probs['booked'] *= 0.4
            base_probs['contacted'] *= 0.6
        
        if components['availability_match'] == 1.0:
            base_probs['booked'] *= 1.3
            base_probs['contacted'] *= 1.2
        
        if user['stated_preferences']['gender_preference'] and components['preference_match'] < 0.5:
            base_probs['booked'] *= 0.2
            base_probs['contacted'] *= 0.4
            base_probs['ignored'] *= 2.0
        
        # Normalizar
        actions = list(base_probs.keys())
        probs = np.array(list(base_probs.values()))
        probs = probs / np.sum(probs)
        
        return probs

# =============================================================================
# GENERADOR DE SESIONES
# =============================================================================

class SessionGenerator:
    def __init__(self, interactions):
        self.booked_interactions = [i for i in interactions 
                                   if i['outcome']['appointment_scheduled']]
        self.interaction_lookup = {i['interaction_id']: i for i in interactions}
        
    def generate_sessions(self):
        """Genera sesiones basadas en interacciones"""
        sessions = []
        
        # Agrupar por usuario-clínico
        user_clinician_pairs = defaultdict(list)
        for interaction in self.booked_interactions:
            if interaction['outcome']['appointment_completed']:
                key = (interaction['user_id'], interaction['clinician_id'])
                user_clinician_pairs[key].append(interaction)
        
        # Generar sesiones
        for (user_id, clinician_id), interactions in user_clinician_pairs.items():
            interactions.sort(key=lambda x: x['match_context']['timestamp'])
            primary_interaction = interactions[0]
            
            outcome = primary_interaction['outcome']['long_term_outcome']
            
            if outcome == 'retained':
                num_sessions = weighted_choice(
                    [6, 8, 10, 12, 16, 20, 24],
                    [10, 15, 20, 25, 15, 10, 5]
                )
            elif outcome == 'switched':
                num_sessions = weighted_choice(
                    [1, 2, 3, 4, 5],
                    [25, 25, 20, 20, 10]
                )
            else:  # dropped
                num_sessions = weighted_choice(
                    [1, 2, 3],
                    [50, 35, 15]
                )
            
            base_date = datetime.fromisoformat(primary_interaction['outcome']['action_timestamp'])
            
            for session_num in range(1, num_sessions + 1):
                session = self._create_session(
                    primary_interaction,
                    session_num,
                    num_sessions,
                    base_date
                )
                sessions.append(session)
                
                if session_num < 4:
                    days_until_next = weighted_choice([7, 10, 14], [60, 25, 15])
                else:
                    days_until_next = weighted_choice([14, 21, 28], [40, 35, 25])
                
                base_date += timedelta(days=days_until_next)
        
        return sessions
    
    def _create_session(self, interaction, session_number, total_sessions, session_date):
        """Crea registro de sesión"""
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        # Tipo de sesión
        clinician_id = interaction['clinician_id']
        if 'medication' in clinician_id:
            session_type = weighted_choice(['medication_management', 'therapy'], [70, 30])
        else:
            session_type = 'individual_therapy'
        
        # Duración
        if session_type == 'medication_management':
            duration = weighted_choice([15, 20, 30], [40, 40, 20])
        else:
            duration = weighted_choice([45, 50, 60], [20, 60, 20])
        
        # Satisfacción
        if session_number == 1:
            base_satisfaction = weighted_choice([5, 6, 7, 8], [10, 30, 40, 20])
        elif session_number <= 3:
            base_satisfaction = weighted_choice([6, 7, 8], [20, 50, 30])
        else:
            if interaction['outcome']['long_term_outcome'] == 'retained':
                base_satisfaction = weighted_choice([7, 8, 9, 10], [10, 30, 40, 20])
            else:
                base_satisfaction = weighted_choice([5, 6, 7, 8], [20, 40, 30, 10])
        
        satisfaction = max(1, min(10, base_satisfaction + random.randint(-1, 1)))
        
        # Indicadores de progreso
        progress_indicators = []
        clinical_needs = interaction['snapshot_features']['stated_needs']
        
        if session_number >= 3:
            progress_indicators.append('initial_rapport_established')
        
        if session_number >= 5:
            progress_indicators.append('treatment_plan_developed')
            if 'anxiety' in clinical_needs or 'depression' in clinical_needs:
                progress_indicators.append('symptom_tracking_started')
        
        if session_number >= 8:
            if random.random() < 0.7:
                progress_indicators.append('symptom_reduction_noted')
            progress_indicators.append('coping_strategies_learned')
        
        if session_number >= 12:
            if random.random() < 0.6:
                progress_indicators.append('significant_improvement')
            if random.random() < 0.5:
                progress_indicators.append('goals_partially_achieved')
        
        if session_number >= 16:
            if random.random() < 0.4:
                progress_indicators.append('goals_achieved')
        
        # Sentimiento clínico
        base_sentiment = 0.5 + (session_number / total_sessions) * 0.3
        if interaction['outcome']['long_term_outcome'] == 'retained':
            base_sentiment += 0.1
        
        clinician_sentiment = round(
            max(0.1, min(0.95, base_sentiment + random.uniform(-0.1, 0.1))), 2
        )
        
        # Adherencia
        if session_number <= 3:
            adherence = round(random.uniform(0.5, 0.8), 2)
        else:
            if interaction['outcome']['long_term_outcome'] == 'retained':
                adherence = round(random.uniform(0.7, 0.95), 2)
            else:
                adherence = round(random.uniform(0.4, 0.7), 2)
        
        # Calidad del match
        if satisfaction >= 8 and interaction['outcome']['long_term_outcome'] == 'retained':
            match_quality = 'excellent'
        elif satisfaction >= 6:
            match_quality = 'good'
        else:
            match_quality = 'poor'
        
        # Probabilidad de cambio
        if match_quality == 'excellent':
            switch_likelihood = round(random.uniform(0.0, 0.1), 2)
        elif match_quality == 'good':
            switch_likelihood = round(random.uniform(0.1, 0.3), 2)
        else:
            switch_likelihood = round(random.uniform(0.4, 0.8), 2)
        
        # Feedback
        feedback_options = {
            'excellent': [
                'great_listener', 'very_helpful', 'feel_understood',
                'excellent_techniques', 'highly_recommend', 'perfect_match'
            ],
            'good': [
                'helpful', 'good_listener', 'professional',
                'knowledgeable', 'supportive', 'accommodating'
            ],
            'poor': [
                'not_a_good_fit', 'didnt_feel_heard', 'too_rigid',
                'not_helpful', 'poor_communication', 'scheduling_issues'
            ]
        }
        
        specific_feedback = random.sample(
            feedback_options[match_quality],
            random.randint(1, 3)
        )
        
        session = {
            'session_id': session_id,
            'user_id': interaction['user_id'],
            'clinician_id': interaction['clinician_id'],
            'interaction_id': interaction['interaction_id'],
            'session_data': {
                'session_number': session_number,
                'date': session_date.isoformat(),
                'duration_minutes': duration,
                'session_type': session_type,
                'completed': True,
                'patient_satisfaction': satisfaction,
                'clinician_notes_sentiment': clinician_sentiment,
                'progress_indicators': progress_indicators,
                'treatment_adherence': adherence
            },
            'recommendation_feedback': {
                'match_quality': match_quality,
                'would_recommend': satisfaction >= 7,
                'switch_likelihood': switch_likelihood,
                'specific_feedback': specific_feedback
            }
        }
        
        return session

# =============================================================================
# FUNCIONES DE VALIDACIÓN Y ESTADÍSTICAS
# =============================================================================

def validate_data_quality(data):
    """Valida la calidad de los datos generados"""
    clinicians = data['clinicians']
    users = data['users']
    interactions = data['interactions']
    sessions = data['sessions']
    
    print("\n🔍 Validando calidad de datos...")
    
    issues = []
    
    # Verificar estados
    states_with_clinicians = set()
    for c in clinicians:
        states_with_clinicians.update(c['basic_info']['license_states'])
    
    users_without_matches = 0
    for user in users:
        user_state = user['stated_preferences']['state']
        if user_state not in states_with_clinicians:
            users_without_matches += 1
    
    if users_without_matches > 0:
        issues.append(f"{users_without_matches} usuarios en estados sin clínicos")
    
    # Verificar IDs
    valid_user_ids = {u['user_id'] for u in users}
    valid_clinician_ids = {c['clinician_id'] for c in clinicians}
    
    for interaction in interactions:
        if interaction['user_id'] not in valid_user_ids:
            issues.append(f"Interacción con user_id inválido: {interaction['user_id']}")
        if interaction['clinician_id'] not in valid_clinician_ids:
            issues.append(f"Interacción con clinician_id inválido: {interaction['clinician_id']}")
    
    valid_interaction_ids = {i['interaction_id'] for i in interactions}
    for session in sessions:
        if session['interaction_id'] not in valid_interaction_ids:
            issues.append(f"Sesión con interaction_id inválido: {session['interaction_id']}")
    
    if issues:
        print("  ⚠️  Problemas encontrados:")
        for issue in issues[:5]:
            print(f"    - {issue}")
        if len(issues) > 5:
            print(f"    ... y {len(issues) - 5} más")
    else:
        print("  ✅ Todos los datos son consistentes")
    
    return len(issues) == 0

def print_detailed_statistics(data):
    """Imprime estadísticas detalladas"""
    clinicians = data['clinicians']
    users = data['users']
    interactions = data['interactions']
    sessions = data['sessions']
    
    print("\n📊 Estadísticas Detalladas:")
    
    # Clínicos
    print(f"\n👨‍⚕️ Clínicos ({len(clinicians)} total):")
    
    immediate_avail = sum(1 for c in clinicians if c['availability_features']['immediate_availability'])
    accepting_new = sum(1 for c in clinicians if c['availability_features']['accepting_new_patients'])
    therapy_only = sum(1 for c in clinicians if c['basic_info']['appointment_types'] == ['therapy'])
    medication_only = sum(1 for c in clinicians if c['basic_info']['appointment_types'] == ['medication'])
    both = len(clinicians) - therapy_only - medication_only
    
    print(f"  - Disponibilidad inmediata: {immediate_avail} ({immediate_avail/len(clinicians)*100:.1f}%)")
    print(f"  - Aceptando nuevos pacientes: {accepting_new} ({accepting_new/len(clinicians)*100:.1f}%)")
    print(f"  - Solo terapia: {therapy_only} ({therapy_only/len(clinicians)*100:.1f}%)")
    print(f"  - Solo medicación: {medication_only} ({medication_only/len(clinicians)*100:.1f}%)")
    print(f"  - Ambos servicios: {both} ({both/len(clinicians)*100:.1f}%)")
    
    # Estados top
    state_counts = defaultdict(int)
    for c in clinicians:
        for state in c['basic_info']['license_states']:
            state_counts[state] += 1
    
    print("\n  📍 Top 5 estados por número de clínicos:")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {state}: {count} clínicos")
    
    # Usuarios
    print(f"\n👥 Usuarios ({len(users)} total):")
    anon = sum(1 for u in users if u['registration_type'] == 'anonymous')
    basic = sum(1 for u in users if u['registration_type'] == 'basic')
    complete = len(users) - anon - basic
    
    print(f"  - Anónimos: {anon} ({anon/len(users)*100:.1f}%)")
    print(f"  - Registrados básicos: {basic} ({basic/len(users)*100:.1f}%)")
    print(f"  - Registrados completos: {complete} ({complete/len(users)*100:.1f}%)")
    
    # Necesidades clínicas
    needs_counter = defaultdict(int)
    for u in users:
        for need in u['stated_preferences']['clinical_needs']:
            needs_counter[need] += 1
    
    print("\n  🧠 Top 5 necesidades clínicas:")
    for need, count in sorted(needs_counter.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    - {need}: {count} usuarios ({count/len(users)*100:.1f}%)")
    
    # Interacciones
    print(f"\n🔄 Interacciones ({len(interactions)} total):")
    
    actions_count = defaultdict(int)
    for i in interactions:
        actions_count[i['outcome']['action']] += 1
    
    print("  📊 Distribución de acciones:")
    for action in ['viewed', 'clicked', 'contacted', 'booked', 'ignored']:
        count = actions_count.get(action, 0)
        if len(interactions) > 0:
            print(f"    - {action}: {count} ({count/len(interactions)*100:.1f}%)")
    
    # Conversión
    scheduled = sum(1 for i in interactions if i['outcome']['appointment_scheduled'])
    completed = sum(1 for i in interactions if i['outcome']['appointment_completed'])
    
    print(f"\n  📈 Métricas de conversión:")
    if len(interactions) > 0:
        print(f"    - Citas agendadas: {scheduled} ({scheduled/len(interactions)*100:.1f}%)")
        print(f"    - Citas completadas: {completed} ({completed/len(interactions)*100:.1f}%)")
    
    # Sesiones
    if sessions:
        print(f"\n📅 Sesiones ({len(sessions)} total):")
        
        avg_satisfaction = sum(s['session_data']['patient_satisfaction'] for s in sessions) / len(sessions)
        print(f"  - Satisfacción promedio: {avg_satisfaction:.1f}/10")
        
        quality_counts = defaultdict(int)
        for s in sessions:
            quality_counts[s['recommendation_feedback']['match_quality']] += 1
        
        print("  🎯 Calidad de matches:")
        for quality in ['excellent', 'good', 'poor']:
            count = quality_counts.get(quality, 0)
            print(f"    - {quality}: {count} ({count/len(sessions)*100:.1f}%)")

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def generate_all_data():
    """Genera todos los datasets necesarios para LunaJoy"""
    
    print("🚀 Iniciando generación de datos mock para LunaJoy...")
    if USE_FAKER:
        print("   ✓ Usando Faker para datos realistas")
    else:
        print("   ⚠️  Faker no disponible, usando generación básica")
    
    # Generar clínicos
    print("\n📋 Generando clínicos...")
    clinician_gen = ClinicianGenerator()
    clinicians = []
    
    num_clinicians = 300
    for i in range(num_clinicians):
        clinician = clinician_gen.generate_clinician(i)
        clinicians.append(clinician)
        if (i + 1) % 50 == 0:
            print(f"  ✓ {i + 1} clínicos generados")
    
    print(f"  ✓ Total: {len(clinicians)} clínicos generados")
    
    # Generar usuarios
    print("\n👥 Generando usuarios...")
    user_gen = UserGenerator(clinicians)
    users = []
    
    # Distribución
    num_anonymous = 500
    num_basic = 800
    num_complete = 1200
    
    # Anónimos
    for i in range(num_anonymous):
        user = user_gen.generate_user(i, 'anonymous')
        users.append(user)
    
    # Básicos
    for i in range(num_anonymous, num_anonymous + num_basic):
        user = user_gen.generate_user(i, 'basic')
        users.append(user)
    
    # Completos
    for i in range(num_anonymous + num_basic, num_anonymous + num_basic + num_complete):
        user = user_gen.generate_user(i, 'complete')
        users.append(user)
        if i % 500 == 0:
            print(f"  ✓ {i} usuarios generados")
    
    print(f"  ✓ Total: {len(users)} usuarios generados")
    
    # Generar interacciones
    print("\n🔄 Generando interacciones...")
    interaction_gen = InteractionGenerator(users, clinicians)
    
    num_interactions = int(len(users) * 5.6)
    interactions = interaction_gen.generate_interactions(num_interactions)
    print(f"  ✓ {len(interactions)} interacciones generadas")
    
    # Generar sesiones
    print("\n📅 Generando sesiones...")
    session_gen = SessionGenerator(interactions)
    sessions = session_gen.generate_sessions()
    print(f"  ✓ {len(sessions)} sesiones generadas")
    
    # Validar
    data = {
        'clinicians': clinicians,
        'users': users,
        'interactions': interactions,
        'sessions': sessions
    }
    
    validate_data_quality(data)
    
    # Guardar archivos
    print("\n💾 Guardando archivos JSON...")
    
    try:
        with open('clinicians.json', 'w', encoding='utf-8') as f:
            json.dump(clinicians, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print("  ✓ clinicians.json guardado")
        
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print("  ✓ users.json guardado")
        
        with open('interactions.json', 'w', encoding='utf-8') as f:
            json.dump(interactions, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print("  ✓ interactions.json guardado")
        
        with open('sessions.json', 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)
        print("  ✓ sessions.json guardado")
        
    except Exception as e:
        print(f"\n❌ Error al guardar archivos: {e}")
        return None
    
    # Mostrar estadísticas
    print_detailed_statistics(data)
    
    print("\n✅ ¡Generación completada exitosamente!")
    print(f"\n📁 Archivos generados:")
    print(f"  - clinicians.json ({len(clinicians)} registros)")
    print(f"  - users.json ({len(users)} registros)")
    print(f"  - interactions.json ({len(interactions)} registros)")
    print(f"  - sessions.json ({len(sessions)} registros)")
    
    return data

# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Función principal del programa"""
    try:
        data = generate_all_data()
        if data:
            print("\n🎉 Proceso completado. Los archivos están listos para usar.")
        else:
            print("\n❌ El proceso no se completó correctamente.")
    except Exception as e:
        print(f"\n❌ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()

# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    main()