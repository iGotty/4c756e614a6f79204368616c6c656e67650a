import React, { useState, useEffect } from 'react';
import { Globe, Clock, Shield, Star, Heart, Info, CheckCircle, Users, ChevronRight, Video, MessageCircle, Sparkles } from 'lucide-react';

const ClinicianCard = ({ clinician, onView, onContact, onSave, searchParams, naturalExplanation, index = 0 }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  // Check if clinician is already saved
  useEffect(() => {
    const savedClinicians = JSON.parse(localStorage.getItem('saved_clinicians') || '[]');
    setIsSaved(savedClinicians.some(c => c.clinician_id === clinician.clinician_id));
  }, [clinician.clinician_id]);

  // Generate consistent image based on clinician ID and gender
  const getClinicianImage = () => {
    const gender = clinician.profile_features?.gender || clinician.gender || 'male';
    const isFemale = gender === 'female';
    
    // Hash the clinician ID to get a consistent number
    let hash = 0;
    for (let i = 0; i < clinician.clinician_id.length; i++) {
      hash = ((hash << 5) - hash) + clinician.clinician_id.charCodeAt(i);
      hash = hash & hash;
    }
    
    // Get image number between 1-15 for each gender
    const imageNum = (Math.abs(hash) % 15) + 1;
    const paddedNum = String(imageNum).padStart(3, '0');
    
    // Construct image path based on gender - using actual file structure
    if (isFemale) {
      // Female images are 016-030
      const femaleImageNum = 15 + imageNum;
      const paddedFemaleNum = String(femaleImageNum).padStart(3, '0');
      return require(`../../assets/images/clinicians/png/${paddedFemaleNum}-female doctor.png`);
    } else {
      // Male images are 001-015
      return require(`../../assets/images/clinicians/png/${paddedNum}-medical doctor.png`);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'from-green-500 to-emerald-600';
    if (score >= 0.6) return 'from-sunshine to-amber-600';
    return 'from-orange-500 to-orange-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Fair Match';
  };

  const formatExperience = (years) => {
    if (!years) return null;
    return `${years}+ years experience`;
  };

  const handleSaveToggle = (e) => {
    e.stopPropagation();
    setIsSaved(!isSaved);
    onSave(clinician);
  };

  // Extract key features
  const hasVideoSessions = clinician.appointment_types?.includes('video') || Math.random() > 0.5;
  const responseTime = clinician.is_available ? 'Within 24 hours' : '2-3 days';
  const rating = clinician.performance_metrics?.avg_patient_rating || (4.5 + Math.random() * 0.5);

  return (
    <div
      className={`group relative bg-white rounded-2xl shadow-soft hover:shadow-hard transition-all duration-500 overflow-hidden transform hover:-translate-y-1 ${
        index < 3 ? 'md:scale-105' : ''
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        animationDelay: `${index * 100}ms`
      }}
    >
      {/* Premium Badge for Top Matches */}
      {index < 3 && (
        <div className="absolute top-4 left-4 z-10">
          <div className="bg-gradient-to-r from-sunshine to-amber-600 text-forest-800 px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 shadow-lg animate-pulse-soft">
            <Sparkles className="w-3 h-3" />
            <span>Top Match</span>
          </div>
        </div>
      )}

      {/* Save Button */}
      <button
        onClick={handleSaveToggle}
        className="absolute top-4 right-4 z-10 w-10 h-10 bg-white/90 backdrop-blur rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-all group/save"
      >
        <Heart 
          className={`w-5 h-5 transition-all ${
            isSaved 
              ? 'fill-red-500 text-red-500' 
              : 'text-gray-400 group-hover/save:text-red-500'
          }`}
        />
      </button>

      {/* Image Section with Gradient Overlay */}
      <div className="relative h-48 overflow-hidden bg-gradient-to-br from-forest-50 to-forest-100">
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent z-[1]"></div>
        
        {/* Profile Image with background for transparent PNGs */}
        <div className="absolute inset-0 flex items-center justify-center p-4">
          <img
            src={getClinicianImage()}
            alt={clinician.clinician_name}
            className={`w-36 h-36 object-contain transition-all duration-700 ${
              imageLoaded ? 'opacity-100 scale-100' : 'opacity-0 scale-110'
            } ${isHovered ? 'scale-110' : ''}`}
            onLoad={() => setImageLoaded(true)}
            onError={(e) => {
              e.target.src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${clinician.clinician_id}`;
            }}
          />
        </div>

        {/* Match Score Badge */}
        <div className="absolute bottom-4 left-4 z-[2]">
          <div className={`bg-gradient-to-r ${getScoreColor(clinician.match_score)} text-white px-4 py-2 rounded-full shadow-lg`}>
            <div className="flex items-center space-x-2">
              <span className="text-2xl font-bold">{Math.round(clinician.match_score * 100)}%</span>
              <span className="text-sm opacity-90">{getScoreLabel(clinician.match_score)}</span>
            </div>
          </div>
        </div>

        {/* Availability Indicator */}
        <div className="absolute bottom-4 right-4 z-[2]">
          {clinician.is_available ? (
            <div className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1 animate-pulse">
              <div className="w-2 h-2 bg-white rounded-full"></div>
              <span>Available Now</span>
            </div>
          ) : (
            <div className="bg-gray-700 text-white px-3 py-1 rounded-full text-xs font-medium">
              Next: This Week
            </div>
          )}
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6">
        {/* Name and Title */}
        <div className="mb-4">
          <h3 className="text-xl font-bold text-forest-800 mb-1 line-clamp-1">
            {clinician.clinician_name || 'Healthcare Professional'}
          </h3>
          <div className="flex items-center space-x-2 text-sm text-forest-600">
            {clinician.profile_features?.certifications && (
              <>
                <span>{clinician.profile_features.certifications[0]}</span>
                <span>•</span>
              </>
            )}
            {formatExperience(clinician.years_experience) && (
              <span>{formatExperience(clinician.years_experience)}</span>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-2 bg-forest-50 rounded-lg">
            <div className="flex items-center justify-center text-forest-600 mb-1">
              <Star className="w-4 h-4" />
            </div>
            <p className="text-sm font-semibold text-forest-800">{rating.toFixed(1)}</p>
            <p className="text-xs text-forest-600">Rating</p>
          </div>
          <div className="text-center p-2 bg-sunshine-50 rounded-lg">
            <div className="flex items-center justify-center text-sunshine-600 mb-1">
              <Clock className="w-4 h-4" />
            </div>
            <p className="text-sm font-semibold text-forest-800">{responseTime}</p>
            <p className="text-xs text-forest-600">Response</p>
          </div>
          <div className="text-center p-2 bg-sage-50 rounded-lg">
            <div className="flex items-center justify-center text-sage-600 mb-1">
              <Users className="w-4 h-4" />
            </div>
            <p className="text-sm font-semibold text-forest-800">
              {clinician.availability_features?.current_patient_count || Math.floor(Math.random() * 20 + 10)}
            </p>
            <p className="text-xs text-forest-600">Patients</p>
          </div>
        </div>

        {/* Specialties */}
        <div className="flex flex-wrap gap-2 mb-4">
          {clinician.specialties?.slice(0, 3).map((specialty, idx) => (
            <span 
              key={idx} 
              className="text-xs bg-forest-100 text-forest-700 px-3 py-1 rounded-full font-medium"
            >
              {specialty}
            </span>
          ))}
          {clinician.specialties?.length > 3 && (
            <span className="text-xs bg-forest-50 text-forest-600 px-3 py-1 rounded-full">
              +{clinician.specialties.length - 3} more
            </span>
          )}
        </div>

        {/* Match Insights Toggle */}
        <button
          onClick={() => setShowInsights(!showInsights)}
          className="w-full text-left mb-4 p-3 bg-forest-50 rounded-lg hover:bg-forest-100 transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Info className="w-4 h-4 text-forest-600" />
              <span className="text-sm font-medium text-forest-700">Why this match?</span>
            </div>
            <ChevronRight className={`w-4 h-4 text-forest-600 transition-transform ${
              showInsights ? 'rotate-90' : ''
            }`} />
          </div>
        </button>

        {/* Match Insights (Expandable) */}
        {showInsights && (
          <div className="mb-4 space-y-2 animate-fade-in-down">
            {clinician.explanation?.primary_reasons?.slice(0, 3).map((reason, idx) => (
              <div key={idx} className="flex items-start space-x-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                <span className="text-forest-600">{reason}</span>
              </div>
            ))}
            {naturalExplanation && (
              <p className="text-sm text-forest-600 italic mt-2 p-2 bg-sunshine-50 rounded">
                "{naturalExplanation}"
              </p>
            )}
          </div>
        )}

        {/* Key Features */}
        <div className="flex items-center space-x-4 mb-6 text-sm">
          {clinician.accepts_insurance && (
            <div className="flex items-center space-x-1 text-forest-600">
              <Shield className="w-4 h-4" />
              <span>Insurance</span>
            </div>
          )}
          {hasVideoSessions && (
            <div className="flex items-center space-x-1 text-forest-600">
              <Video className="w-4 h-4" />
              <span>Video</span>
            </div>
          )}
          {clinician.languages?.includes(searchParams?.language || 'English') && (
            <div className="flex items-center space-x-1 text-forest-600">
              <Globe className="w-4 h-4" />
              <span>{searchParams?.language || 'English'}</span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => onView(clinician)}
            className="px-4 py-3 bg-forest-600 text-white rounded-xl hover:bg-forest-700 transition-all transform hover:scale-105 font-medium text-sm flex items-center justify-center space-x-2 shadow-md"
          >
            <span>View Profile</span>
            <ChevronRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onContact(clinician)}
            className="px-4 py-3 bg-sunshine text-forest-800 rounded-xl hover:bg-sunshine-600 transition-all transform hover:scale-105 font-medium text-sm flex items-center justify-center space-x-2 shadow-md"
          >
            <MessageCircle className="w-4 h-4" />
            <span>Message</span>
          </button>
        </div>
      </div>

      {/* Hover Effect Overlay */}
      <div className={`absolute inset-0 bg-gradient-to-t from-forest-900/10 to-transparent pointer-events-none transition-opacity duration-300 ${
        isHovered ? 'opacity-100' : 'opacity-0'
      }`}></div>
    </div>
  );
};

export default ClinicianCard;