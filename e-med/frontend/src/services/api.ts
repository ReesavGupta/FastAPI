import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User,
  Medicine,
  Category,
  Order,
  Prescription,
  ApiResponse,
  PaginatedResponse
} from '../types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  // Login
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const loginData = {
      email: credentials.username,
      password: credentials.password,
    };

    const response: AxiosResponse<AuthResponse> = await api.post('/auth/login', loginData);
    return response.data;
  },

  // Register
  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const response: AxiosResponse<AuthResponse> = await api.post('/auth/register', userData);
    return response.data;
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/auth/me');
    return response.data;
  },

  // Update user profile
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.put('/users/me', userData);
    return response.data;
  },
};

// Medicine API
export const medicineAPI = {
  // Get all medicines
  getMedicines: async (params?: {
    search?: string;
    category_id?: number;
    min_price?: number;
    max_price?: number;
    prescription_required?: boolean;
    in_stock?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<Medicine[]> => {
    const response: AxiosResponse<Medicine[]> = await api.get('/medicines/', { params });
    return response.data;
  },

  // Get medicine by ID
  getMedicine: async (id: number): Promise<Medicine> => {
    const response: AxiosResponse<Medicine> = await api.get(`/medicines/${id}`);
    return response.data;
  },

  // Get medicine alternatives
  getMedicineAlternatives: async (id: number): Promise<Medicine[]> => {
    const response: AxiosResponse<Medicine[]> = await api.get(`/medicines/${id}/alternatives`);
    return response.data;
  },

  // Get categories
  getCategories: async (): Promise<Category[]> => {
    const response: AxiosResponse<Category[]> = await api.get('/medicines/categories/');
    return response.data;
  },
};

// Order API
export const orderAPI = {
  // Create order
  createOrder: async (orderData: {
    delivery_address: string;
    delivery_instructions?: string;
    is_emergency: boolean;
    emergency_reason?: string;
    items: Array<{ medicine_id: number; quantity: number }>;
    prescription_ids?: number[];
  }): Promise<Order> => {
    const response: AxiosResponse<Order> = await api.post('/orders/', orderData);
    return response.data;
  },

  // Get orders
  getOrders: async (params?: {
    status?: string;
    order_type?: string;
    is_emergency?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<Order[]> => {
    const response: AxiosResponse<Order[]> = await api.get('/orders/', { params });
    return response.data;
  },

  // Get order by ID
  getOrder: async (id: number): Promise<Order> => {
    const response: AxiosResponse<Order> = await api.get(`/orders/${id}`);
    return response.data;
  },

  // Update order status
  updateOrderStatus: async (id: number, status: string, notes?: string): Promise<Order> => {
    const response: AxiosResponse<Order> = await api.patch(`/orders/${id}/status`, {
      status,
      notes,
    });
    return response.data;
  },

  // Cancel order
  cancelOrder: async (id: number): Promise<{ message: string }> => {
    const response: AxiosResponse<{ message: string }> = await api.delete(`/orders/${id}`);
    return response.data;
  },

  // Upload delivery proof
  uploadDeliveryProof: async (orderId: number, file: File): Promise<{ message: string; proof_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response: AxiosResponse<{ message: string; proof_url: string }> = await api.post(`/orders/${orderId}/delivery-proof`, formData, {
      headers: { 'Content-Type': undefined },
    });
    return response.data;
  },

  // Track order
  trackOrder: async (orderId: number): Promise<Record<string, unknown>> => {
    const response: AxiosResponse<Record<string, unknown>> = await api.get(`/orders/${orderId}/track`);
    return response.data;
  },
};

// Prescription API
export const prescriptionAPI = {
  // Upload prescription
  uploadPrescription: async (formData: FormData): Promise<Prescription> => {
    const response: AxiosResponse<Prescription> = await api.post('/prescriptions/upload', formData, {
      headers: { 'Content-Type': undefined }, // Let browser set correct boundary
    });
    return response.data;
  },

  // Get prescriptions
  getPrescriptions: async (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<Prescription[]> => {
    const response: AxiosResponse<Prescription[]> = await api.get('/prescriptions/', { params });
    return response.data;
  },

  // Get prescription by ID
  getPrescription: async (id: number): Promise<Prescription> => {
    const response: AxiosResponse<Prescription> = await api.get(`/prescriptions/${id}`);
    return response.data;
  },

  // Get user's prescriptions
  getMyPrescriptions: async (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<Prescription[]> => {
    const response: AxiosResponse<Prescription[]> = await api.get('/prescriptions/user/me', { params });
    return response.data;
  },

  // Get pending prescriptions (Admin only)
  getPendingPrescriptions: async (params?: {
    limit?: number;
    offset?: number;
  }): Promise<Prescription[]> => {
    const response: AxiosResponse<Prescription[]> = await api.get('/prescriptions/admin/pending', { params });
    return response.data;
  },

  // Verify prescription (Admin only)
  verifyPrescription: async (prescriptionId: number, verificationData: {
    status: 'verified' | 'rejected';
    verification_notes?: string;
    extracted_medicines?: string;
  }): Promise<Prescription> => {
    const response: AxiosResponse<Prescription> = await api.post(`/prescriptions/${prescriptionId}/verify`, verificationData);
    return response.data;
  },
};

// User API
export const userAPI = {
  // Get all users (admin only)
  getUsers: async (params?: {
    role?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<User[]> => {
    const response: AxiosResponse<User[]> = await api.get('/users/', { params });
    return response.data;
  },

  // Update user profile
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.put('/users/me', userData);
    return response.data;
  },
};

// Categories API
export const categoryAPI = {
  // Get all categories
  getCategories: async (): Promise<Category[]> => {
    const response: AxiosResponse<Category[]> = await api.get('/categories/');
    return response.data;
  },
};

// WebSocket Service
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(private baseUrl: string, private token: string) {}

  connect(userId: number): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.baseUrl.replace('http', 'ws')}/api/v1/ws/connect?token=${this.token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(1); // userId will be handled by the backend
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  private handleMessage(message: any): void {
    switch (message.type) {
      case 'order_update':
        // Handle order status updates
        console.log('Order update:', message.data);
        // You can dispatch to a global state or emit an event
        break;
      case 'inventory_update':
        // Handle inventory updates
        console.log('Inventory update:', message.data);
        break;
      case 'prescription_update':
        // Handle prescription status updates
        console.log('Prescription update:', message.data);
        break;
      case 'connection_confirmed':
        console.log('WebSocket connection confirmed:', message);
        break;
      case 'error':
        console.error('WebSocket error:', message.message);
        break;
      default:
        console.log('Unknown WebSocket message:', message);
    }
  }

  sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Utility functions
export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const removeAuthToken = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
};

export const setUser = (user: User) => {
  localStorage.setItem('user', JSON.stringify(user));
};

export const getUser = (): User | null => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const removeUser = () => {
  localStorage.removeItem('user');
};

export default api; 