import React, { useState, useEffect, useRef } from 'react';
import { 
  Brain, Shield, Zap, Heart, ArrowRight, Check, 
  Users, Search, Sparkles, Lock, Award, 
  TrendingUp, Activity, ChevronRight, Play, Pause,
  Database, Cpu, GitBranch, BarChart3
} from 'lucide-react';

const HowItWorks = () => {
  const [activeTab, setActiveTab] = useState('patient');
  const [activeStep, setActiveStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const sectionRef = useRef(null);

  // Auto-play steps
  useEffect(() => {
    if (isPlaying && activeStep < 3) {
      const timer = setTimeout(() => {
        setActiveStep((prev) => (prev + 1) % 4);
      }, 3000);
      return () => clearTimeout(timer);
    } else if (isPlaying && activeStep === 3) {
      setIsPlaying(false);
    }
  }, [isPlaying, activeStep]);

  // Scroll animations
  useEffect(() => {
    const handleScroll = () => {
      if (sectionRef.current) {
        const rect = sectionRef.current.getBoundingClientRect();
        const progress = Math.max(0, Math.min(1, -rect.top / rect.height));
        setScrollProgress(progress);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const patientSteps = [
    {
      icon: Search,
      title: "Share Your Needs",
      description: "Tell us about your mental health goals, preferences, and what you're looking for in a therapist",
      details: [
        "Location and availability preferences",
        "Insurance and budget considerations",
        "Specific areas you want to work on",
        "Therapist gender and language preferences"
      ],
      color: "blue"
    },
    {
      icon: Brain,
      title: "AI-Powered Matching",
      description: "Our intelligent system analyzes your needs across multiple dimensions to find your perfect match",
      details: [
        "3-tier matching strategy based on your profile",
        "70,000+ successful matches analyzed",
        "Real-time availability checking",
        "Multi-criteria scoring system"
      ],
      color: "purple"
    },
    {
      icon: Users,
      title: "Review Your Matches",
      description: "Get a curated list of professionals perfectly suited to your needs, with clear explanations",
      details: [
        "Top 9 personalized matches",
        "Match scores and explanations",
        "Verified credentials and ratings",
        "Direct booking availability"
      ],
      color: "green"
    },
    {
      icon: Heart,
      title: "Start Your Journey",
      description: "Book your first appointment and begin your path to better mental health",
      details: [
        "Easy online scheduling",
        "Secure messaging with your therapist",
        "Flexible session options (video/phone)",
        "Ongoing support and care"
      ],
      color: "red"
    }
  ];

  const techSpecs = [
    {
      icon: Zap,
      title: "Lightning Fast",
      stat: "<2ms",
      description: "Average response time"
    },
    {
      icon: Shield,
      title: "HIPAA Compliant",
      stat: "100%",
      description: "Secure & private"
    },
    {
      icon: Database,
      title: "Data Points",
      stat: "70K+",
      description: "Interactions analyzed"
    },
    {
      icon: TrendingUp,
      title: "Success Rate",
      stat: "92%",
      description: "Patient satisfaction"
    }
  ];

  const matchingStrategies = [
    {
      type: "Anonymous",
      title: "Content-Based Filtering",
      description: "Quick matches based on your stated preferences",
      features: ["State & insurance matching", "Specialty alignment", "Availability priority"],
      icon: "🌱"
    },
    {
      type: "Basic User",
      title: "Enhanced with Demographics",
      description: "Smarter matches using age and experience data",
      features: ["Demographic clustering", "Peer group analysis", "Experience matching"],
      icon: "🌿"
    },
    {
      type: "Premium User",
      title: "AI-Powered Predictions",
      description: "Predictive matching based on your history",
      features: ["Collaborative filtering", "Success prediction", "Behavioral learning"],
      icon: "🌳"
    }
  ];

  return (
    <section id="how-it-works" ref={sectionRef} className="py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center p-2 bg-forest-100 rounded-full mb-4">
            <Sparkles className="w-5 h-5 text-forest-600 mr-2" />
            <span className="text-sm font-medium text-forest-700">How LunaJoy Works</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-display font-bold text-gray-900 mb-4">
            Your Journey to Better Mental Health
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            We use advanced AI and a deep understanding of mental health to connect you with the right professional in under 60 seconds
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex justify-center mb-12">
          <div className="bg-gray-100 p-1 rounded-full inline-flex">
            <button
              onClick={() => setActiveTab('patient')}
              className={`px-6 py-3 rounded-full font-medium transition-all ${
                activeTab === 'patient' 
                  ? 'bg-white text-forest-700 shadow-md' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              For Patients
            </button>
            <button
              onClick={() => setActiveTab('technical')}
              className={`px-6 py-3 rounded-full font-medium transition-all ${
                activeTab === 'technical' 
                  ? 'bg-white text-forest-700 shadow-md' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              How It Works (Technical)
            </button>
          </div>
        </div>

        {/* Patient Journey */}
        {activeTab === 'patient' && (
          <div className="space-y-16">
            {/* Interactive Steps */}
            <div className="relative">
              {/* Progress Line */}
              <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-1 bg-gray-200 -translate-y-1/2">
                <div 
                  className="h-full bg-gradient-to-r from-forest-600 to-sunshine transition-all duration-1000"
                  style={{ width: `${(activeStep + 1) * 25}%` }}
                />
              </div>

              {/* Steps */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 relative">
                {patientSteps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index === activeStep;
                  const isPast = index < activeStep;
                  
                  return (
                    <div
                      key={index}
                      className={`relative cursor-pointer transition-all duration-500 ${
                        isActive ? 'scale-105' : 'scale-100'
                      }`}
                      onClick={() => setActiveStep(index)}
                    >
                      {/* Step Card */}
                      <div className={`bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all ${
                        isActive ? 'ring-2 ring-forest-500' : ''
                      }`}>
                        {/* Icon */}
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-all ${
                          isActive 
                            ? `bg-${step.color}-100` 
                            : isPast 
                            ? 'bg-green-100' 
                            : 'bg-gray-100'
                        }`}>
                          {isPast && !isActive ? (
                            <Check className="w-8 h-8 text-green-600" />
                          ) : (
                            <Icon className={`w-8 h-8 ${
                              isActive 
                                ? `text-${step.color}-600` 
                                : 'text-gray-400'
                            }`} />
                          )}
                        </div>

                        {/* Content */}
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {step.title}
                        </h3>
                        <p className="text-sm text-gray-600 mb-4">
                          {step.description}
                        </p>

                        {/* Details (shown when active) */}
                        <div className={`space-y-2 overflow-hidden transition-all duration-500 ${
                          isActive ? 'max-h-40 opacity-100' : 'max-h-0 opacity-0'
                        }`}>
                          {step.details.map((detail, idx) => (
                            <div key={idx} className="flex items-start">
                              <Check className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                              <span className="text-xs text-gray-700">{detail}</span>
                            </div>
                          ))}
                        </div>

                        {/* Step Number */}
                        <div className="absolute -top-3 -right-3 w-8 h-8 bg-forest-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Play/Pause Button */}
              <div className="flex justify-center mt-8">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="flex items-center space-x-2 px-6 py-3 bg-forest-600 text-white rounded-full hover:bg-forest-700 transition-all"
                >
                  {isPlaying ? (
                    <>
                      <Pause className="w-5 h-5" />
                      <span>Pause Demo</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Play Demo</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Trust Indicators */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {techSpecs.map((spec, index) => {
                const Icon = spec.icon;
                return (
                  <div 
                    key={index}
                    className="text-center p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-all"
                    style={{
                      transform: `translateY(${Math.max(0, (1 - scrollProgress) * 50)}px)`,
                      opacity: Math.min(1, scrollProgress * 2),
                      transitionDelay: `${index * 100}ms`
                    }}
                  >
                    <Icon className="w-8 h-8 text-forest-600 mx-auto mb-3" />
                    <div className="text-3xl font-bold text-gray-900 mb-1">{spec.stat}</div>
                    <div className="text-sm font-medium text-gray-700">{spec.title}</div>
                    <div className="text-xs text-gray-500">{spec.description}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Technical Details */}
        {activeTab === 'technical' && (
          <div className="space-y-16">
            {/* Matching Strategies */}
            <div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
                Progressive Matching System
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {matchingStrategies.map((strategy, index) => (
                  <div 
                    key={index}
                    className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1"
                  >
                    <div className="text-4xl mb-4">{strategy.icon}</div>
                    <div className="text-sm font-medium text-forest-600 mb-2">{strategy.type}</div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">{strategy.title}</h4>
                    <p className="text-sm text-gray-600 mb-4">{strategy.description}</p>
                    <div className="space-y-2">
                      {strategy.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-sm">
                          <ChevronRight className="w-4 h-4 text-forest-500 mr-2" />
                          <span className="text-gray-700">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Architecture Diagram */}
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">System Architecture</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Frontend */}
                <div className="text-center">
                  <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Activity className="w-10 h-10 text-blue-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">React Frontend</h4>
                  <p className="text-sm text-gray-600">
                    Modern UI with TypeScript, Tailwind CSS, and real-time updates
                  </p>
                </div>

                {/* API */}
                <div className="text-center">
                  <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <GitBranch className="w-10 h-10 text-purple-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">FastAPI Backend</h4>
                  <p className="text-sm text-gray-600">
                    High-performance Python API with async support and ML integration
                  </p>
                </div>

                {/* Data */}
                <div className="text-center">
                  <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Database className="w-10 h-10 text-green-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Smart Data Layer</h4>
                  <p className="text-sm text-gray-600">
                    In-memory caching, 70K+ interactions, real-time processing
                  </p>
                </div>
              </div>

              {/* Connection Lines */}
              <div className="flex justify-center items-center mt-8 space-x-4">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <div className="w-24 h-0.5 bg-gray-300"></div>
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <div className="w-24 h-0.5 bg-gray-300"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
              </div>
            </div>

            {/* ML Features */}
            <div className="bg-gradient-to-r from-forest-50 to-blue-50 rounded-2xl p-8">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">Advanced ML Features</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
                    <Brain className="w-6 h-6 text-forest-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">User Clustering</h4>
                    <p className="text-sm text-gray-600">8 demographic clusters for better personalization</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
                    <BarChart3 className="w-6 h-6 text-forest-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Collaborative Filtering</h4>
                    <p className="text-sm text-gray-600">Learn from 70K+ successful matches</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
                    <Cpu className="w-6 h-6 text-forest-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">Real-time Scoring</h4>
                    <p className="text-sm text-gray-600">Multi-criteria weighted scoring system</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
                    <Lock className="w-6 h-6 text-forest-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">HIPAA Compliant</h4>
                    <p className="text-sm text-gray-600">Secure, private, and regulation-ready</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CTA Section */}
        <div className="mt-20 text-center">
          <div className="bg-gradient-to-r from-forest-600 to-forest-700 rounded-3xl p-12 text-white">
            <Award className="w-16 h-16 mx-auto mb-6 text-sunshine" />
            <h3 className="text-3xl font-display font-bold mb-4">
              Ready to Find Your Perfect Match?
            </h3>
            <p className="text-lg text-forest-100 max-w-2xl mx-auto mb-8">
              Join thousands who have found their ideal mental health professional through our intelligent matching system
            </p>
            <button
              onClick={() => {
                // Navigate to home and then scroll to search
                window.location.hash = '#home';
                setTimeout(() => {
                  const searchSection = document.getElementById('search-section');
                  if (searchSection) {
                    searchSection.scrollIntoView({ behavior: 'smooth' });
                  }
                }, 100);
              }}
              className="bg-white text-forest-700 px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-100 transition-all transform hover:scale-105 shadow-lg inline-flex items-center space-x-2"
            >
              <span>Start Matching Now</span>
              <ArrowRight className="w-5 h-5" />
            </button>
            <p className="text-sm text-forest-200 mt-4">
              No credit card required • 100% confidential • Results in under 60 seconds
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;