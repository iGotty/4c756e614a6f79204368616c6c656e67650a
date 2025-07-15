import React, { useState, useEffect } from 'react';
import { Star, Calendar, Award, Users, MapPin, Clock, Shield, Heart, Video, MessageCircle, ChevronRight, Check, Briefcase, GraduationCap, Activity, Phone } from 'lucide-react';

// Get API URL from environment
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ClinicianDetailModal = ({ clinician, isOpen, onClose, onContact, onSchedule }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [detailedInfo, setDetailedInfo] = useState(null);

  useEffect(() => {
    const fetchDetailedInfo = async () => {
      if (!clinician?.clinician_id) return;
      
      try {
        const response = await fetch(`${API_URL}/api/v1/clinicians/${clinician.clinician_id}`);
        if (response.ok) {
          const data = await response.json();
          setDetailedInfo(data);
        }
      } catch (error) {
        console.error('Error fetching clinician details:', error);
      }
    };

    if (isOpen && clinician) {
      setIsAnimating(true);
      document.body.style.overflow = 'hidden';
      // Reset tab when opening
      setActiveTab('overview');
      setImageLoaded(false);
      
      // Fetch detailed info if not already present
      if (!clinician.basic_info && clinician.clinician_id) {
        fetchDetailedInfo();
      }
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, clinician]);

  // Use detailed info if available, otherwise use data from listing
  const clinicianData = detailedInfo || clinician;

  if (!isOpen || !clinician) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // Generate clinician image
  const getClinicianImage = () => {
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

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Users },
    { id: 'specialties', label: 'Expertise', icon: Award },
    { id: 'availability', label: 'Availability', icon: Calendar }
  ];

  const rating = clinicianData.performance?.avg_patient_rating || 
                 clinicianData.performance_metrics?.avg_patient_rating || 
                 null;
  const patientCount = clinicianData.availability?.current_patient_count || 
                       clinicianData.availability_features?.current_patient_count || 
                       0;
  const successRate = clinicianData.performance?.retention_rate 
                      ? Math.round(clinicianData.performance.retention_rate * 100)
                      : clinicianData.performance_metrics?.retention_rate 
                      ? Math.round(clinicianData.performance_metrics.retention_rate * 100)
                      : null;
  const totalPatientsHelped = clinicianData.performance?.total_patients_helped || 0;

  // Get basic info with fallbacks
  const fullName = clinicianData.basic_info?.full_name || clinicianData.clinician_name || 'Healthcare Professional';
  const licenseStates = clinicianData.basic_info?.license_states || clinicianData.license_states || [];
  const languages = clinicianData.profile?.languages || clinicianData.languages || ['English'];
  const yearsExperience = clinicianData.profile?.years_experience || clinicianData.years_experience || null;
  const specialties = clinicianData.profile?.specialties || clinicianData.specialties || [];
  const certifications = clinicianData.profile?.certifications || clinicianData.profile_features?.certifications || [];
  const ageGroupsServed = clinicianData.profile?.age_groups_served || clinicianData.profile_features?.age_groups_served || [];
  
  // Availability info
  const isAvailable = clinicianData.availability?.immediate_availability !== false || clinicianData.is_available;
  const acceptingNew = clinicianData.availability?.accepting_new_patients !== false;
  const capacityPercentage = clinicianData.availability?.capacity_percentage || 
    (clinicianData.availability?.current_patient_count && clinicianData.availability?.max_patient_capacity 
      ? Math.round((clinicianData.availability.current_patient_count / clinicianData.availability.max_patient_capacity) * 100)
      : null);

  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className={`bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] sm:max-h-[85vh] flex flex-col shadow-2xl transform transition-all duration-500 ${
        isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
      }`}>
        {/* Header - Responsive Design */}
        <div className="relative bg-gradient-to-br from-blue-600 to-blue-700 p-4 sm:p-6 rounded-t-2xl flex-shrink-0">
          {/* Profile Info - Stack on mobile */}
          <div className="flex flex-col sm:flex-row items-center sm:items-end gap-4 sm:gap-6">
            {/* Profile Image - Responsive sizing */}
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full overflow-hidden bg-white p-1 sm:p-1.5 shadow-xl flex-shrink-0">
              <img
                src={getClinicianImage()}
                alt={clinician.clinician_name}
                className={`w-full h-full object-contain rounded-full transition-all duration-700 ${
                  imageLoaded ? 'opacity-100' : 'opacity-0'
                }`}
                onLoad={() => setImageLoaded(true)}
                onError={(e) => {
                  e.target.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${clinician.clinician_id}`;
                }}
              />
            </div>

            {/* Name and Info with Match Score - Updated Layout */}
            <div className="flex-1 flex flex-col sm:flex-row items-center sm:items-end gap-3 sm:gap-4">
              <div className="text-center sm:text-left flex-1">
                <h2 className="text-xl sm:text-2xl font-bold text-white mb-1">{fullName}</h2>
                <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2 sm:gap-4 text-blue-100 text-sm">
                  {certifications.length > 0 && (
                    <span className="flex items-center">
                      <GraduationCap className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                      <span className="hidden sm:inline">{certifications.join(', ')}</span>
                      <span className="sm:hidden">{certifications[0]}</span>
                    </span>
                  )}
                  {yearsExperience !== null && (
                    <span className="flex items-center">
                      <Briefcase className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                      {yearsExperience}+ yrs
                    </span>
                  )}
                  {licenseStates.length > 0 && (
                    <span className="flex items-center">
                      <MapPin className="w-3 h-3 sm:w-4 sm:h-4 mr-1" />
                      <span className="hidden sm:inline">{licenseStates.join(', ')}</span>
                      <span className="sm:hidden">{licenseStates[0]}{licenseStates.length > 1 && ` +${licenseStates.length - 1}`}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Match Score - Now positioned right after doctor info */}
              <div className="bg-white/20 backdrop-blur rounded-lg p-2 sm:p-3 text-center flex-shrink-0">
                <div className="text-xl sm:text-2xl font-bold text-white">
                  {Math.round(clinician.match_score * 100)}%
                </div>
                <p className="text-blue-100 text-xs">Match</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats - Responsive Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 p-3 sm:p-4 bg-gray-50 border-b flex-shrink-0">
          {rating !== null && (
            <div className="text-center">
              <div className="flex items-center justify-center text-yellow-500 mb-1">
                <Star className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <p className="text-lg sm:text-xl font-bold text-gray-900">{rating.toFixed(1)}</p>
              <p className="text-xs text-gray-600">Rating</p>
            </div>
          )}
          {patientCount > 0 && (
            <div className="text-center">
              <div className="flex items-center justify-center text-blue-600 mb-1">
                <Users className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <p className="text-lg sm:text-xl font-bold text-gray-900">{patientCount}</p>
              <p className="text-xs text-gray-600">Patients</p>
            </div>
          )}
          {successRate !== null && (
            <div className="text-center">
              <div className="flex items-center justify-center text-green-600 mb-1">
                <Activity className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <p className="text-lg sm:text-xl font-bold text-gray-900">{successRate}%</p>
              <p className="text-xs text-gray-600">Success</p>
            </div>
          )}
          {totalPatientsHelped > 0 && (
            <div className="text-center">
              <div className="flex items-center justify-center text-purple-600 mb-1">
                <Heart className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <p className="text-lg sm:text-xl font-bold text-gray-900">{totalPatientsHelped}</p>
              <p className="text-xs text-gray-600">Helped</p>
            </div>
          )}
        </div>

        {/* Tabs - Scrollable on mobile */}
        <div className="border-b flex-shrink-0">
          <div className="flex space-x-1 px-4 sm:px-6 overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-3 sm:py-4 px-4 sm:px-6 font-medium text-sm transition-all flex items-center space-x-2 border-b-2 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content - Scrollable with proper padding */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          {activeTab === 'overview' && (
            <div className="space-y-4 sm:space-y-6 animate-fade-in">
              {/* About */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 sm:mb-3">About</h3>
                <p className="text-sm sm:text-base text-gray-700 leading-relaxed">
                  {clinician.bio || `${fullName} is an experienced mental health professional specializing in ${specialties.slice(0, 3).join(', ') || 'various areas'}. With a compassionate approach, they help clients achieve their wellness goals.`}
                </p>
              </div>

              {/* Key Information - Stack on mobile */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                {/* Contact & Session Info */}
                <div className="space-y-3 sm:space-y-4">
                  <h4 className="font-semibold text-gray-900">Contact & Sessions</h4>
                  
                  <div className="space-y-2 sm:space-y-3">
                    <div className="flex items-center text-sm sm:text-base text-gray-700">
                      <Video className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3 text-blue-600 flex-shrink-0" />
                      <span>Video sessions available</span>
                    </div>
                    <div className="flex items-center text-sm sm:text-base text-gray-700">
                      <Phone className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3 text-green-600 flex-shrink-0" />
                      <span>Phone sessions available</span>
                    </div>
                    <div className="flex items-center text-sm sm:text-base text-gray-700">
                      <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3 text-purple-600 flex-shrink-0" />
                      <span>In-app messaging</span>
                    </div>
                  </div>
                </div>

                {/* Languages & Insurance */}
                <div className="space-y-3 sm:space-y-4">
                  <h4 className="font-semibold text-gray-900">Languages & Insurance</h4>
                  
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs sm:text-sm text-gray-600 mb-2">Languages spoken:</p>
                      <div className="flex flex-wrap gap-2">
                        {languages.map((lang, idx) => (
                          <span key={idx} className="px-2 sm:px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs sm:text-sm">
                            {lang}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs sm:text-sm text-gray-600 mb-2">Insurance:</p>
                      <div className="flex items-center">
                        <Shield className={`w-4 h-4 sm:w-5 sm:h-5 mr-2 flex-shrink-0 ${clinician.accepts_insurance ? 'text-green-600' : 'text-gray-400'}`} />
                        <span className="text-sm sm:text-base text-gray-700">
                          {clinician.accepts_insurance ? 'Accepts most major insurance' : 'Self-pay options available'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Why This Match - Responsive padding */}
              {(clinicianData.matching_info || clinician.explanation) && (
                <div className="bg-blue-50 rounded-lg p-3 sm:p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 sm:mb-3 flex items-center text-sm sm:text-base">
                    <Star className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-yellow-500" />
                    Why This Match?
                  </h4>
                  
                  {clinician.matching_info?.best_suited_for && (
                    <div className="mb-3">
                      <p className="text-xs sm:text-sm font-medium text-gray-700 mb-2">Best suited for:</p>
                      <div className="space-y-1">
                        {clinician.matching_info.best_suited_for.map((item, idx) => (
                          <div key={idx} className="flex items-start">
                            <Check className="w-3 h-3 sm:w-4 sm:h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                            <span className="text-sm sm:text-base text-gray-700">{item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {clinician.explanation?.primary_reasons && (
                    <div className="space-y-1">
                      {clinician.explanation.primary_reasons.map((reason, idx) => (
                        <div key={idx} className="flex items-start">
                          <Check className="w-3 h-3 sm:w-4 sm:h-4 mr-2 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-sm sm:text-base text-gray-700">{reason}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'specialties' && (
            <div className="space-y-4 sm:space-y-6 animate-fade-in">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3 sm:mb-4">Areas of Expertise</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 sm:gap-3">
                  {specialties.map((specialty, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-3 sm:p-4 text-center hover:bg-gray-100 transition-colors">
                      <p className="font-medium text-sm sm:text-base text-gray-800 capitalize">
                        {specialty.replace(/_/g, ' ')}
                      </p>
                      {(clinician.performance?.success_by_specialty?.[specialty] || clinicianData.performance?.success_by_specialty?.[specialty]) && (
                        <p className="text-xs text-gray-600 mt-1">
                          {Math.round((clinician.performance?.success_by_specialty?.[specialty] || clinicianData.performance?.success_by_specialty?.[specialty]) * 100)}% success
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Treatment Approaches */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Treatment Approaches</h4>
                <div className="space-y-2">
                  {['Cognitive Behavioral Therapy (CBT)', 'Mindfulness-Based Therapy', 'Solution-Focused Therapy', 'Trauma-Informed Care'].map((approach, idx) => (
                    <div key={idx} className="flex items-center text-sm sm:text-base text-gray-700">
                      <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 mr-2 text-gray-400 flex-shrink-0" />
                      <span>{approach}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Age Groups */}
              {ageGroupsServed.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Age Groups Served</h4>
                  <div className="flex flex-wrap gap-2">
                    {ageGroupsServed.map((age, idx) => (
                      <span key={idx} className="px-3 sm:px-4 py-1 sm:py-2 bg-purple-100 text-purple-700 rounded-full text-xs sm:text-sm capitalize">
                        {age}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'availability' && (
            <div className="space-y-4 sm:space-y-6 animate-fade-in">
              {/* Current Status */}
              <div className={`p-4 sm:p-6 rounded-xl ${
                isAvailable 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-yellow-50 border border-yellow-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-2 sm:mr-3 flex-shrink-0 ${
                        isAvailable ? 'bg-green-500' : 'bg-yellow-500'
                      }`}></div>
                      <p className={`font-medium text-sm sm:text-base ${
                        isAvailable ? 'text-green-800' : 'text-yellow-800'
                      }`}>
                        {acceptingNew 
                          ? 'Accepting new patients' 
                          : 'Not currently accepting new patients'}
                      </p>
                    </div>
                    {clinician.matching_info?.availability_status && (
                      <p className="text-xs sm:text-sm mt-1 ml-5 sm:ml-6 text-gray-600">
                        {clinician.matching_info.availability_status}
                      </p>
                    )}
                  </div>
                  {capacityPercentage !== null && (
                    <div className="text-right ml-4">
                      <p className="text-xl sm:text-2xl font-bold text-gray-900">{capacityPercentage}%</p>
                      <p className="text-xs text-gray-600">Capacity</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Weekly Schedule - Responsive */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-3 sm:mb-4">Typical Availability</h4>
                <div className="grid grid-cols-7 gap-1 sm:gap-2 text-center">
                  {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, idx) => (
                    <div key={idx}>
                      <p className="text-xs sm:text-sm font-medium text-gray-700 mb-1 sm:mb-2">{day}</p>
                      <div className={`p-2 sm:p-3 rounded-lg text-xs sm:text-sm ${
                        idx < 5 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        {idx < 5 ? '9-5' : 'Off'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Response Time */}
              <div className="bg-blue-50 rounded-xl p-4 sm:p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 text-sm sm:text-base">Average Response Time</h4>
                    <p className="text-gray-600 text-sm mt-1">Usually responds within 24 hours</p>
                  </div>
                  <Clock className="w-6 h-6 sm:w-8 sm:h-8 text-blue-600 ml-4" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions - Responsive */}
        <div className="bg-gray-50 p-3 sm:p-4 rounded-b-2xl flex-shrink-0">
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
            <button
              onClick={() => onSchedule && onSchedule(clinician)}
              className="flex-1 px-4 sm:px-6 py-2.5 sm:py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-all font-medium flex items-center justify-center space-x-2 text-sm sm:text-base"
            >
              <Calendar className="w-4 h-4 sm:w-5 sm:h-5" />
              <span>Book Appointment</span>
            </button>
            <button
              onClick={() => onContact && onContact(clinician)}
              className="flex-1 px-4 sm:px-6 py-2.5 sm:py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all font-medium flex items-center justify-center space-x-2 text-sm sm:text-base"
            >
              <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5" />
              <span>Send Message</span>
            </button>
            <button
              className="sm:flex-initial px-4 sm:px-6 py-2.5 sm:py-3 bg-white text-gray-700 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors font-medium flex items-center justify-center space-x-2 text-sm sm:text-base"
            >
              <Heart className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="sm:hidden">Save</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClinicianDetailModal;