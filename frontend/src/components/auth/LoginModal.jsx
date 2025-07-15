import React, { useState, useEffect } from 'react';
import { X, User, Info, Shield, Heart, Brain, ChevronRight, Check } from 'lucide-react';
import { useUser } from '../../contexts/UserContext';
import { EXAMPLE_USERS } from '../../utils/constants';
import ErrorMessage from '../common/ErrorMessage';

const LoginModal = ({ isOpen, onClose }) => {
  const { login } = useUser();
  const [userId, setUserId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showBenefits, setShowBenefits] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!userId.trim()) {
      setError('Please enter a user ID');
      return;
    }

    setError('');
    setLoading(true);

    const result = await login(userId.trim());
    
    if (result.success) {
      // Success animation before closing
      setTimeout(() => {
        setUserId('');
        setError('');
        onClose();
      }, 500);
    } else {
      setError(result.error || 'Unable to sign in. Please try again.');
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleId) => {
    setUserId(exampleId);
    setError('');
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !loading) {
      handleClose();
    }
  };

  const handleClose = () => {
    setUserId('');
    setError('');
    setShowBenefits(true);
    onClose();
  };

  if (!isOpen) return null;

  const benefits = [
    {
      icon: Brain,
      title: 'AI-Powered Matching',
      description: 'Get smarter recommendations based on your history'
    },
    {
      icon: Heart,
      title: 'Save Favorites',
      description: 'Build your dream team of healthcare providers'
    },
    {
      icon: Shield,
      title: 'Privacy Protected',
      description: 'Your data is encrypted and secure'
    }
  ];

  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className={`bg-white rounded-3xl max-w-4xl w-full shadow-2xl transform transition-all duration-500 ${
        isAnimating ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
      }`}>
        <div className="flex flex-col lg:flex-row">
          {/* Left Side - Benefits */}
          <div className={`lg:w-1/2 p-8 lg:p-12 bg-gradient-to-br from-forest-600 to-forest-700 rounded-t-3xl lg:rounded-l-3xl lg:rounded-tr-none transition-all duration-500 ${
            showBenefits ? 'opacity-100' : 'opacity-0 lg:opacity-100'
          }`}>
            <div className="text-white">
              <h3 className="text-3xl font-display font-bold mb-2">Welcome Back!</h3>
              <p className="text-forest-100 mb-8">
                Sign in to unlock personalized mental health matching
              </p>

              {/* Benefits List */}
              <div className="space-y-6">
                {benefits.map((benefit, idx) => {
                  const Icon = benefit.icon;
                  return (
                    <div 
                      key={idx} 
                      className="flex items-start space-x-4 animate-fade-in-up"
                      style={{ animationDelay: `${idx * 100}ms` }}
                    >
                      <div className="w-12 h-12 bg-white/20 backdrop-blur rounded-xl flex items-center justify-center flex-shrink-0">
                        <Icon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-white mb-1">{benefit.title}</h4>
                        <p className="text-forest-100 text-sm">{benefit.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Trust Badge */}
              <div className="mt-12 p-4 bg-white/10 backdrop-blur rounded-xl">
                <div className="flex items-center space-x-3">
                  <Shield className="w-8 h-8 text-sunshine" />
                  <div>
                    <p className="font-semibold text-white">HIPAA Compliant</p>
                    <p className="text-forest-100 text-sm">Your privacy is our priority</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Login Form */}
          <div className="lg:w-1/2 p-8 lg:p-12">
            {/* Close Button */}
            <button 
              onClick={handleClose}
              disabled={loading}
              className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
              aria-label="Close"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>

            {/* Form Header */}
            <div className="mb-8">
              <h2 className="text-2xl font-display font-bold text-forest-800 mb-2">Sign In</h2>
              <p className="text-forest-600">Enter your user ID to continue</p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* User ID Input */}
              <div>
                <label className="block text-sm font-medium text-forest-700 mb-2">
                  User ID
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-forest-400" />
                  </div>
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="e.g., user_01307_c530ad"
                    className="w-full pl-12 pr-4 py-3 border-2 border-forest-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-forest-100 focus:border-forest-400 transition-all text-lg"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="animate-fade-in">
                  <ErrorMessage message={error} type="error" />
                </div>
              )}

              {/* Example Users */}
              <div>
                <div className="flex items-center text-sm text-forest-600 mb-3">
                  <Info className="w-4 h-4 mr-2" />
                  <span>Demo accounts (click to use):</span>
                </div>
                <div className="space-y-3">
                  {EXAMPLE_USERS.map((example) => (
                    <button
                      key={example.id}
                      type="button"
                      onClick={() => handleExampleClick(example.id)}
                      className={`w-full text-left p-4 rounded-xl border-2 transition-all hover:shadow-md ${
                        userId === example.id 
                          ? 'border-forest-400 bg-forest-50' 
                          : 'border-forest-100 hover:border-forest-300 bg-white'
                      }`}
                      disabled={loading}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <code className="text-forest-600 font-mono font-medium">{example.id}</code>
                          <p className="text-sm text-forest-500 mt-1">{example.description}</p>
                        </div>
                        {userId === example.id && (
                          <Check className="w-5 h-5 text-forest-600 animate-scale-in" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !userId.trim()}
                className="w-full bg-sunshine text-forest-800 py-4 rounded-xl hover:bg-sunshine-600 transition-all font-medium text-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg transform hover:scale-105"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-forest-800 border-t-transparent rounded-full animate-spin"></div>
                    <span>Signing in...</span>
                  </>
                ) : (
                  <>
                    <span>Continue</span>
                    <ChevronRight className="w-5 h-5" />
                  </>
                )}
              </button>

              {/* Alternative Actions */}
              <div className="text-center pt-4 border-t border-forest-100">
                <p className="text-sm text-forest-600">
                  New to LunaJoy?{' '}
                  <button 
                    type="button"
                    onClick={() => {}} 
                    className="text-forest-700 hover:text-forest-800 font-medium underline"
                  >
                    Create an account
                  </button>
                </p>
              </div>
            </form>

            {/* Security Note */}
            <div className="mt-8 flex items-start space-x-2 text-xs text-forest-500">
              <Shield className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <p>
                By signing in, you agree to our Terms of Service and Privacy Policy. 
                Your data is encrypted and will never be shared without your consent.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;