// src/contexts/UserContext.jsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import { userAPI } from '../services/api';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check for saved user on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('lunajoy_user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error loading saved user:', error);
        localStorage.removeItem('lunajoy_user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (userId) => {
    try {
      setLoading(true);
      // Clear any existing user data first
      setUser(null);
      setIsAuthenticated(false);
      
      const userData = await userAPI.getUser(userId);
      
      setUser(userData);
      setIsAuthenticated(true);
      localStorage.setItem('lunajoy_user', JSON.stringify(userData));
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      // Make sure to clear state on error too
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('lunajoy_user');
      
      return { 
        success: false, 
        error: error.message || 'Usuario no encontrado' 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('lunajoy_user');
    localStorage.removeItem('last_search');
  };

  const updateUser = (updates) => {
    const updatedUser = { ...user, ...updates };
    setUser(updatedUser);
    localStorage.setItem('lunajoy_user', JSON.stringify(updatedUser));
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

// Custom hook to use the user context
export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};  