import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User, LoginFormData, RegisterFormData } from '../types';
import { authAPI, setAuthToken, getAuthToken, removeAuthToken, setUser, getUser, removeUser } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginFormData) => Promise<void>;
  register: (userData: RegisterFormData) => Promise<void>;
  logout: () => void;
  updateProfile: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUserState] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on app load
  useEffect(() => {
    const initializeAuth = async () => {
      const token = getAuthToken();
      const savedUser = getUser();

      if (token && savedUser) {
        try {
          // Verify token is still valid by fetching current user
          const currentUser = await authAPI.getCurrentUser();
          setUserState(currentUser);
          setUser(currentUser);
        } catch (error) {
          // Token is invalid, clear auth data
          removeAuthToken();
          removeUser();
          setUserState(null);
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginFormData) => {
    try {
      const response = await authAPI.login({
        username: credentials.email,
        password: credentials.password,
      });

      setAuthToken(response.access_token);
      
      // Fetch user data after successful login
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      setUserState(userData);

      if (credentials.rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (userData: RegisterFormData) => {
    try {
      const response = await authAPI.register({
        email: userData.email,
        phone: userData.phone,
        password: userData.password,
        full_name: userData.full_name,
        address: userData.address,
        emergency_contact: userData.emergency_contact,
        medical_info: userData.medical_info,
      });

      setAuthToken(response.access_token);
      
      // Fetch user data after successful registration
      const userDataResponse = await authAPI.getCurrentUser();
      setUser(userDataResponse);
      setUserState(userDataResponse);
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    }
  };

  const logout = () => {
    removeAuthToken();
    removeUser();
    setUserState(null);
    localStorage.removeItem('rememberMe');
  };

  const updateProfile = async (userData: Partial<User>) => {
    try {
      const updatedUser = await authAPI.updateProfile(userData);
      setUser(updatedUser);
      setUserState(updatedUser);
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 