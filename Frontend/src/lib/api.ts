import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// ✅ Fixed — falls back to localhost in local dev
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// JWT Token Types
export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role?: string;
  department?: string;
  is_active: boolean;
}

// Storage keys
const ACCESS_TOKEN_KEY = 'auth_access_token';
const REFRESH_TOKEN_KEY = 'auth_refresh_token';

// API Service Class
class ApiService {
  private api: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: any) => void;
  }> = [];

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
          console.log('🔐 [API] Request with token:', { 
            method: config.method?.toUpperCase(),
            url: config.url,
            hasAuth: true
          });
        } else {
          console.log('🔓 [API] Request without token:', { 
            method: config.method?.toUpperCase(),
            url: config.url,
            hasAuth: false
          });
        }
        return config;
      },
      (error) => {
        console.error('❌ [API] Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && originalRequest) {
          // If token refresh is already in progress, queue the request
          if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject });
            }).then(token => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return this.api(originalRequest);
            }).catch(err => {
              return Promise.reject(err);
            });
          }

          this.isRefreshing = true;

          try {
            const newToken = await this.refreshToken();
            this.processQueue(null, newToken);

            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            this.processQueue(refreshError, null);
            this.logout();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        return Promise.reject(this.handleError(error));
      }
    );
  }

  private processQueue(error: any, token: string | null = null) {
    this.failedQueue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token!);
      }
    });

    this.failedQueue = [];
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      const { status, data } = error.response;

      if (status === 400 && data) {
        return {
          message: 'Validation error',
          status,
          errors: data as Record<string, string[]>,
        };
      }

      if (status === 401) {
        return {
          message: 'Authentication required',
          status,
        };
      }

      if (status === 403) {
        return {
          message: 'Access denied',
          status,
        };
      }

      if (status === 404) {
        return {
          message: 'Resource not found',
          status,
        };
      }

      if (status >= 500) {
        return {
          message: 'Server error',
          status,
        };
      }

      return {
        message: (data as any)?.message || 'Request failed',
        status,
      };
    }

    if (error.request) {
      return {
        message: 'Network error - please check your connection',
        status: 0,
      };
    }

    return {
      message: error.message || 'An unexpected error occurred',
      status: 0,
    };
  }

  // Token Management
  private getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  private setTokens(tokens: AuthTokens): void {
    console.log('💾 [API] Setting tokens...');
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
    console.log('✅ [API] Tokens stored successfully');
  }

  private clearTokens(): void {
    console.log('🗑️ [API] Clearing tokens...');
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    console.log('✅ [API] Tokens cleared successfully');
  }

  private async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/api/token/refresh/`, {
        refresh: refreshToken,
      });

      const newTokens: AuthTokens = response.data;
      this.setTokens(newTokens);
      return newTokens.access;
    } catch (error) {
      throw error;
    }
  }

  // Authentication Methods
  async login(credentials: LoginCredentials): Promise<User> {
    console.log('🔐 [API] Login attempt started:', { email: credentials.email });
    
    try {
      // Backend now accepts email directly since USERNAME_FIELD = 'email'
      console.log('🌐 [API] Sending login request to:', `${API_BASE_URL}/api/token/`);
      console.log('📤 [API] Request payload:', { email: credentials.email, password: '***' });
      console.log('🌍 [API] Current API_BASE_URL:', API_BASE_URL);
      
      const response = await axios.post(`${API_BASE_URL}/api/token/`, credentials);
      console.log('✅ [API] Login response received:', response.status);
      console.log('📥 [API] Response data keys:', Object.keys(response.data));
      
      const tokens: AuthTokens = {
        access: response.data.access,
        refresh: response.data.refresh
      };
      this.setTokens(tokens);
      console.log('💾 [API] Tokens stored in localStorage');

      // Enhanced: Backend now returns user data directly
      let userData: User = response.data.user;
      
      if (!userData) {
        // Fallback: If user data not in response, fetch from profile endpoint
        console.log('👤 [API] User data not in login response, fetching from /api/v1/users/me/...');
        const userResponse = await this.api.get('/api/v1/users/me/');
        userData = userResponse.data;
      }
      
      console.log('✅ [API] User profile obtained:', { 
        id: userData.id,
        email: userData.email,
        role: userData.role || 'N/A'
      });
      
      return userData;
    } catch (error) {
      console.error('❌ [API] Login failed:', error);
      
      // Enhanced network error debugging
      if (error.code === 'ERR_FAILED' || error.message?.includes('Network Error')) {
        console.error('🌐 [API] Network connection failed - check if backend is running at:', API_BASE_URL);
        console.error('🔧 [API] Solutions:');
        console.error('  1. Run: python manage.py runserver');
        console.error('  2. Backend URL:', API_BASE_URL);
        console.error('  3. Check CORS in settings.py');
        console.error('  4. Check firewall/antivirus');
      }
      
      const authError = this.handleAuthError(error as AxiosError);
      console.error('🚫 [API] Processed error:', authError);
      throw authError;
    }
  }

  private handleAuthError(error: AxiosError): ApiError {
    if (error.response) {
      const { status, data } = error.response;
      const errorData = data as any;

      // Handle 401 Unauthorized responses (login endpoint returns 401)
      if (status === 401) {
        const message = errorData.error || errorData.non_field_errors?.[0];
        
        if (!message) {
          return {
            message: 'Login failed',
            status,
            errors: {},
          };
        }

        // Map backend messages to user-friendly messages
        if (message.includes('No account found with this email address')) {
          return {
            message: 'Email is not registered',
            status,
            errors: { email: ['Email is not registered'] }
          };
        }
        
        if (message.includes('Incorrect password for this email address')) {
          return {
            message: 'Password is incorrect',
            status,
            errors: { password: ['Password is incorrect'] }
          };
        }
        
        if (message.includes('This user account is inactive')) {
          return {
            message: 'Your account has been deactivated',
            status,
            errors: {}
          };
        }

        // Generic error for other 401 responses
        return {
          message,
          status,
          errors: {}
        };
      }

      // Handle 400 Bad Request responses
      if (status === 400 && errorData) {
        // Handle specific authentication errors from backend
        if (errorData.non_field_errors && errorData.non_field_errors.length > 0) {
          const message = errorData.non_field_errors[0];
          
          // Email not found in system
          if (message.includes('No account found with this email address')) {
            return {
              message: 'Email is not registered',
              status,
              errors: { email: ['Email is not registered'] }
            };
          }
          
          // Incorrect password
          if (message.includes('Incorrect password for this email address')) {
            return {
              message: 'Password is incorrect',
              status,
              errors: { password: ['Password is incorrect'] }
            };
          }
          
          // User account inactive
          if (message.includes('This user account is inactive')) {
            return {
              message: 'Your account has been deactivated',
              status,
              errors: {}
            };
          }
          
          // Both email and password invalid (fallback for generic invalid credentials)
          if (message.toLowerCase().includes('invalid') || message.toLowerCase().includes('credentials')) {
            return {
              message: 'Invalid email and password',
              status,
              errors: { 
                email: ['Invalid email and password'],
                password: ['Invalid email and password']
              }
            };
          }
          
          // Generic error message
          return {
            message,
            status,
            errors: {}
          };
        }

        // Handle field-specific errors from validation
        if (errorData.email || errorData.username) {
          return {
            message: 'Email is not registered',
            status,
            errors: { email: errorData.email || errorData.username }
          };
        }

        if (errorData.password) {
          return {
            message: 'Password is incorrect',
            status,
            errors: { password: errorData.password }
          };
        }

        return {
          message: 'Invalid credentials',
          status,
          errors: errorData as Record<string, string[]>,
        };
      }
    }

    // Default to invalid credentials for network/other errors
    return {
      message: 'Invalid credentials',
      status: 400,
    };
  }

  logout(): void {
    console.log('🚪 [API] Logout started');
    try {
      // Attempt to notify backend (non-blocking)
      this.api.post('/api/logout/', {}).catch(err => {
        console.warn('⚠️ [API] Backend logout notification failed (non-critical):', err);
      });
    } catch (err) {
      console.warn('⚠️ [API] Could not notify backend of logout');
    } finally {
      // Always clear local tokens
      this.clearTokens();
      console.log('✅ [API] Logout complete - tokens cleared');
    }
  }

  async checkHealth(): Promise<boolean> {
    console.log('🏥 [API] Health check started');
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/health/`, {
        timeout: 5000
      });
      console.log('✅ [API] Health check passed:', response.data);
      return true;
    } catch (error) {
      console.error('❌ [API] Health check failed:', error.message);
      return false;
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  // Generic API Methods
  async get<T = any>(url: string, params?: any): Promise<T> {
    const response = await this.api.get(url, { params });
    return response.data;
  }

  async post<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.api.post(url, data);
    return response.data;
  }

  async put<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.api.put(url, data);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.api.patch(url, data);
    return response.data;
  }

  async delete<T = any>(url: string): Promise<T> {
    const response = await this.api.delete(url);
    return response.data;
  }

  // Resource-specific methods (convenience methods)
  // Users
  async getUsers(params?: any) {
    return this.get('/api/v1/users/', params);
  }

  async getUser(id: number) {
    return this.get(`/api/v1/users/${id}/`);
  }

  async createUser(data: any) {
    return this.post('/api/v1/users/', data);
  }

  async updateUser(id: number, data: any) {
    return this.put(`/api/v1/users/${id}/`, data);
  }

  async deleteUser(id: number) {
    return this.delete(`/api/v1/users/${id}/`);
  }

  // Customers
  async getCustomers(params?: any) {
    return this.get('/api/v1/customers/', params);
  }

  async getCustomer(id: number) {
    return this.get(`/api/v1/customers/${id}/`);
  }

  async createCustomer(data: any) {
    return this.post('/api/v1/customers/', data);
  }

  async updateCustomer(id: number, data: any) {
    return this.put(`/api/v1/customers/${id}/`, data);
  }

  async deleteCustomer(id: number) {
    return this.delete(`/api/v1/customers/${id}/`);
  }

  // Policy Types
  async getPolicyTypes(params?: any) {
    return this.get('/api/v1/policy-types/', params);
  }

  async getGenders(params?: any) {
    return this.get('/api/v1/genders/', params);
  }

  async getLocations(params?: any) {
    return this.get('/api/v1/locations/', params);
  }

  async getIncomeLevels(params?: any) {
    return this.get('/api/v1/income-levels/', params);
  }

  // Policies
  async getPolicies(params?: any) {
    return this.get('/api/v1/policies/', params);
  }

  async getPolicy(id: number) {
    return this.get(`/api/v1/policies/${id}/`);
  }

  async createPolicy(data: any) {
    return this.post('/api/v1/policies/', data);
  }

  async updatePolicy(id: number, data: any) {
    return this.put(`/api/v1/policies/${id}/`, data);
  }

  async deletePolicy(id: number) {
    return this.delete(`/api/v1/policies/${id}/`);
  }

  // Claims
  async getClaims(params?: any) {
    return this.get('/api/v1/claims/', params);
  }

  async getClaim(id: number) {
    return this.get(`/api/v1/claims/${id}/`);
  }

  async createClaim(data: any) {
    return this.post('/api/v1/claims/', data);
  }

  async updateClaim(id: number, data: any) {
    return this.put(`/api/v1/claims/${id}/`, data);
  }

  async uploadClaimDocument(claimId: string, data: FormData) {
    return this.post(`/api/v1/claims/${claimId}/upload_document/`, data, true);
  }

  async deleteClaim(id: number) {
    return this.delete(`/api/v1/claims/${id}/`);
  }

  // Payments
  async getPayments(params?: any) {
    return this.get('/api/v1/payments/', params);
  }

  async getPayment(id: number) {
    return this.get(`/api/v1/payments/${id}/`);
  }

  async createPayment(data: any) {
    return this.post('/api/v1/payments/', data);
  }

  async updatePayment(id: number, data: any) {
    return this.put(`/api/v1/payments/${id}/`, data);
  }

  async deletePayment(id: number) {
    return this.delete(`/api/v1/payments/${id}/`);
  }

  // Predictions
  async getPredictions(params?: any) {
    return this.get('/api/v1/predictions/', params);
  }

  async getPrediction(id: number) {
    return this.get(`/api/v1/predictions/${id}/`);
  }

  async predictSingle(data: any) {
    return this.post('/api/v1/predictions/predict_single/', data);
  }

  // Batch Jobs
  async getBatchJobs(params?: any) {
    return this.get('/api/v1/batch-jobs/', params);
  }

  async createBatchJob(data: any) {
    return this.post('/api/v1/batch-jobs/', data);
  }

  async runBatchPrediction(data: any) {
    return this.post('/api/v1/batch-jobs/run_batch_prediction/', data);
  }

  // Churn calculation helper endpoints
  async getChurnCalculationCustomerDetails(customerId: string) {
    return this.get('/api/v1/churn-calculation/customer_details/', {
      customer_id: customerId
    });
  }

  async calculateChurn(data: any) {
    return this.post('/api/v1/churn-calculation/calculate_churn/', data);
  }

  // Dashboard
  async getDashboardStats() {
    return this.get('/api/v1/dashboard/');
  }

  // Analytics
  async getMonthlyTrends() {
    return this.get('/api/v1/analytics/monthly_trends/');
  }

  async getChurnByLocation() {
    return this.get('/api/v1/analytics/churn_by_location/');
  }

  async getChurnByAge() {
    return this.get('/api/v1/analytics/churn_by_age/');
  }

  async getChurnByIncome() {
    return this.get('/api/v1/analytics/churn_by_income/');
  }

  async getRecentActivities() {
    return this.get('/api/v1/analytics/recent_activities/');
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
