// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

// Context
import { UserProvider, useUser } from './contexts/UserContext';

// Components
import Header from './components/common/Header';
import SearchForm from './components/search/SearchForm';
import ClinicianList from './components/clinicians/ClinicianList';
import ClinicianDetailModal from './components/clinicians/ClinicianDetailModal';
import LoginModal from './components/auth/LoginModal';
import ErrorMessage from './components/common/ErrorMessage';
import HowItWorks from './components/sections/HowItWorks';

// Icons
import { Shield, Zap, Heart, ArrowRight, Sparkles } from 'lucide-react';

// Services - Updated import
import { matchingAPI, interactionAPI, healthCheck, getUIConfig } from './services/api';

// Logo
import LogoWhite from './assets/images/logo/lunajoy-logo-white.png';

// Counter Animation Component
function AnimatedCounter({ end, duration = 2000, prefix = '', suffix = '' }) {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime = null;
    const startValue = 0;
    const endValue = parseFloat(end) || 0;
    
    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      const currentCount = Math.floor(progress * (endValue - startValue) + startValue);
      setCount(currentCount);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [end, duration]);
  
  return <span>{prefix}{count.toLocaleString()}{suffix}</span>;
}

// Main App Component (wrapped with UserProvider)
function AppContent() {
  // State management
  const [currentView, setCurrentView] = useState('home'); // 'home', 'how-it-works', 'search-results'
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedClinician, setSelectedClinician] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [searchParams, setSearchParams] = useState({});
  const [apiHealth, setApiHealth] = useState(null);
  const [matchStats, setMatchStats] = useState(null);
  
  const { user, isAuthenticated } = useUser();

  // Handle navigation from URL hash
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      if (hash === 'how-it-works') {
        setCurrentView('how-it-works');
      } else if (hash === 'home' || hash === '') {
        setCurrentView('home');
        setSearchResults(null);
      }
    };

    // Check initial hash
    handleHashChange();

    // Listen for hash changes
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  // Check API health and load UI config on mount
  useEffect(() => {
    checkApiHealth();
    fetchUIConfig();
  }, []);

  // Load last search on mount
  useEffect(() => {
    const lastSearch = localStorage.getItem('last_search');
    if (lastSearch) {
      try {
        const searchData = JSON.parse(lastSearch);
        setSearchParams(searchData);
      } catch (e) {
        console.error('Error loading last search:', e);
      }
    }
  }, []);

  const checkApiHealth = async () => {
    try {
      const health = await healthCheck();
      setApiHealth(health);
    } catch (err) {
      console.error('API health check failed:', err);
      setApiHealth({ status: 'error' });
    }
  };

  const fetchUIConfig = async () => {
    try {
      const config = await getUIConfig();
      setMatchStats(config.animated_stats);
    } catch (err) {
      console.error('Error fetching UI config:', err);
      // Will use default values from getUIConfig
    }
  };

  const handleSearch = async (formData) => {
    setLoading(true);
    setError(null);
    setSearchParams(formData);
    setCurrentView('search-results');

    try {
      let response;

      // Clean the form data based on appointment type
      const cleanedPreferences = {
        ...formData,
        clinical_needs: formData.appointment_type === 'medication' ? [] : formData.clinical_needs
      };

      // Add limit to get exactly 9 results
      const searchWithLimit = { ...cleanedPreferences, limit: 9 };

      // Choose the appropriate endpoint based on authentication status
      if (isAuthenticated && user) {
        if (user.registration_type === 'complete') {
          console.log('Using complete matching for user:', user.user_id);
          
          const profileData = {
            age_range: user.profile_data?.age_range || "25-34",
            therapy_experience: user.profile_data?.therapy_experience || "experienced",
            therapy_goals: user.profile_data?.therapy_goals || ["personal_growth", "manage_symptoms"]
          };
          
          if (!['first_time', 'some_experience', 'experienced'].includes(profileData.therapy_experience)) {
            profileData.therapy_experience = 'experienced';
          }
          
          response = await matchingAPI.matchComplete(
            user.user_id,
            searchWithLimit,
            profileData,
            true
          );
        } else if (user.registration_type === 'basic') {
          console.log('Using basic matching for user:', user.user_id);
          response = await matchingAPI.matchBasic(
            user.user_id,
            searchWithLimit,
            user.profile_data || {
              age_range: "25-34",
              therapy_experience: "first_time",
              therapy_goals: ["manage_symptoms"]
            }
          );
        } else {
          console.log('Using anonymous matching (fallback)');
          response = await matchingAPI.match(searchWithLimit);
        }
      } else {
        console.log('Using anonymous matching');
        response = await matchingAPI.match(searchWithLimit);
      }

      console.log('Search response:', response);
      setSearchResults(response);

      // Save search to localStorage
      localStorage.setItem('last_search', JSON.stringify(formData));

      // Refresh stats after search
      fetchUIConfig();
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'Unable to find matches. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewClinician = async (clinician) => {
    setSelectedClinician(clinician);
    setShowDetailModal(true);

    // Track view if user is authenticated
    if (isAuthenticated && user) {
      try {
        await interactionAPI.trackView(
          user.user_id,
          clinician.clinician_id,
          'match_result'
        );
      } catch (err) {
        console.error('Error tracking view:', err);
      }
    }
  };

  const handleContactClinician = async (clinician) => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
    } else {
      try {
        await interactionAPI.trackContact(user.user_id, clinician.clinician_id);
        alert(`✅ You've contacted ${clinician.clinician_name}. They'll reach out within 24 hours.`);
      } catch (err) {
        alert(`Connecting you with ${clinician.clinician_name}...`);
      }
    }
  };

  const handleScheduleClinician = async (clinician) => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
    } else {
      try {
        await interactionAPI.trackBooking(user.user_id, clinician.clinician_id);
        alert(`📅 Appointment scheduled with ${clinician.clinician_name}. Check your email for confirmation.`);
      } catch (err) {
        alert(`Opening scheduler for ${clinician.clinician_name}...`);
      }
    }
  };

  const handleSaveClinician = (clinician) => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
    } else {
      const savedClinicians = JSON.parse(localStorage.getItem('saved_clinicians') || '[]');
      const alreadySaved = savedClinicians.find(c => c.clinician_id === clinician.clinician_id);
      
      if (alreadySaved) {
        const filtered = savedClinicians.filter(c => c.clinician_id !== clinician.clinician_id);
        localStorage.setItem('saved_clinicians', JSON.stringify(filtered));
      } else {
        savedClinicians.push(clinician);
        localStorage.setItem('saved_clinicians', JSON.stringify(savedClinicians));
      }
    }
  };

  const handleNewSearch = () => {
    setSearchResults(null);
    setError(null);
    setCurrentView('home');
    window.location.hash = '#home';
  };

  const navigateToHome = () => {
    setCurrentView('home');
    setSearchResults(null);
    window.location.hash = '#home';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onLoginClick={() => setShowLoginModal(true)} />

      {/* API Health Warning */}
      {apiHealth?.status === 'error' && (
        <div className="bg-amber-50 border-b border-amber-200">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <ErrorMessage
              message={`Connection issue detected. Backend URL: ${process.env.REACT_APP_API_URL || 'http://localhost:8000'}`}
              type="warning"
            />
          </div>
        </div>
      )}

      {/* Main Content - Conditional Rendering based on currentView */}
      <main className="pt-20">
        {/* HOME VIEW */}
        {currentView === 'home' && (
          <>
            {/* Hero Section */}
            <section className="relative bg-gradient-to-b from-forest-700 to-forest-800 overflow-hidden">
              <div className="relative max-w-7xl mx-auto px-4 py-20 lg:py-32">
                <div className="text-center max-w-4xl mx-auto">
                  <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-bold text-white mb-6 animate-fade-in-up">
                    Your journey to wellness starts with the right match
                  </h1>
                  <p className="text-xl text-gray-200 mb-12 animate-fade-in-up animation-delay-200">
                    Connect with licensed mental health professionals who understand your unique needs
                  </p>

                  {/* Stats Row with Animation */}
                  {matchStats && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12 animate-fade-in-up animation-delay-400">
                      <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                        <p className="text-3xl font-bold text-white">
                          <AnimatedCounter end={matchStats.active_professionals} suffix="+" />
                        </p>
                        <p className="text-gray-200 text-sm">Verified Professionals</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                        <p className="text-3xl font-bold text-white">
                          <AnimatedCounter end={matchStats.total_matches} />
                        </p>
                        <p className="text-gray-200 text-sm">Successful Matches</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                        <p className="text-3xl font-bold text-white">
                          <AnimatedCounter end={matchStats.success_rate} suffix="%" />
                        </p>
                        <p className="text-gray-200 text-sm">Satisfaction Rate</p>
                      </div>
                      <div className="bg-white/10 backdrop-blur rounded-xl p-4">
                        <p className="text-3xl font-bold text-white">
                          <AnimatedCounter end={matchStats.states_covered} />
                        </p>
                        <p className="text-gray-200 text-sm">States Covered</p>
                      </div>
                    </div>
                  )}

                  <button
                    onClick={() => document.getElementById('search-section').scrollIntoView({ behavior: 'smooth' })}
                    className="bg-white text-forest-700 px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-100 transition-all transform hover:scale-105 shadow-xl animate-fade-in-up animation-delay-600 inline-flex items-center space-x-2"
                  >
                    <span>Start Your Journey</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </section>

            {/* Search Section */}
            <section id="search-section" className="py-16 lg:py-24">
              <div className="max-w-4xl mx-auto px-4">
                <div className="bg-white rounded-3xl shadow-lg p-8 lg:p-12 animate-scale-in">
                  <SearchForm
                    onSearch={handleSearch}
                    initialValues={searchParams}
                    loading={loading}
                  />
                </div>

                {/* Trust Features */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
                  <div className="text-center animate-fade-in-up">
                    <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Shield className="w-8 h-8 text-blue-600" />
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">Verified Professionals</h3>
                    <p className="text-gray-600 text-sm">All providers are licensed and background-checked</p>
                  </div>
                  <div className="text-center animate-fade-in-up animation-delay-200">
                    <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Zap className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">Quick Matching</h3>
                    <p className="text-gray-600 text-sm">Get matched in under 60 seconds</p>
                  </div>
                  <div className="text-center animate-fade-in-up animation-delay-400">
                    <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Heart className="w-8 h-8 text-purple-600" />
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-2">Personalized Care</h3>
                    <p className="text-gray-600 text-sm">Matches based on your unique needs</p>
                  </div>
                </div>
              </div>
            </section>
          </>
        )}

        {/* HOW IT WORKS VIEW */}
        {currentView === 'how-it-works' && (
          <div className="animate-fade-in">
            <HowItWorks />
            {/* Back to Home Button */}
            <div className="text-center pb-12">
              <button
                onClick={navigateToHome}
                className="text-forest-600 hover:text-forest-700 font-medium inline-flex items-center space-x-2 group"
              >
                <ArrowRight className="w-5 h-5 transform rotate-180 group-hover:-translate-x-1 transition-transform" />
                <span>Back to Home</span>
              </button>
            </div>
          </div>
        )}

        {/* SEARCH RESULTS VIEW */}
        {currentView === 'search-results' && searchResults && (
          <section className="py-8 animate-fade-in">
            <div className="max-w-7xl mx-auto px-4">
              {/* Back Button */}
              <div className="mb-8">
                <button
                  onClick={handleNewSearch}
                  className="text-gray-700 hover:text-gray-900 font-medium flex items-center space-x-2 group"
                >
                  <ArrowRight className="w-5 h-5 transform rotate-180 group-hover:-translate-x-1 transition-transform" />
                  <span>New Search</span>
                </button>
              </div>

              {/* Results */}
              <ClinicianList
                clinicians={searchResults.matches}
                loading={loading}
                error={error}
                searchInfo={searchResults}
                searchParams={searchParams}
                onViewClinician={handleViewClinician}
                onContactClinician={handleContactClinician}
                onSaveClinician={handleSaveClinician}
              />

              {/* CTA for non-authenticated users */}
              {!isAuthenticated && searchResults.matches && searchResults.matches.length > 0 && (
                <div className="mt-16 p-8 lg:p-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-3xl text-white text-center shadow-xl">
                  <Sparkles className="w-16 h-16 mx-auto mb-6 text-yellow-400" />
                  <h3 className="text-3xl font-display font-bold mb-4">
                    Unlock Your Perfect Match
                  </h3>
                  <p className="text-lg text-blue-100 max-w-2xl mx-auto mb-8">
                    Sign in to get personalized recommendations based on your unique profile and save your favorite professionals
                  </p>
                  <button
                    onClick={() => setShowLoginModal(true)}
                    className="bg-white text-blue-700 px-8 py-4 rounded-full hover:bg-gray-100 transition-all font-semibold text-lg transform hover:scale-105 shadow-lg inline-flex items-center space-x-2"
                  >
                    <span>Sign In Now</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12 mt-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="mb-4">
                <img
                  src={LogoWhite}
                  alt="LunaJoy"
                  className="h-10 w-auto"
                />
              </div>
              <p className="text-gray-400 text-sm">Your journey to wellness starts here.</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#about" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a></li>
                <li><a href="#for-providers" className="hover:text-white transition-colors">For Providers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#help" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#contact" className="hover:text-white transition-colors">Contact Us</a></li>
                <li><a href="#privacy" className="hover:text-white transition-colors">Privacy Policy</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Stay Connected</h4>
              <p className="text-gray-400 text-sm mb-4">Get wellness tips and updates</p>
              <div className="flex space-x-4">
                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors cursor-pointer">
                  <span>📧</span>
                </div>
                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors cursor-pointer">
                  <span>💬</span>
                </div>
                <div className="w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center hover:bg-gray-600 transition-colors cursor-pointer">
                  <span>📱</span>
                </div>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400 text-sm">
            <p>&copy; 2025 LunaJoy. All rights reserved. Made with 💚 for your mental health.</p>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <ClinicianDetailModal
        clinician={selectedClinician}
        isOpen={showDetailModal}
        onClose={() => setShowDetailModal(false)}
        onContact={handleContactClinician}
        onSchedule={handleScheduleClinician}
      />

      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
      />
    </div>
  );
}

// Main App with Provider
function App() {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

export default App;