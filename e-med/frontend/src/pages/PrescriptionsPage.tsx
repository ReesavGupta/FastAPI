import React from 'react';
import Navigation from '../components/ui/Navigation';

const PrescriptionsPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Prescription Management</h2>
              <p className="text-gray-600">Upload and manage your prescriptions</p>
              <p className="text-sm text-gray-500 mt-2">Coming soon...</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PrescriptionsPage; 