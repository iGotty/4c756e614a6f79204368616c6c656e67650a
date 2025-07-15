import { useState, useEffect } from 'react';
import { Heart, Brain, Sparkles } from 'lucide-react';

const LoadingSpinner = ({ size = 'medium', message = 'Loading...', variant = 'default' }) => {
  const [currentTip, setCurrentTip] = useState(0);
  const [showTip, setShowTip] = useState(false);

  const tips = [
    "Finding the perfect match for you...",
    "Analyzing compatibility scores...",
    "Reviewing professional backgrounds...",
    "Checking real-time availability...",
    "Optimizing your results...",
    "Almost there..."
  ];

  const affirmations = [
    "You're taking a great step",
    "Your wellness journey matters",
    "Finding help is a sign of strength",
    "You deserve quality care",
    "Better days are ahead"
  ];

  useEffect(() => {
    if (variant === 'search') {
      const interval = setInterval(() => {
        setCurrentTip((prev) => (prev + 1) % tips.length);
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [variant]);

  useEffect(() => {
    if (variant === 'affirmation') {
      setTimeout(() => setShowTip(true), 500);
    }
  }, [variant]);

  const sizes = {
    small: 'w-8 h-8',
    medium: 'w-16 h-16',
    large: 'w-24 h-24'
  };

  const spinnerSize = sizes[size] || sizes.medium;

  if (variant === 'minimal') {
    return (
      <div className="flex items-center justify-center p-4">
        <div className={`${spinnerSize} relative`}>
          <div className="absolute inset-0 border-4 border-forest-200 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-forest-600 rounded-full border-t-transparent animate-spin"></div>
        </div>
      </div>
    );
  }

  if (variant === 'dots') {
    return (
      <div className="flex items-center justify-center space-x-2 p-4">
        <div className="w-3 h-3 bg-forest-600 rounded-full animate-bounce-soft" style={{ animationDelay: '0ms' }}></div>
        <div className="w-3 h-3 bg-forest-600 rounded-full animate-bounce-soft" style={{ animationDelay: '150ms' }}></div>
        <div className="w-3 h-3 bg-forest-600 rounded-full animate-bounce-soft" style={{ animationDelay: '300ms' }}></div>
      </div>
    );
  }

  if (variant === 'search') {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        {/* Animated Logo */}
        <div className="relative mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-forest-400 to-forest-600 rounded-full flex items-center justify-center animate-breathe">
            <Sparkles className="w-12 h-12 text-white animate-pulse-soft" />
          </div>
          <div className="absolute inset-0 bg-forest-500 rounded-full animate-ping opacity-20"></div>
        </div>

        {/* Progress Ring */}
        <div className="relative w-32 h-32 mb-6">
          <svg className="w-full h-full transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="60"
              stroke="#e8f0ed"
              strokeWidth="8"
              fill="none"
            />
            <circle
              cx="64"
              cy="64"
              r="60"
              stroke="url(#gradient)"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 60}`}
              strokeDashoffset={`${2 * Math.PI * 60 * 0.25}`}
              className="animate-[spin_3s_linear_infinite]"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#44645c" />
                <stop offset="100%" stopColor="#fab21c" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <Brain className="w-8 h-8 text-forest-600 animate-pulse" />
          </div>
        </div>

        {/* Loading Text */}
        <h3 className="text-xl font-semibold text-forest-800 mb-2">{message}</h3>
        
        {/* Animated Tips */}
        <div className="h-6 relative overflow-hidden">
          <p className="text-forest-600 text-sm animate-fade-in-up key={currentTip}">
            {tips[currentTip]}
          </p>
        </div>

        {/* Progress Dots */}
        <div className="flex items-center space-x-2 mt-6">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i === currentTip
                  ? 'w-8 bg-sunshine'
                  : i < currentTip
                  ? 'bg-forest-400'
                  : 'bg-forest-200'
              }`}
            />
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'affirmation') {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        {/* Heart Animation */}
        <div className="relative mb-6">
          <Heart className="w-16 h-16 text-red-500 fill-red-500 animate-pulse" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Heart className="w-16 h-16 text-red-500 fill-red-500 animate-ping opacity-30" />
          </div>
        </div>

        {/* Loading Bar */}
        <div className="w-48 h-2 bg-forest-100 rounded-full overflow-hidden mb-4">
          <div className="h-full bg-gradient-to-r from-forest-400 to-sunshine animate-[shimmer_2s_ease-in-out_infinite]"></div>
        </div>

        {/* Message */}
        <p className="text-forest-800 font-medium mb-2">{message}</p>
        
        {/* Affirmation */}
        {showTip && (
          <p className="text-forest-600 text-sm animate-fade-in">
            {affirmations[Math.floor(Math.random() * affirmations.length)]}
          </p>
        )}
      </div>
    );
  }

  // Default variant
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className={`${spinnerSize} relative mb-4`}>
        {/* Outer ring */}
        <div className="absolute inset-0 border-4 border-forest-100 rounded-full"></div>
        
        {/* Spinning gradient ring */}
        <div className="absolute inset-0 rounded-full overflow-hidden animate-spin">
          <div className="w-full h-full bg-gradient-to-r from-forest-600 via-sunshine to-forest-600 
                          opacity-80 blur-sm"></div>
        </div>
        
        {/* Inner spinning ring */}
        <div className="absolute inset-0 border-4 border-transparent border-t-forest-600 
                        border-r-sunshine rounded-full animate-spin"></div>
        
        {/* Center icon */}
        {size === 'large' && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-inner">
              <Sparkles className="w-4 h-4 text-forest-600" />
            </div>
          </div>
        )}
      </div>
      
      {message && (
        <p className="text-forest-700 font-medium animate-pulse">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;