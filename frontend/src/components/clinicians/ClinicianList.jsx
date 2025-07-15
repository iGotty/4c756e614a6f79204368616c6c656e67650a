import { useState, useEffect, useCallback } from 'react';
import { MapPin, Shield, Star, Heart, ChevronRight, Check, Globe, Video, Sparkles, Grid, List, Info } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import { CLINICAL_NEEDS_DISPLAY } from '../../utils/constants';

// Get API URL from environment
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ClinicianList = ({ 
  clinicians, 
  loading, 
  error, 
  searchInfo, 
  searchParams,
  onViewClinician,
  onContactClinician,
  onSaveClinician 
}) => {
  const [viewMode, setViewMode] = useState('grid');
  const [savedClinicians, setSavedClinicians] = useState(
    JSON.parse(localStorage.getItem('saved_clinicians') || '[]').map(c => c.clinician_id)
  );
  const [explanations, setExplanations] = useState({});
  const [loadingExplanations, setLoadingExplanations] = useState({});
  const [clinicianDetails, setClinicianDetails] = useState({});
  const [loadingDetails, setLoadingDetails] = useState({});

  // Check if user is authenticated from localStorage
  const isUserAuthenticated = () => {
    const savedUser = localStorage.getItem('lunajoy_user');
    return !!savedUser;
  };

  const fetchClinicianDetail = useCallback(async (clinicianId) => {
    if (loadingDetails[clinicianId] || clinicianDetails[clinicianId]) return;

    setLoadingDetails(prev => ({ ...prev, [clinicianId]: true }));

    try {
      const response = await fetch(`${API_URL}/api/v1/clinicians/${clinicianId}`);
      if (response.ok) {
        const data = await response.json();
        setClinicianDetails(prev => ({ ...prev, [clinicianId]: data }));
      }
    } catch (error) {
      console.error(`Error fetching details for ${clinicianId}:`, error);
    } finally {
      setLoadingDetails(prev => ({ ...prev, [clinicianId]: false }));
    }
  }, [loadingDetails, clinicianDetails]);

  // Fetch details for all clinicians when component mounts
  useEffect(() => {
    const fetchAllClinicianDetails = async () => {
      // Fetch details for clinicians that don't have rating info
      const cliniciansToFetch = clinicians.filter(c => 
        !c.performance?.avg_patient_rating && 
        !c.performance_metrics?.avg_patient_rating &&
        !clinicianDetails[c.clinician_id]
      );

      for (const clinician of cliniciansToFetch) {
        fetchClinicianDetail(clinician.clinician_id);
      }
    };

    if (clinicians && clinicians.length > 0) {
      fetchAllClinicianDetails();
    }
  }, [clinicians, clinicianDetails, fetchClinicianDetail]);

  const getClinicianRating = (clinician) => {
    // First check if we have detailed info
    const details = clinicianDetails[clinician.clinician_id];
    if (details?.performance?.avg_patient_rating) {
      return details.performance.avg_patient_rating.toFixed(1);
    }
    
    // Then check the clinician object itself
    if (clinician.performance?.avg_patient_rating) {
      return clinician.performance.avg_patient_rating.toFixed(1);
    }
    
    if (clinician.performance_metrics?.avg_patient_rating) {
      return clinician.performance_metrics.avg_patient_rating.toFixed(1);
    }
    
    // If still loading, show loading indicator
    if (loadingDetails[clinician.clinician_id]) {
      return '...';
    }
    
    return 'N/A';
  };

  // Get clinician image
  const getClinicianImage = (clinician) => {
    const gender = clinician.profile_features?.gender || clinician.gender || 'male';
    const isFemale = gender === 'female';
    
    let hash = 0;
    for (let i = 0; i < clinician.clinician_id.length; i++) {
      hash = ((hash << 5) - hash) + clinician.clinician_id.charCodeAt(i);
      hash = hash & hash;
    }
    
    const imageNum = (Math.abs(hash) % 15) + 1;
    const paddedNum = String(imageNum).padStart(3, '0');
    
    try {
      if (isFemale) {
        const femaleImageNum = 15 + imageNum;
        const paddedFemaleNum = String(femaleImageNum).padStart(3, '0');
        return require(`../../assets/images/clinicians/png/${paddedFemaleNum}-female doctor.png`);
      } else {
        return require(`../../assets/images/clinicians/png/${paddedNum}-medical doctor.png`);
      }
    } catch (err) {
      return `https://api.dicebear.com/7.x/avataaars/svg?seed=${clinician.clinician_id}`;
    }
  };

  const handleSave = (clinician) => {
    const isSaved = savedClinicians.includes(clinician.clinician_id);
    
    if (isSaved) {
      setSavedClinicians(prev => prev.filter(id => id !== clinician.clinician_id));
    } else {
      setSavedClinicians(prev => [...prev, clinician.clinician_id]);
    }
    
    onSaveClinician(clinician);
  };

  const handleViewClinician = (clinician) => {
    // Pass the detailed info if available
    const enrichedClinician = clinicianDetails[clinician.clinician_id] 
      ? { ...clinician, ...clinicianDetails[clinician.clinician_id] }
      : clinician;
    
    onViewClinician(enrichedClinician);
  };

  const getSpecialtyDisplay = (specialty) => {
    return CLINICAL_NEEDS_DISPLAY[specialty.toLowerCase()] || specialty;
  };

  const fetchExplanation = async (clinicianId) => {
    if (explanations[clinicianId] || loadingExplanations[clinicianId]) return;

    setLoadingExplanations(prev => ({ ...prev, [clinicianId]: true }));

    try {
      // Simulate API call for explanation
      // In real implementation, this would call the actual API
      const mockExplanation = `This professional is an excellent match because they specialize in ${
        clinicians.find(c => c.clinician_id === clinicianId)?.specialties?.[0] || 'your needs'
      }, accept your insurance, and have immediate availability.`;
      
      setTimeout(() => {
        setExplanations(prev => ({ ...prev, [clinicianId]: mockExplanation }));
        setLoadingExplanations(prev => ({ ...prev, [clinicianId]: false }));
      }, 500);
    } catch (err) {
      setLoadingExplanations(prev => ({ ...prev, [clinicianId]: false }));
    }
  };

  if (loading) {
    return (
      <div className="min-h-[600px] flex items-center justify-center">
        <LoadingSpinner variant="search" message="Finding your perfect matches..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-8">
        <ErrorMessage message={error} type="error" />
      </div>
    );
  }

  if (!clinicians || clinicians.length === 0) {
    return (
      <div className="max-w-2xl mx-auto p-8 text-center">
        <ErrorMessage 
          message="No matches found. Try adjusting your search criteria." 
          type="empty" 
        />
      </div>
    );
  }

  return (
    <div>
      {/* Results Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-3xl font-display font-bold text-gray-900 mb-2">
              Your Matches
            </h2>
            <p className="text-gray-600">
              {clinicians.length} mental health professionals match your criteria
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-4 py-2 rounded transition-all ${
                viewMode === 'grid' 
                  ? 'bg-white shadow text-gray-900' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded transition-all ${
                viewMode === 'list' 
                  ? 'bg-white shadow text-gray-900' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Active Filters */}
      {searchParams && (
        <div className="flex flex-wrap gap-2 mb-6">
          {searchParams.state && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center">
              <MapPin className="w-3 h-3 mr-1" />
              {searchParams.state}
            </span>
          )}
          {searchParams.insurance_provider && (
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm flex items-center">
              <Shield className="w-3 h-3 mr-1" />
              {searchParams.insurance_provider}
            </span>
          )}
          {searchParams.urgency_level === 'immediate' && (
            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
              Urgent
            </span>
          )}
          {searchParams.appointment_type && (
            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
              {searchParams.appointment_type === 'therapy' ? 'Therapy' : 'Medication'}
            </span>
          )}
        </div>
      )}

      {/* Results Grid or List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {clinicians.map((clinician, index) => (
            <div
              key={clinician.clinician_id}
              className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all animate-fade-in-up flex flex-col h-full"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Profile Header */}
              <div className="p-6 flex-1 flex flex-col">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 rounded-full overflow-hidden bg-gray-100 flex-shrink-0">
                      <img
                        src={getClinicianImage(clinician)}
                        alt={clinician.clinician_name}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          e.target.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${clinician.clinician_id}`;
                        }}
                      />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {clinician.clinician_name}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {clinician.profile_features?.certifications?.[0] || 'Licensed Professional'}
                      </p>
                      <div className="flex items-center mt-1">
                        <Star className="w-4 h-4 text-yellow-500 mr-1" />
                        <span className="text-sm text-gray-600">
                          {getClinicianRating(clinician)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className={`text-xl font-bold ${
                      clinician.match_score >= 0.8 ? 'text-green-600' :
                      clinician.match_score >= 0.6 ? 'text-blue-600' :
                      'text-gray-600'
                    }`}>
                      {Math.round(clinician.match_score * 100)}%
                    </div>
                    <p className="text-xs text-gray-500">Match</p>
                  </div>
                </div>

                {/* Specialties */}
                <div className="flex flex-wrap gap-1 mb-4">
                  {clinician.specialties?.slice(0, 3).map((specialty, idx) => (
                    <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                      {getSpecialtyDisplay(specialty)}
                    </span>
                  ))}
                </div>

                {/* Key Features */}
                <div className="space-y-2 mb-4 flex-1">
                  {clinician.is_available && (
                    <div className="flex items-center text-sm text-green-700">
                      <Check className="w-4 h-4 mr-2" />
                      Available now
                    </div>
                  )}
                  {clinician.accepts_insurance !== false && searchParams.insurance_provider && (
                    <div className="flex items-center text-sm text-blue-700">
                      <Shield className="w-4 h-4 mr-2" />
                      Accepts your insurance
                    </div>
                  )}
                </div>

                {/* Why This Match */}
                <button
                  onClick={() => fetchExplanation(clinician.clinician_id)}
                  className="w-full text-left p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors mb-4"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 font-medium">Why this match?</span>
                    <Info className="w-4 h-4 text-gray-400" />
                  </div>
                  {explanations[clinician.clinician_id] && (
                    <p className="text-xs text-gray-600 mt-2">
                      {explanations[clinician.clinician_id]}
                    </p>
                  )}
                  {loadingExplanations[clinician.clinician_id] && (
                    <p className="text-xs text-gray-500 mt-2">Loading...</p>
                  )}
                </button>

                {/* Actions - Always at bottom */}
                <div className="flex items-center space-x-2 mt-auto">
                  <button
                    onClick={() => handleViewClinician(clinician)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
                  >
                    View Profile
                  </button>
                  <button
                    onClick={() => handleSave(clinician)}
                    className={`p-2 rounded-lg transition-colors ${
                      savedClinicians.includes(clinician.clinician_id)
                        ? 'bg-red-50 text-red-600 hover:bg-red-100'
                        : 'bg-gray-100 text-gray-400 hover:text-red-500 hover:bg-gray-200'
                    }`}
                  >
                    <Heart className={`w-5 h-5 ${
                      savedClinicians.includes(clinician.clinician_id) ? 'fill-current' : ''
                    }`} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {clinicians.map((clinician, index) => (
            <div
              key={clinician.clinician_id}
              className="bg-white rounded-xl shadow-md hover:shadow-lg transition-all p-6 animate-fade-in-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-start space-x-6">
                {/* Profile Image */}
                <div className="flex-shrink-0">
                  <div className="w-24 h-24 rounded-full overflow-hidden bg-gray-100">
                    <img
                      src={getClinicianImage(clinician)}
                      alt={clinician.clinician_name}
                      className="w-full h-full object-contain"
                      onError={(e) => {
                        e.target.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${clinician.clinician_id}`;
                      }}
                    />
                  </div>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-1">
                        {clinician.clinician_name}
                      </h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        {clinician.profile_features?.certifications && (
                          <span>{clinician.profile_features.certifications[0]}</span>
                        )}
                        {clinician.years_experience && (
                          <span>{clinician.years_experience}+ years experience</span>
                        )}
                        <div className="flex items-center">
                          <Star className="w-4 h-4 text-yellow-500 mr-1" />
                          <span>{getClinicianRating(clinician)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Match Score */}
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${
                        clinician.match_score >= 0.8 ? 'text-green-600' :
                        clinician.match_score >= 0.6 ? 'text-blue-600' :
                        'text-gray-600'
                      }`}>
                        {Math.round(clinician.match_score * 100)}%
                      </div>
                      <p className="text-xs text-gray-500">Match</p>
                    </div>
                  </div>

                  {/* Specialties */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {clinician.specialties?.slice(0, 4).map((specialty, idx) => (
                      <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                        {getSpecialtyDisplay(specialty)}
                      </span>
                    ))}
                    {clinician.specialties?.length > 4 && (
                      <span className="px-3 py-1 bg-gray-50 text-gray-600 rounded-full text-sm">
                        +{clinician.specialties.length - 4} more
                      </span>
                    )}
                  </div>

                  {/* Key Features */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    {clinician.is_available && (
                      <div className="flex items-center text-sm text-green-700 bg-green-50 px-3 py-2 rounded-lg">
                        <Check className="w-4 h-4 mr-2" />
                        Available now
                      </div>
                    )}
                    {clinician.accepts_insurance !== false && searchParams.insurance_provider && (
                      <div className="flex items-center text-sm text-blue-700 bg-blue-50 px-3 py-2 rounded-lg">
                        <Shield className="w-4 h-4 mr-2" />
                        Insurance accepted
                      </div>
                    )}
                    {clinician.languages?.includes(searchParams.language) && searchParams.language && (
                      <div className="flex items-center text-sm text-purple-700 bg-purple-50 px-3 py-2 rounded-lg">
                        <Globe className="w-4 h-4 mr-2" />
                        {searchParams.language}
                      </div>
                    )}
                    {clinician.appointment_types?.includes('video') && (
                      <div className="flex items-center text-sm text-indigo-700 bg-indigo-50 px-3 py-2 rounded-lg">
                        <Video className="w-4 h-4 mr-2" />
                        Video sessions
                      </div>
                    )}
                  </div>

                  {/* Match Explanation */}
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <button
                        onClick={() => fetchExplanation(clinician.clinician_id)}
                        className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
                      >
                        <Info className="w-4 h-4 mr-1" />
                        Why this match?
                      </button>
                      {explanations[clinician.clinician_id] && (
                        <p className="text-sm text-gray-600 mt-2">
                          {explanations[clinician.clinician_id]}
                        </p>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-3 ml-4">
                      <button
                        onClick={() => handleViewClinician(clinician)}
                        className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm flex items-center"
                      >
                        View Profile
                        <ChevronRight className="w-4 h-4 ml-1" />
                      </button>
                      <button
                        onClick={() => onContactClinician(clinician)}
                        className="px-5 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm"
                      >
                        Contact
                      </button>
                      <button
                        onClick={() => handleSave(clinician)}
                        className={`p-2 rounded-lg transition-colors ${
                          savedClinicians.includes(clinician.clinician_id)
                            ? 'bg-red-50 text-red-600 hover:bg-red-100'
                            : 'bg-gray-100 text-gray-400 hover:text-red-500 hover:bg-gray-200'
                        }`}
                      >
                        <Heart className={`w-5 h-5 ${
                          savedClinicians.includes(clinician.clinician_id) ? 'fill-current' : ''
                        }`} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Premium Prompt for Non-Authenticated Users Only */}
      {!isUserAuthenticated() && (
        <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
          <div className="flex items-start space-x-3">
            <Sparkles className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <p className="text-gray-900 font-semibold mb-1">Get better matches!</p>
              <p className="text-gray-700 text-sm">
                Sign in to unlock personalized recommendations based on your preferences and history.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClinicianList;