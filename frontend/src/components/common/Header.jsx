import React, { useState, useEffect } from 'react';
import { Menu, X, User, Heart, Calendar, LogOut, Sparkles } from 'lucide-react';
import { useUser } from '../../contexts/UserContext';

const Header = ({ onLoginClick }) => {
  const { user, isAuthenticated, logout } = useUser();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-xl shadow-soft'
          : 'bg-forest-800/80 backdrop-blur-md'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex items-center">
            <a href="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-sunshine rounded-full opacity-20 group-hover:opacity-30 transition-opacity blur-lg"></div>
                <div className="relative w-10 h-10 bg-forest-gradient rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform">
                  <span className="text-white text-xl">🌙</span>
                </div>
              </div>
              <span className={`text-2xl font-display font-bold ${
                isScrolled ? 'text-forest-700' : 'text-white'
              } group-hover:text-forest-500 transition-colors`}>
                LunaJoy
              </span>
            </a>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <a
              href="#how-it-works"
              className={`font-medium transition-all hover:text-sunshine ${
                isScrolled ? 'text-forest-600' : 'text-white/90'
              }`}
            >
              How it Works
            </a>
            <a
              href="#professionals"
              className={`font-medium transition-all hover:text-sunshine ${
                isScrolled ? 'text-forest-600' : 'text-white/90'
              }`}
            >
              Find Professionals
            </a>
            <a
              href="#about"
              className={`font-medium transition-all hover:text-sunshine ${
                isScrolled ? 'text-forest-600' : 'text-white/90'
              }`}
            >
              About
            </a>
          </div>

          {/* User Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className={`flex items-center space-x-3 px-4 py-2 rounded-full transition-all ${
                    isScrolled
                      ? 'bg-forest-50 hover:bg-forest-100'
                      : 'bg-white/10 hover:bg-white/20 backdrop-blur-md'
                  }`}
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-forest-400 to-forest-600 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <span className={`font-medium ${
                    isScrolled ? 'text-forest-700' : 'text-white'
                  }`}>
                    {user.user_id.split('_')[1]}
                  </span>
                  <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    user.registration_type === 'complete'
                      ? 'bg-sunshine/20 text-sunshine-700'
                      : 'bg-forest-100 text-forest-700'
                  }`}>
                    <Sparkles className="w-3 h-3 mr-1" />
                    {user.registration_type === 'complete' ? 'Premium' : 'Basic'}
                  </div>
                </button>

                {/* User Dropdown Menu */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-2xl shadow-hard overflow-hidden animate-scale-in">
                    <div className="p-4 bg-forest-50 border-b border-forest-100">
                      <p className="text-sm text-forest-600">Signed in as</p>
                      <p className="font-semibold text-forest-800">{user.user_id}</p>
                    </div>
                    <div className="p-2">
                      <a
                        href="#saved"
                        className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-forest-50 transition-colors"
                      >
                        <Heart className="w-5 h-5 text-forest-600" />
                        <span className="text-forest-700">Saved Professionals</span>
                      </a>
                      <a
                        href="#appointments"
                        className="flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-forest-50 transition-colors"
                      >
                        <Calendar className="w-5 h-5 text-forest-600" />
                        <span className="text-forest-700">My Appointments</span>
                      </a>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-red-50 transition-colors text-left"
                      >
                        <LogOut className="w-5 h-5 text-red-600" />
                        <span className="text-red-700">Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={onLoginClick}
                className={`px-6 py-2.5 rounded-full font-medium transition-all transform hover:scale-105 ${
                  isScrolled
                    ? 'bg-sunshine text-forest-800 hover:bg-sunshine-600 shadow-medium'
                    : 'bg-white/90 text-forest-700 hover:bg-white backdrop-blur-md'
                }`}
              >
                Sign In
              </button>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className={`md:hidden p-2 rounded-lg transition-colors ${
              isScrolled
                ? 'text-forest-700 hover:bg-forest-50'
                : 'text-white hover:bg-white/10'
            }`}
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-white shadow-hard animate-slide-in-down">
            <div className="px-4 py-6 space-y-4">
              <a
                href="#how-it-works"
                className="block py-2 text-forest-700 font-medium hover:text-sunshine transition-colors"
              >
                How it Works
              </a>
              <a
                href="#professionals"
                className="block py-2 text-forest-700 font-medium hover:text-sunshine transition-colors"
              >
                Find Professionals
              </a>
              <a
                href="#about"
                className="block py-2 text-forest-700 font-medium hover:text-sunshine transition-colors"
              >
                About
              </a>
              <div className="pt-4 border-t border-forest-100">
                {isAuthenticated && user ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 bg-forest-50 rounded-lg">
                      <div className="w-10 h-10 bg-gradient-to-br from-forest-400 to-forest-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-forest-800">{user.user_id}</p>
                        <p className="text-xs text-forest-600 capitalize">{user.registration_type} User</p>
                      </div>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full py-3 px-4 bg-red-50 text-red-700 rounded-lg font-medium hover:bg-red-100 transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      onLoginClick();
                    }}
                    className="w-full py-3 px-4 bg-sunshine text-forest-800 rounded-lg font-medium hover:bg-sunshine-600 transition-colors"
                  >
                    Sign In
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Close dropdown when clicking outside */}
      {isUserMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsUserMenuOpen(false)}
        />
      )}
    </header>
  );
};

export default Header;