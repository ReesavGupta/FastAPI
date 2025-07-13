import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CartProvider } from './contexts/CartContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/ui/Navigation';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import MedicinesPage from './pages/MedicinesPage';
import OrdersPage from './pages/OrdersPage';
import PrescriptionsPage from './pages/PrescriptionsPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import OrderDetailPage from './pages/OrderDetailPage';
import AdminDashboard from './pages/AdminDashboard';
import AdminOrdersPage from './pages/AdminOrdersPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import OrderNotificationListener from './components/OrderNotificationListener';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <WebSocketProvider>
          <OrderNotificationListener />
          <Router>
            <div className="min-h-screen bg-gray-50">
              <Navigation />
              <main className="container mx-auto px-4 py-8">
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route 
                    path="/medicines" 
                    element={
                      <ProtectedRoute>
                        <MedicinesPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/orders" 
                    element={
                      <ProtectedRoute>
                        <OrdersPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/orders/:orderId" 
                    element={
                      <ProtectedRoute>
                        <OrderDetailPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/prescriptions" 
                    element={
                      <ProtectedRoute>
                        <PrescriptionsPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/cart" 
                    element={
                      <ProtectedRoute>
                        <CartPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/checkout" 
                    element={
                      <ProtectedRoute>
                        <CheckoutPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/admin" 
                    element={
                      <ProtectedRoute requiredRole="pharmacy_admin">
                        <AdminDashboard />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/admin/orders" 
                    element={
                      <ProtectedRoute requiredRole="pharmacy_admin">
                        <AdminOrdersPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route path="/" element={<Navigate to="/medicines" replace />} />
                </Routes>
              </main>
            </div>
          </Router>
        </WebSocketProvider>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
