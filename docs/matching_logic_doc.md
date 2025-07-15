# LunaJoy Matching Engine - Matching Logic & Algorithms

## 🧠 Core Matching Philosophy

The LunaJoy matching system is designed around the principle of **Progressive Personalization**. As users engage more with the platform, the system learns and adapts, providing increasingly accurate matches.

## 📊 Three-Tier Matching Strategy

### Tier 1: Anonymous Users (Cold Start)
**Goal**: Demonstrate value quickly to encourage registration

```python
def match_anonymous(user_preferences):
    # 1. Apply hard filters (state, appointment_type)
    candidates = filter_by_requirements(all_clinicians)
    
    # 2. Score based on immediate needs
    for clinician in candidates:
        score = calculate_content_score(clinician, user_preferences)
    
    # 3. Return top 5 generic matches
    return top_k(candidates, k=5)
```

**Scoring Formula**:
```
Score = 0.4 × Availability + 0.2 × Insurance + 0.2 × Specialties + 0.1 × LoadBalance + 0.1 × Preferences
```

### Tier 2: Basic Registered Users
**Goal**: Leverage demographic data for better personalization

```python
def match_basic(user):
    # 1. Anonymous matching as baseline
    base_matches = match_anonymous(user.preferences)
    
    # 2. Identify user cluster
    cluster_id = clustering_service.get_cluster(user)
    
    # 3. Find popular clinicians in cluster
    cluster_popular = get_cluster_favorites(cluster_id)
    
    # 4. Boost scores for cluster matches
    for match in base_matches:
        if match.clinician_id in cluster_popular:
            match.score *= 1.15  # Cluster boost
```

**Enhanced Scoring**:
```
Score = BaseScore × ClusterBoost × DemographicMatch
```

### Tier 3: Users with History
**Goal**: Predict success using behavioral patterns

```python
def match_complete(user):
    # 1. Get collaborative filtering predictions
    cf_predictions = collaborative_engine.predict(user)
    
    # 2. Calculate content-based scores
    content_scores = calculate_content_scores(user)
    
    # 3. Hybrid scoring
    for clinician in candidates:
        final_score = 0.6 × content_scores[clinician] + 
                     0.4 × cf_predictions[clinician]
    
    # 4. Apply ML adjustments
    apply_ml_boosting(matches, user.history)
```

## 🔍 Filtering Logic

### Hard Filters (Mandatory)
These filters MUST be satisfied for a match to occur:

1. **State License**
   ```python
   def filter_by_state(clinicians, user_state):
       return [c for c in clinicians 
               if user_state in c.license_states]
   ```

2. **Appointment Type**
   ```python
   def filter_by_appointment_type(clinicians, type):
       return [c for c in clinicians 
               if type in c.appointment_types]
   ```

3. **Accepting Patients**
   ```python
   def filter_accepting_patients(clinicians):
       return [c for c in clinicians 
               if c.accepting_new_patients]
   ```

### Soft Filters (Scoring Influence)
These preferences influence scoring but don't exclude matches:

- **Language**: Non-English speakers get boost, but English speakers aren't excluded
- **Gender Preference**: Matching gender gets boost
- **Time Slots**: Available slots increase score

## 📈 Scoring Components

### 1. Availability Score
```python
def score_availability(clinician, user):
    if user.urgency_level == "immediate":
        return 1.0 if clinician.immediate_availability else 0.2
    else:
        base = clinician.availability_score
        if clinician.accepting_new_patients:
            base = min(base + 0.2, 1.0)
        return base
```

### 2. Insurance Compatibility
```python
def score_insurance(clinician, user):
    if not user.has_insurance():
        return 0.5  # Neutral
    
    # Deterministic simulation based on IDs
    acceptance_probability = calculate_insurance_match(
        clinician.id, 
        user.insurance_provider
    )
    return 1.0 if accepted else 0.0
```

### 3. Specialty Matching

#### Basic Matching (Anonymous)
```python
def score_specialties_basic(clinician, user):
    user_needs = set(user.clinical_needs)
    clinician_specs = set(clinician.specialties)
    
    if not user_needs:
        return 0.5
    
    overlap = user_needs & clinician_specs
    return len(overlap) / len(user_needs)
```

#### Enhanced Matching (Registered)
```python
def score_specialties_enhanced(clinician, user):
    base_score = score_specialties_basic(clinician, user)
    
    # Consider clinician's success rate in specialties
    success_scores = []
    for need in user.clinical_needs:
        if need in clinician.success_by_specialty:
            success_scores.append(clinician.success_by_specialty[need])
    
    if success_scores:
        avg_success = mean(success_scores)
        return 0.6 × base_score + 0.4 × avg_success
    
    return base_score
```

#### ML-Enhanced Matching (History)
```python
def score_specialties_ml(clinician, user):
    enhanced_score = score_specialties_enhanced(clinician, user)
    
    # Use embeddings for semantic similarity
    if has_embeddings(clinician, user):
        cosine_sim = calculate_cosine_similarity(
            clinician.specialty_vector,
            user.preference_vector
        )
        return 0.5 × enhanced_score + 0.5 × cosine_sim
    
    return enhanced_score
```

### 4. Load Balancing
```python
def score_load_balance(clinician):
    load_ratio = clinician.current_patients / clinician.max_capacity
    
    if load_ratio < 0.5:
        return 1.0
    elif load_ratio < 0.7:
        return 0.8
    elif load_ratio < 0.85:
        return 0.6
    else:
        return 0.3
```

