import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, User, LoginCredentials, ApiError } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  error: string | null;
  fieldErrors: Record<string, string[]>;
  clearError: () => void;
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
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  useEffect(() => {
    // Check if user is already authenticated on app startup
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    console.log('🔍 [AUTH] Checking authentication status...');
    
    try {
      const hasToken = apiService.isAuthenticated();
      console.log('🔑 [AUTH] Token exists in localStorage:', hasToken);
      
      if (hasToken) {
        // Try to get current user profile
        console.log('👤 [AUTH] Fetching user profile...');
        const userData = await apiService.get('/api/v1/users/me/');
        console.log('✅ [AUTH] User profile loaded:', { 
          id: userData.id,
          email: userData.email,
          role: userData.role,
          is_active: userData.is_active
        });
        setUser(userData);
      } else {
        console.log('🚫 [AUTH] No token found, user not authenticated');
      }
    } catch (err) {
      console.error('❌ [AUTH] Auth check failed:', err);
      // If token is invalid, clear it
      apiService.logout();
      console.log('🧹 [AUTH] Invalid token cleared');
    } finally {
      setIsLoading(false);
      console.log('🏁 [AUTH] Auth check completed');
    }
  };

  const login = async (credentials: LoginCredentials) => {
    console.log('🔐 [AUTH] Login function called with:', { email: credentials.email });
    
    try {
      setIsLoading(true);
      setError(null);
      setFieldErrors({});
      console.log('🔄 [AUTH] Loading state set to true');

      const userData = await apiService.login(credentials);
      console.log('✅ [AUTH] Login successful, user data:', { 
        id: userData.id,
        email: userData.email,
        role: userData.role,
        is_active: userData.is_active
      });
      
      setUser(userData);
      console.log('👤 [AUTH] User state updated');
    } catch (err) {
      console.error('❌ [AUTH] Login error in context:', err);
      const apiError = err as ApiError;
      setError(apiError.message || 'Login failed');
      setFieldErrors(apiError.errors || {});
      console.log('🚫 [AUTH] Error state set:', { 
        message: apiError.message,
        fieldErrors: apiError.errors 
      });
      throw err;
    } finally {
      setIsLoading(false);
      console.log('🔄 [AUTH] Loading state set to false');
    }
  };

  const logout = () => {
    console.log('🔓 [AUTH] Logout initiated by user');
    apiService.logout();
    setUser(null);
    setError(null);
    setFieldErrors({});
    console.log('✅ [AUTH] User logged out');
  };

  const clearError = () => {
    setError(null);
    setFieldErrors({});
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    error,
    fieldErrors,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
