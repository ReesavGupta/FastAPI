
import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';

const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      {/* Background Pattern */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 left-10 w-32 h-32 bg-blue-100 rounded-full opacity-20 animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-24 h-24 bg-green-100 rounded-full opacity-30 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 right-1/4 w-16 h-16 bg-blue-200 rounded-full opacity-25 animate-pulse delay-500"></div>
      </div>

      <div className="relative max-w-md w-full space-y-8">
        
        {/* Header */}
        <div className="text-center space-y-6">
          <div className="space-y-4">
            {/* Logo */}
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-200">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            
            <div className="space-y-2">
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight text-red-800">
                Welcome back
              </h1>
              <p className="text-gray-600 font-medium">
                Sign in to your MediDash account
              </p>
              
              {/* Trust Indicators */}
              <div className="flex items-center justify-center space-x-4 mt-4 text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Secure</span>
                </div>
                <div className="flex items-center space-x-1">
                  <svg className="w-3 h-3 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Licensed</span>
                </div>
                <div className="flex items-center space-x-1">
                  <svg className="w-3 h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Verified</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Login Form Card */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 space-y-6">
          <LoginForm />
          
          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500 font-medium">or</span>
            </div>
          </div>

          {/* Sign Up Link */}
          <Link
            to="/register"
            className="block w-full text-center py-3 text-sm font-medium text-gray-700 hover:text-blue-600 transition-colors duration-200 bg-gray-50 rounded-xl hover:bg-gray-100"
          >
            Don't have an account? <span className="text-blue-600 font-semibold">Sign up</span>
          </Link>
        </div>

        {/* Footer */}
        <div className="text-center pt-4">
          <p className="text-xs text-gray-500 leading-relaxed">
            By continuing, you agree to our{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors font-medium">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors font-medium">
              Privacy Policy
            </a>
          </p>
          
          {/* Medical Compliance */}
          <div className="mt-4 flex items-center justify-center space-x-4 text-xs text-gray-400">
            <span>HIPAA Compliant</span>
            <span>•</span>
            <span>FDA Approved</span>
            <span>•</span>
            <span>SSL Secured</span>
          </div>
        </div>
        
      </div>
    </div>
  );
};

export default LoginPage;
