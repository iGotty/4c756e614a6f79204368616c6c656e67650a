import React from 'react';
import { AlertCircle, XCircle, Info, CheckCircle, Heart, RefreshCw, HelpCircle, X } from 'lucide-react';

const ErrorMessage = ({ message, type = 'error', action, actionText = 'Try Again', onDismiss }) => {
  const configs = {
    error: {
      icon: XCircle,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      iconColor: 'text-red-500',
      textColor: 'text-red-800',
      title: "Something went wrong",
      supportText: "Don't worry, we're here to help"
    },
    warning: {
      icon: AlertCircle,
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      iconColor: 'text-amber-500',
      textColor: 'text-amber-800',
      title: "Please note",
      supportText: "This is just a heads up"
    },
    info: {
      icon: Info,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-500',
      textColor: 'text-blue-800',
      title: "Good to know",
      supportText: null
    },
    success: {
      icon: CheckCircle,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      iconColor: 'text-green-500',
      textColor: 'text-green-800',
      title: "Success!",
      supportText: null
    },
    empty: {
      icon: Heart,
      bgColor: 'bg-forest-50',
      borderColor: 'border-forest-200',
      iconColor: 'text-forest-500',
      textColor: 'text-forest-800',
      title: "No results found",
      supportText: "Let's try a different approach"
    }
  };

  const config = configs[type] || configs.error;
  const Icon = config.icon;

  // Friendly error messages mapping
  const friendlyMessages = {
    'Network Error': "It looks like you're offline. Please check your internet connection.",
    'Server Error': "Our servers are taking a break. Please try again in a moment.",
    'Not Found': "We couldn't find what you're looking for. Let's try something else.",
    'Unauthorized': "Please sign in to continue your wellness journey.",
    'Validation Error': "Please check your information and try again."
  };

  const displayMessage = friendlyMessages[message] || message;

  return (
    <div className={`rounded-2xl border-2 ${config.borderColor} ${config.bgColor} p-6 animate-fade-in-down`}>
      <div className="flex items-start space-x-4">
        {/* Icon with Animation */}
        <div className={`flex-shrink-0 ${type === 'error' ? 'animate-bounce-soft' : 'animate-pulse-soft'}`}>
          <div className={`w-12 h-12 rounded-full bg-white shadow-inner flex items-center justify-center`}>
            <Icon className={`w-6 h-6 ${config.iconColor}`} />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1">
          {config.title && (
            <h3 className={`font-semibold ${config.textColor} mb-1`}>
              {config.title}
            </h3>
          )}
          
          <p className={`${config.textColor} opacity-90`}>
            {displayMessage}
          </p>

          {config.supportText && (
            <p className={`text-sm ${config.textColor} opacity-70 mt-1`}>
              {config.supportText}
            </p>
          )}

          {/* Actions */}
          <div className="mt-4 flex items-center space-x-3">
            {action && (
              <button
                onClick={action}
                className={`px-4 py-2 rounded-lg font-medium transition-all transform hover:scale-105 flex items-center space-x-2 ${
                  type === 'error' 
                    ? 'bg-red-600 text-white hover:bg-red-700' 
                    : 'bg-forest-600 text-white hover:bg-forest-700'
                }`}
              >
                <RefreshCw className="w-4 h-4" />
                <span>{actionText}</span>
              </button>
            )}

            {type === 'error' && (
              <button className="text-sm text-forest-600 hover:text-forest-800 underline flex items-center space-x-1">
                <HelpCircle className="w-4 h-4" />
                <span>Get help</span>
              </button>
            )}
          </div>
        </div>

        {/* Dismiss Button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 p-1 hover:bg-white/50 rounded-lg transition-colors"
            aria-label="Dismiss message"
          >
            <X className={`w-5 h-5 ${config.textColor} opacity-50 hover:opacity-100`} />
          </button>
        )}
      </div>

      {/* Decorative Elements */}
      {type === 'error' && (
        <div className="mt-6 p-4 bg-white/50 rounded-xl">
          <p className="text-sm text-forest-700">
            <span className="font-medium">Need immediate help?</span> Our support team is available 24/7 at{' '}
            <a href="tel:1-800-LUNAJOY" className="text-forest-600 underline font-medium">
              1-800-LUNAJOY
            </a>
          </p>
        </div>
      )}

      {type === 'empty' && (
        <div className="mt-6 space-y-3">
          <p className="text-sm font-medium text-forest-700">Try these suggestions:</p>
          <ul className="space-y-2">
            <li className="flex items-start space-x-2 text-sm text-forest-600">
              <span className="text-forest-400 mt-0.5">•</span>
              <span>Expand your search radius or remove some filters</span>
            </li>
            <li className="flex items-start space-x-2 text-sm text-forest-600">
              <span className="text-forest-400 mt-0.5">•</span>
              <span>Check if your insurance provider name is spelled correctly</span>
            </li>
            <li className="flex items-start space-x-2 text-sm text-forest-600">
              <span className="text-forest-400 mt-0.5">•</span>
              <span>Consider online therapy options for more flexibility</span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ErrorMessage;