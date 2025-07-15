// src/utils/constants.js

export const API_BASE_URL = '/api/v1';

// Actualizado con los 20 estados del dataset
export const STATES = [
  'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
  'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI'
];

// Actualizado con los 10 idiomas del dataset
export const LANGUAGES = [
  'English', 'Spanish', 'Mandarin', 'French', 'Portuguese',
  'Hindi', 'Arabic', 'Russian', 'Korean', 'Vietnamese'
];

// Actualizado con los proveedores de seguro correctos
export const INSURANCE_PROVIDERS = [
  'BlueCross BlueShield',
  'UnitedHealth',
  'Aetna',
  'Cigna',
  'Kaiser',
  'Humana',
  'Anthem',
  'Centene',
  'Molina',
  'WellCare',
  'Private Pay'
];


// Actualizado con todas las necesidades clínicas del dataset
export const CLINICAL_NEEDS = [
  'Anxiety',
  'Depression',
  'Stress',
  'Trauma',
  'PTSD',
  'Grief',
  'ADHD',
  'OCD',
  'Bipolar',
  'Relationship',
  'Family',
  'Parenting',
  'Addiction',
  'Substance Abuse',
  'Self Esteem',
  'Anger',
  'Life Transitions'
];

// Mapping for better display
export const CLINICAL_NEEDS_DISPLAY = {
  'anxiety': 'Anxiety',
  'depression': 'Depression',
  'stress': 'Stress Management',
  'trauma': 'Trauma Recovery',
  'ptsd': 'PTSD',
  'grief': 'Grief & Loss',
  'adhd': 'ADHD',
  'ocd': 'OCD',
  'bipolar': 'Bipolar Disorder',
  'relationship': 'Relationship Issues',
  'family': 'Family Therapy',
  'parenting': 'Parenting Support',
  'addiction': 'Addiction Recovery',
  'substance_abuse': 'Substance Abuse',
  'self_esteem': 'Self-Esteem',
  'anger': 'Anger Management',
  'life_transitions': 'Life Transitions'
};

// Actualizado con los horarios correctos
export const TIME_SLOTS = [
  'morning',
  'afternoon',
  'evening',
  'weekends'
];

export const GENDER_PREFERENCES = [
  { value: '', label: 'No Preference' },
  { value: 'female', label: 'Female' },
  { value: 'male', label: 'Male' },
  { value: 'non_binary', label: 'Non-Binary' }
];

export const APPOINTMENT_TYPES = [
  { value: 'therapy', label: 'Therapy' },
  { value: 'medication', label: 'Medication' }
];

export const URGENCY_LEVELS = [
  { value: 'flexible', label: 'Flexible' },
  { value: 'immediate', label: 'Immediate' }
];

export const EXAMPLE_USERS = [
  { id: 'user_01307_c530ad', description: 'User with complete history' },
  { id: 'user_00500_ac2423', description: 'Basic user' }
];