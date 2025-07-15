// src/services/api.js

// Get API URL from environment or fallback
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Base URLs
const API_BASE_URL = `${API_URL}/api`;
const API_V1_URL = `${API_URL}/api/v1`;

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    let error;
    try {
      const errorData = await response.json();
      error = errorData.detail || errorData.message || 'Error en la solicitud';
    } catch {
      error = `Error ${response.status}: ${response.statusText}`;
    }
    throw new Error(error);
  }
  return response.json();
};

// Matching API endpoints
export const matchingAPI = {
  // Anonymous matching - EXACTLY as the backend expects
  match: async (preferences) => {
    // Extract limit if present
    const { limit, ...cleanPreferences } = preferences;
    const url = limit ? `${API_V1_URL}/match?limit=${limit}` : `${API_V1_URL}/match`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(cleanPreferences), // Send preferences without limit
    });
    return handleResponse(response);
  },

  // Basic user matching - with specific structure
  matchBasic: async (userId, preferences, profile) => {
    // Extract limit if present
    const { limit, ...cleanPreferences } = preferences;
    const url = limit ? `${API_V1_URL}/match/basic?limit=${limit}` : `${API_V1_URL}/match/basic`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        preferences: cleanPreferences, // preferences without limit
        profile: profile || {}
      }),
    });
    return handleResponse(response);
  },

  // Complete user matching with history - with specific structure
  matchComplete: async (userId, preferences, profile, useHistory = true) => {
    // Extract limit if present
    const { limit, ...cleanPreferences } = preferences;
    const url = limit ? `${API_V1_URL}/match/complete?limit=${limit}` : `${API_V1_URL}/match/complete`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        preferences: cleanPreferences, // preferences without limit
        profile: profile || {},
        use_history: useHistory
      }),
    });
    return handleResponse(response);
  },

  // Get match explanation
  getExplanation: async (params) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API_V1_URL}/match/explain?${queryString}`);
    return handleResponse(response);
  },

  // Get ALL match explanations
  getExplanationAll: async (params) => {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API_V1_URL}/match/explain/all?${queryString}`);
    return handleResponse(response);
  },

  // Get match statistics
  getStats: async () => {
    const response = await fetch(`${API_V1_URL}/match/stats`);
    return handleResponse(response);
  },
};

// User API endpoints
export const userAPI = {
  // Get user details
  getUser: async (userId) => {
    const response = await fetch(`${API_V1_URL}/users/${userId}`);
    return handleResponse(response);
  },

  // Login (no password needed for demo)
  login: async (userId) => {
    // First try to get the user directly
    try {
      const response = await fetch(`${API_V1_URL}/users/${userId}`);
      if (response.ok) {
        return handleResponse(response);
      }
    } catch (error) {
      console.log('User not found via GET, trying POST login...');
    }

    // If that fails, try the login endpoint
    const response = await fetch(`${API_V1_URL}/users/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId }),
    });
    return handleResponse(response);
  },

  // Get user's match history
  getMatchHistory: async (userId, limit = 20, offset = 0) => {
    const response = await fetch(
      `${API_V1_URL}/users/${userId}/match-history?limit=${limit}&offset=${offset}`
    );
    return handleResponse(response);
  },
};

// Clinician API endpoints
export const clinicianAPI = {
  // Get clinicians list
  getClinicians: async (filters = {}) => {
    const queryString = new URLSearchParams(filters).toString();
    const response = await fetch(`${API_V1_URL}/clinicians?${queryString}`);
    return handleResponse(response);
  },

  // Get clinician details
  getClinicianDetails: async (clinicianId, userId = null) => {
    const url = userId
      ? `${API_V1_URL}/clinicians/${clinicianId}?user_id=${userId}`
      : `${API_V1_URL}/clinicians/${clinicianId}`;
    const response = await fetch(url);
    return handleResponse(response);
  },
};

// Interaction API endpoints
export const interactionAPI = {
  // Track view
  trackView: async (userId, clinicianId, context = 'match_result') => {
    const response = await fetch(`${API_V1_URL}/interactions/view`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        clinician_id: clinicianId,
        context,
      }),
    });
    return handleResponse(response);
  },

  // Track contact
  trackContact: async (userId, clinicianId) => {
    const response = await fetch(`${API_V1_URL}/interactions/contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        clinician_id: clinicianId,
        action: 'contacted',
      }),
    });
    return handleResponse(response);
  },

  // Track booking
  trackBooking: async (userId, clinicianId) => {
    const response = await fetch(`${API_V1_URL}/interactions/book`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        clinician_id: clinicianId,
        action: 'booked',
      }),
    });
    return handleResponse(response);
  },
};

// Health check
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// System/UI config (update the URL)
export const getUIConfig = async () => {
  try {
    const response = await fetch(`${API_URL}/api/system/ui-config`);
    return handleResponse(response);
  } catch (error) {
    console.error('Failed to fetch UI config:', error);
    // Return default config if API fails
    return {
      animated_stats: {
        active_professionals: 500,
        total_matches: 10000,
        success_rate: 94,
        states_covered: 50
      }
    };
  }
};