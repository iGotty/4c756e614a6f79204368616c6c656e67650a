import React, { useState, useEffect } from 'react';
import { Search, MapPin, Heart, Shield, Clock, Sparkles, ChevronRight, AlertCircle } from 'lucide-react';
import {
  STATES,
  LANGUAGES,
  INSURANCE_PROVIDERS,
  CLINICAL_NEEDS,
  TIME_SLOTS,
  GENDER_PREFERENCES,
  APPOINTMENT_TYPES,
  URGENCY_LEVELS
} from '../../utils/constants';

const SearchForm = ({ onSearch, initialValues = {}, loading = false }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    state: '',
    appointment_type: 'therapy',
    insurance_provider: '',
    language: 'English',
    gender_preference: '',
    clinical_needs: [],
    preferred_time_slots: [],
    urgency_level: 'flexible',
    ...initialValues
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  // Animation states
  const [isAnimating, setIsAnimating] = useState(false);

  // Update form when initialValues change
  useEffect(() => {
    setFormData(prev => ({ ...prev, ...initialValues }));
  }, [initialValues]);

  const steps = [
    { id: 'location', title: 'Your Location', icon: MapPin, required: true },
    { id: 'appointment', title: 'Appointment Type', icon: Heart, required: true },
    { id: 'insurance', title: 'Insurance', icon: Shield, required: true },
    { id: 'preferences', title: 'Preferences', icon: Sparkles, required: false },
    { id: 'timing', title: 'Availability', icon: Clock, required: false }
  ];

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setTouched(prev => ({ ...prev, [field]: true }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const toggleArrayField = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(item => item !== value)
        : [...prev[field], value]
    }));
  };

  const validateStep = (stepIndex) => {
    const newErrors = {};
    
    switch (stepIndex) {
      case 0: // Location
        if (!formData.state) {
          newErrors.state = 'Please select your state';
        }
        break;
      case 1: // Appointment Type
        if (!formData.appointment_type) {
          newErrors.appointment_type = 'Please select appointment type';
        }
        break;
      case 2: // Insurance
        if (!formData.insurance_provider) {
          newErrors.insurance_provider = 'Please select your insurance provider';
        }
        break;
      default:
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
        setIsAnimating(false);
      }, 300);
    }
  };

  const handlePrev = () => {
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentStep(prev => Math.max(prev - 1, 0));
      setIsAnimating(false);
    }, 300);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate all required steps
    let hasErrors = false;
    for (let i = 0; i <= 2; i++) {
      if (!validateStep(i)) {
        hasErrors = true;
        setCurrentStep(i);
        break;
      }
    }
    
    if (!hasErrors) {
      const cleanedData = {
        ...formData,
        clinical_needs: formData.appointment_type === 'medication' ? [] : formData.clinical_needs,
        // Remove language if it's just English (default)
        language: formData.language === 'English' ? '' : formData.language
      };
      onSearch(cleanedData);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Location
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-10 h-10 text-blue-600" />
              </div>
              <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">
                Where are you located?
              </h3>
              <p className="text-gray-600">
                We'll match you with licensed professionals in your state
              </p>
            </div>
            
            <div className="relative">
              <select
                value={formData.state}
                onChange={(e) => handleChange('state', e.target.value)}
                className={`w-full px-6 py-4 text-lg border-2 rounded-2xl focus:outline-none focus:ring-4 transition-all appearance-none bg-white ${
                  errors.state && touched.state
                    ? 'border-red-300 focus:ring-red-100'
                    : 'border-gray-300 focus:ring-blue-100 focus:border-blue-500'
                }`}
              >
                <option value="">Select your state</option>
                {STATES.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
              <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none rotate-90" />
            </div>
            
            {errors.state && touched.state && (
              <p className="mt-2 text-sm text-red-600 flex items-center animate-fade-in">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.state}
              </p>
            )}
          </div>
        );

      case 1: // Appointment Type
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="w-10 h-10 text-purple-600" />
              </div>
              <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">
                What type of support do you need?
              </h3>
              <p className="text-gray-600">
                Choose the type of care that best fits your needs
              </p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {APPOINTMENT_TYPES.map(type => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => handleChange('appointment_type', type.value)}
                  className={`p-6 rounded-2xl border-2 transition-all transform hover:scale-105 ${
                    formData.appointment_type === type.value
                      ? 'border-purple-500 bg-purple-50 shadow-lg'
                      : 'border-gray-300 hover:border-gray-400 bg-white'
                  }`}
                >
                  <div className={`text-3xl mb-3`}>
                    {type.value === 'therapy' ? '💬' : '💊'}
                  </div>
                  <h4 className="font-semibold text-lg text-gray-900">{type.label}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {type.value === 'therapy' 
                      ? 'Talk therapy and counseling'
                      : 'Psychiatric medication management'}
                  </p>
                </button>
              ))}
            </div>
          </div>
        );

      case 2: // Insurance
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-10 h-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">
                Your insurance provider
              </h3>
              <p className="text-gray-600">
                We'll find professionals who accept your insurance
              </p>
            </div>
            
            <div className="relative">
              <select
                value={formData.insurance_provider}
                onChange={(e) => handleChange('insurance_provider', e.target.value)}
                className={`w-full px-6 py-4 text-lg border-2 rounded-2xl focus:outline-none focus:ring-4 transition-all appearance-none bg-white ${
                  errors.insurance_provider && touched.insurance_provider
                    ? 'border-red-300 focus:ring-red-100'
                    : 'border-gray-300 focus:ring-green-100 focus:border-green-500'
                }`}
              >
                <option value="">Select your insurance</option>
                {INSURANCE_PROVIDERS.map(provider => (
                  <option key={provider} value={provider}>{provider}</option>
                ))}
              </select>
              <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none rotate-90" />
            </div>
            
            {errors.insurance_provider && touched.insurance_provider && (
              <p className="mt-2 text-sm text-red-600 flex items-center animate-fade-in">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors.insurance_provider}
              </p>
            )}
          </div>
        );

      case 3: // Preferences
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-10 h-10 text-amber-600" />
              </div>
              <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">
                Your preferences (optional)
              </h3>
              <p className="text-gray-600">
                Help us find the perfect match for you
              </p>
            </div>

            {/* Language Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Preferred language
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => handleChange('language', '')}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    formData.language === ''
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  No preference
                </button>
                {LANGUAGES.slice(0, 5).map(lang => (
                  <button
                    key={lang}
                    type="button"
                    onClick={() => handleChange('language', lang)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      formData.language === lang
                        ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {lang}
                  </button>
                ))}
              </div>
            </div>

            {/* Gender Preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Professional's gender preference
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {GENDER_PREFERENCES.map(pref => (
                  <button
                    key={pref.value}
                    type="button"
                    onClick={() => handleChange('gender_preference', pref.value)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      formData.gender_preference === pref.value
                        ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {pref.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Clinical Needs */}
            {formData.appointment_type === 'therapy' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  What would you like to work on?
                </label>
                <div className="flex flex-wrap gap-2">
                  {CLINICAL_NEEDS.map(need => (
                    <button
                      key={need}
                      type="button"
                      onClick={() => toggleArrayField('clinical_needs', need)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                        formData.clinical_needs.includes(need)
                          ? 'bg-purple-600 text-white shadow-md transform scale-105'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {need.replace(/_/g, ' ')}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 4: // Timing
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-10 h-10 text-indigo-600" />
              </div>
              <h3 className="text-2xl font-display font-bold text-gray-900 mb-2">
                When do you need care?
              </h3>
              <p className="text-gray-600">
                Let us know your urgency and preferred times
              </p>
            </div>

            {/* Urgency Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                How urgent is your need?
              </label>
              <div className="grid grid-cols-2 gap-4">
                {URGENCY_LEVELS.map(level => (
                  <button
                    key={level.value}
                    type="button"
                    onClick={() => handleChange('urgency_level', level.value)}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.urgency_level === level.value
                        ? 'border-indigo-500 bg-indigo-50 shadow-lg'
                        : 'border-gray-300 hover:border-gray-400 bg-white'
                    }`}
                  >
                    <div className="text-2xl mb-2">
                      {level.value === 'immediate' ? '🚨' : '📅'}
                    </div>
                    <h4 className="font-semibold text-gray-900">{level.label}</h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {level.value === 'immediate' 
                        ? 'Need help within 24-72 hours'
                        : 'Can wait for the right match'}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Time Slots */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Preferred appointment times
              </label>
              <div className="grid grid-cols-2 gap-3">
                {TIME_SLOTS.map(slot => (
                  <button
                    key={slot}
                    type="button"
                    onClick={() => toggleArrayField('preferred_time_slots', slot)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center justify-center space-x-2 ${
                      formData.preferred_time_slots.includes(slot)
                        ? 'bg-indigo-600 text-white shadow-lg transform scale-105'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <span>
                      {slot === 'morning' ? '🌅' :
                       slot === 'afternoon' ? '☀️' :
                       slot === 'evening' ? '🌙' : '📅'}
                    </span>
                    <span>
                      {slot === 'morning' ? 'Mornings' :
                       slot === 'afternoon' ? 'Afternoons' :
                       slot === 'evening' ? 'Evenings' : 'Weekends'}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${
                index < steps.length - 1 ? 'flex-1' : ''
              }`}
            >
              <div
                className={`relative w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                  index <= currentStep
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-400'
                }`}
              >
                <step.icon className="w-5 h-5" />
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 rounded transition-all ${
                    index < currentStep
                      ? 'bg-blue-600'
                      : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Step {currentStep + 1} of {steps.length}: {steps[currentStep].title}
          </p>
        </div>
      </div>

      {/* Step Content */}
      <div className={`transition-all duration-300 ${isAnimating ? 'opacity-0 transform translate-x-4' : 'opacity-100 transform translate-x-0'}`}>
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center mt-12">
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={handlePrev}
            disabled={currentStep === 0}
            className={`px-6 py-3 rounded-full font-medium transition-all ${
              currentStep === 0
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300 transform hover:scale-105'
            }`}
          >
            Previous
          </button>

          {/* Skip Button for Optional Steps */}
          {currentStep >= 3 && (
            <button
              type="submit"
              className="px-6 py-3 bg-gray-500 text-white rounded-full font-medium hover:bg-gray-600 transition-all transform hover:scale-105"
            >
              Skip & Search
            </button>
          )}
        </div>

        {currentStep < steps.length - 1 ? (
          <button
            type="button"
            onClick={handleNext}
            className="px-8 py-3 bg-blue-600 text-white rounded-full font-medium hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg flex items-center space-x-2"
          >
            <span>Continue</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3 bg-green-600 text-white rounded-full font-medium hover:bg-green-700 transition-all transform hover:scale-105 shadow-lg flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Finding matches...</span>
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                <span>Find My Match</span>
              </>
            )}
          </button>
        )}
      </div>
    </form>
  );
};

export default SearchForm;