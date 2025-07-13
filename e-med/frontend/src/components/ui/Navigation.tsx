import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useCart } from '../../contexts/CartContext';
import type { CartItem } from '../../types';

const Navigation: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const { items: cartItems } = useCart();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const cartItemCount = cartItems.reduce((total: number, item: CartItem) => total + item.quantity, 0);

  // Helper to highlight active link
  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <nav className="bg-white shadow border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                MediDash
              </span>
            </Link>
          </div>

          {/* Navigation Links */}
          {isAuthenticated && (
            <div className="flex items-center space-x-1 md:space-x-3 lg:space-x-6">
              <Link 
                to="/medicines" 
                className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center
                  ${isActive('/medicines') ? 'bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 shadow' : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'}`}
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                Medicines
              </Link>
              {/* Only show Orders for non-admins */}
              {user?.role !== 'pharmacy_admin' && (
                <Link 
                  to="/orders" 
                  className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center
                    ${isActive('/orders') ? 'bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 shadow' : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'}`}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Orders
                </Link>
              )}
              <Link 
                to="/prescriptions" 
                className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center
                  ${isActive('/prescriptions') ? 'bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 shadow' : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'}`}
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 1.343-3 3s1.343 3 3 3 3-1.343 3-3-1.343-3-3-3zm0 0V5m0 6v6m0 0h3m-3 0H9" />
                </svg>
                Prescriptions
              </Link>
              {user?.role === 'pharmacy_admin' && (
                <>
                  <Link 
                    to="/admin" 
                    className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center
                      ${isActive('/admin') ? 'bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 shadow' : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'}`}
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Admin
                  </Link>
                  <Link 
                    to="/admin/orders" 
                    className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center
                      ${isActive('/admin/orders') ? 'bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 shadow' : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'}`}
                  >
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
                    </svg>
                    Manage Orders
                  </Link>
                </>
              )}
              <Link 
                to="/cart" 
                className={`px-3 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center relative
                  ${isActive('/cart') ? 'bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 shadow' : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'}`}
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
                </svg>
                Cart
                {cartItemCount > 0 && (
                  <span className="ml-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center absolute -top-2 -right-2 shadow">
                    {cartItemCount}
                  </span>
                )}
              </Link>
            </div>
          )}

          {/* Right side */}
          <div className="flex items-center space-x-2 md:space-x-4">
            {isAuthenticated ? (
              <>
                {/* User Menu */}
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors duration-200">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-medium">
                        {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <span className="hidden md:block text-sm font-medium">{user?.full_name || user?.email}</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {/* Dropdown Menu */}
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                      <p className="font-medium">{user?.full_name}</p>
                      <p className="text-gray-500">{user?.email}</p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-200"
                    >
                      Sign out
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-2 md:space-x-4">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200"
                >
                  Sign in
                </Link>
                <Link
                  to="/register"
                  className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-md"
                >
                  Sign up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 