## 🤖 Machine Learning Components

### User Clustering (8 Clusters)
```python
CLUSTERS = {
    0: "Young first-timers with anxiety/stress",
    1: "Experienced adults with complex issues",
    2: "Urgent cases with insurance",
    3: "Flexible cases without insurance",
    4: "Couples/family therapy seekers",
    5: "Medication management",
    6: "Trauma/PTSD cases",
    7: "Other/General"
}

def assign_cluster(user):
    if user.appointment_type == "medication":
        return 5
    
    if "trauma" in user.clinical_needs:
        return 6
    
    if user.urgency_level == "immediate" and user.has_insurance():
        return 2
    
    # ... more rules
```

### Collaborative Filtering
```python
def build_user_item_matrix():
    matrix = defaultdict(dict)
    
    for interaction in all_interactions:
        score = interaction_to_score(interaction)
        matrix[user_id][clinician_id] = max(
            matrix[user_id][clinician_id], 
            score
        )
    
    return matrix

def predict_scores(user, candidates):
    similar_users = find_similar_users(user)
    predictions = {}
    
    for clinician_id in candidates:
        scores = []
        for similar_user in similar_users:
            if clinician_id in user_item_matrix[similar_user]:
                scores.append(user_item_matrix[similar_user][clinician_id])
        
        predictions[clinician_id] = mean(scores) if scores else 0.5
    
    return predictions
```

### Success Prediction
```python
def predict_success_rate(clinician, user):
    factors = []
    
    # Clinician performance
    factors.append(clinician.avg_rating / 5.0)
    factors.append(clinician.retention_rate)
    
    # Specialty match
    factors.append(score_specialties_ml(clinician, user))
    
    # Historical similarity
    factors.append(calculate_historical_similarity(clinician, user))
    
    return weighted_mean(factors, weights=[0.2, 0.3, 0.3, 0.2])
```

## 🎯 Adjustment Factors

### New Clinician Boost
```python
if is_new_clinician(clinician):  # First 30 days
    score *= 1.1
```

### Overload Penalty
```python
if clinician.load_ratio > 0.85:
    score *= 0.7
```

### Diversity Boost
```python
def apply_diversity(matches):
    seen_attributes = set()
    
    for i, match in enumerate(matches):
        if i < 3:  # Top 3 unchanged
            update_seen(match, seen_attributes)
        else:
            diversity_score = calculate_diversity(match, seen_attributes)
            match.score *= diversity_score
            update_seen(match, seen_attributes)
    
    return sort_by_score(matches)
```

## 📊 Weight Configurations

### Urgent Users
```python
WEIGHTS_URGENT = {
    "availability": 0.40,
    "insurance": 0.20,
    "specialties": 0.20,
    "load_balance": 0.10,
    "preferences": 0.10
}
```

### Flexible Users
```python
WEIGHTS_FLEXIBLE = {
    "availability": 0.25,
    "insurance": 0.25,
    "specialties": 0.25,
    "load_balance": 0.15,
    "preferences": 0.10
}
```

## 🔄 Interaction Score Mapping

```python
ACTION_SCORES = {
    "booked": 1.0,       # Maximum positive signal
    "contacted": 0.7,    # Strong interest
    "clicked": 0.4,      # Moderate interest
    "viewed": 0.2,       # Weak interest
    "ignored": 0.0,      # No interest
    "rejected": -0.5     # Negative signal
}
```

## 📈 Performance Optimizations

### 1. Early Termination
```python
def apply_filters_optimized(clinicians, filters):
    # Check most restrictive filters first
    if filters.state:
        clinicians = filter_by_state(clinicians, filters.state)
        if len(clinicians) < MIN_RESULTS:
            return clinicians  # Early termination
```

### 2. Cached Scoring
```python
@lru_cache(maxsize=1000)
def get_specialty_overlap(user_needs, clinician_specs):
    return len(set(user_needs) & set(clinician_specs))
```

### 3. Batch Processing
```python
def score_batch(clinicians, user):
    # Vectorized operations for efficiency
    availability_scores = np.array([c.availability for c in clinicians])
    insurance_scores = np.array([score_insurance(c, user) for c in clinicians])
    
    return availability_scores * 0.4 + insurance_scores * 0.2 + ...
```

## 🎲 Deterministic Randomness

To ensure consistent results for testing while simulating randomness:

```python
def deterministic_hash(seed_string):
    """Generate deterministic value from string"""
    return int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)

def simulate_insurance_acceptance(clinician_id, insurance):
    hash_val = deterministic_hash(f"{clinician_id}{insurance}")
    base_probability = 70
    
    if insurance in ["Aetna", "Blue Cross"]:
        base_probability = 85
    
    return (hash_val % 100) < base_probability
```

## 📊 Match Quality Metrics

### nDCG (Normalized Discounted Cumulative Gain)
```python
def calculate_ndcg(predicted_ranking, true_relevance):
    dcg = sum(rel / log2(i + 2) for i, rel in enumerate(true_relevance))
    idcg = sum(rel / log2(i + 2) for i, rel in enumerate(sorted(true_relevance, reverse=True)))
    return dcg / idcg if idcg > 0 else 0
```

### Conversion Rate
```python
conversion_rate = bookings / total_views
```

### Match Satisfaction
```python
satisfaction_score = (positive_feedback / total_feedback) * 100
```