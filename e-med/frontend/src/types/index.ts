// User Types
export interface User {
  id: number;
  email: string;
  phone: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  address?: string;
  emergency_contact?: string;
  medical_info?: string;
  created_at: string;
  updated_at?: string;
  vehicle_number?: string;
  is_available?: boolean;
}

export enum UserRole {
  CUSTOMER = "customer",
  PHARMACY_ADMIN = "pharmacy_admin",
  SYSTEM_ADMIN = "system_admin",
  DELIVERY_PARTNER = "delivery_partner"
}

// Authentication Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  phone: string;
  password: string;
  full_name: string;
  role?: UserRole;
  address?: string;
  emergency_contact?: string;
  medical_info?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Medicine Types
export interface Category {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Medicine {
  id: number;
  name: string;
  generic_name?: string;
  description?: string;
  manufacturer?: string;
  dosage_form?: string;
  strength?: string;
  prescription_required: boolean;
  price: number;
  stock_quantity: number;
  min_stock_level: number;
  is_active: boolean;
  category_id?: number;
  category?: Category;
  created_at: string;
  updated_at?: string;
}

// Order Types
export enum OrderStatus {
  PENDING = "pending",
  CONFIRMED = "confirmed",
  PREPARING = "preparing",
  OUT_FOR_DELIVERY = "out_for_delivery",
  DELIVERED = "delivered",
  CANCELLED = "cancelled",
  FAILED = "failed"
}

export enum OrderType {
  NORMAL = "normal",
  EMERGENCY = "emergency",
  PRESCRIPTION = "prescription"
}

export interface OrderItem {
  id: number;
  medicine_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  medicine_name?: string;
}

export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  delivery_partner_id?: number;
  status: OrderStatus;
  order_type: OrderType;
  subtotal: number;
  delivery_fee: number;
  emergency_fee: number;
  total_amount: number;
  delivery_address: string;
  delivery_instructions?: string;
  is_emergency: boolean;
  emergency_reason?: string;
  estimated_delivery_time?: string;
  actual_delivery_time?: string;
  created_at: string;
  updated_at?: string;
  items: OrderItem[];
  delivery_proof_url?: string;
}

// Prescription Types
export enum PrescriptionStatus {
  PENDING = "pending",
  VERIFIED = "verified",
  REJECTED = "rejected",
  EXPIRED = "expired"
}

export interface Prescription {
  id: number;
  user_id: number;
  verified_by?: number;
  doctor_name?: string;
  hospital_name?: string;
  prescription_date?: string;
  expiry_date?: string;
  file_url: string;
  file_name?: string;
  file_size?: number;
  status: PrescriptionStatus;
  verification_notes?: string;
  extracted_medicines?: string;
  verified_at?: string;
  created_at: string;
  updated_at?: string;
}

// Cart Types
export interface CartItem {
  id: number;
  medicine_id: number;
  quantity: number;
  medicine_name?: string;
  medicine_price?: number;
  total_price?: number;
  created_at: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  user_id?: number;
  user_type?: string;
  role?: string;
  full_name?: string;
}

export interface OrderUpdateMessage extends WebSocketMessage {
  type: 'order_update';
  data: {
    order_id: number;
    status: string;
    updated_at: string;
    notes?: string;
  };
}

export interface InventoryUpdateMessage extends WebSocketMessage {
  type: 'inventory_update';
  data: {
    medicine_id: number;
    medicine_name: string;
    new_stock: number;
    updated_at: string;
  };
}

export interface PrescriptionUpdateMessage extends WebSocketMessage {
  type: 'prescription_update';
  data: {
    prescription_id: number;
    status: string;
    updated_at: string;
    notes?: string;
  };
}

export interface ConnectionMessage extends WebSocketMessage {
  type: 'connection_confirmed';
  user_id: number;
  user_type: string;
  role: string;
  full_name?: string;
}

export interface ErrorMessage extends WebSocketMessage {
  type: 'error';
  message: string;
}

// Form Types
export interface LoginFormData {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterFormData {
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
  full_name: string;
  address?: string;
  emergency_contact?: string;
  medical_info?: string;
  agreeToTerms: boolean;
  role?: string;
}

// UI Types
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
} 