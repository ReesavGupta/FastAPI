import React, { useState, useEffect } from 'react';
import { medicineAPI } from '../services/api';
import type { Medicine, Category } from '../types';
import MedicineCard from '../components/medicines/MedicineCard';
import MedicineFilters from '../components/medicines/MedicineFilters';

const MedicinesPage: React.FC = () => {
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(0);
  const [prescriptionRequired, setPrescriptionRequired] = useState<boolean | null>(null);
  const [inStock, setInStock] = useState<boolean | null>(null);

  // Load medicines and categories
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [medicinesData, categoriesData] = await Promise.all([
          medicineAPI.getMedicines(),
          medicineAPI.getCategories()
        ]);
        setMedicines(medicinesData);
        setCategories(categoriesData);
      } catch (err) {
        setError('Failed to load medicines. Please try again.');
        console.error('Error loading medicines:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Apply filters
  const filteredMedicines = medicines.filter(medicine => {
    // Search filter
    if (search) {
      const searchLower = search.toLowerCase();
      const matchesSearch = 
        medicine.name.toLowerCase().includes(searchLower) ||
        (medicine.generic_name && medicine.generic_name.toLowerCase().includes(searchLower)) ||
        (medicine.description && medicine.description.toLowerCase().includes(searchLower));
      if (!matchesSearch) return false;
    }

    // Category filter
    if (selectedCategory && medicine.category_id !== selectedCategory) {
      return false;
    }

    // Price filter
    if (minPrice > 0 && medicine.price < minPrice) {
      return false;
    }
    if (maxPrice > 0 && medicine.price > maxPrice) {
      return false;
    }

    // Prescription filter
    if (prescriptionRequired !== null && medicine.prescription_required !== prescriptionRequired) {
      return false;
    }

    // Stock filter
    if (inStock !== null) {
      const hasStock = medicine.stock_quantity > 0;
      if (inStock !== hasStock) {
        return false;
      }
    }

    return true;
  });

  const clearFilters = () => {
    setSearch('');
    setSelectedCategory(null);
    setMinPrice(0);
    setMaxPrice(0);
    setPrescriptionRequired(null);
    setInStock(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Medicine Catalog</h1>
          <p className="text-gray-600">Browse and order medicines for quick delivery</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <MedicineFilters
              search={search}
              setSearch={setSearch}
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              minPrice={minPrice}
              setMinPrice={setMinPrice}
              maxPrice={maxPrice}
              setMaxPrice={setMaxPrice}
              prescriptionRequired={prescriptionRequired}
              setPrescriptionRequired={setPrescriptionRequired}
              inStock={inStock}
              setInStock={setInStock}
              categories={categories}
              onClearFilters={clearFilters}
            />
          </div>

          {/* Medicines Grid */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {filteredMedicines.length} {filteredMedicines.length === 1 ? 'medicine' : 'medicines'} found
                </h2>
                {filteredMedicines.length !== medicines.length && (
                  <p className="text-sm text-gray-500 mt-1">
                    Showing filtered results
                  </p>
                )}
              </div>
            </div>

            {/* Medicines Grid */}
            {filteredMedicines.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredMedicines.map((medicine) => (
                  <MedicineCard key={medicine.id} medicine={medicine} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No medicines found</h3>
                <p className="text-gray-500 mb-4">
                  Try adjusting your filters or search terms
                </p>
                <button
                  onClick={clearFilters}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicinesPage; 