import React, { useState, useEffect } from 'react';
import Navigation from '../components/ui/Navigation';
import MedicineCard from '../components/medicines/MedicineCard';
import MedicineFilters from '../components/medicines/MedicineFilters';
import { useCart } from '../contexts/CartContext';
import { medicineAPI } from '../services/api';
import type { Medicine, Category } from '../types';

const MedicinesPage: React.FC = () => {
  const { addToCart } = useCart();
  const [medicines, setMedicines] = useState<Medicine[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // Filter states
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });
  const [prescriptionRequired, setPrescriptionRequired] = useState<boolean | null>(null);
  const [inStockOnly, setInStockOnly] = useState(false);

  // Load medicines and categories
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [medicinesData, categoriesData] = await Promise.all([
          medicineAPI.getMedicines(),
          medicineAPI.getCategories(),
        ]);
        setMedicines(medicinesData);
        setCategories(categoriesData);
      } catch (err: any) {
        setError(err.message || 'Failed to load medicines');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Filter medicines based on current filters
  const filteredMedicines = medicines.filter(medicine => {
    // Search filter
    if (search && !medicine.name.toLowerCase().includes(search.toLowerCase()) &&
        !(medicine.generic_name && medicine.generic_name.toLowerCase().includes(search.toLowerCase())) &&
        !(medicine.manufacturer && medicine.manufacturer.toLowerCase().includes(search.toLowerCase()))) {
      return false;
    }

    // Category filter
    if (selectedCategory && medicine.category_id !== selectedCategory) {
      return false;
    }

    // Price range filter
    if (medicine.price < priceRange.min || medicine.price > priceRange.max) {
      return false;
    }

    // Prescription required filter
    if (prescriptionRequired !== null && medicine.prescription_required !== prescriptionRequired) {
      return false;
    }

    // In stock filter
    if (inStockOnly && medicine.stock_quantity <= 0) {
      return false;
    }

    return true;
  });

  const handleAddToCart = (medicineId: number, quantity: number) => {
    const medicine = medicines.find(m => m.id === medicineId);
    if (medicine) {
      addToCart(medicine, quantity);
    }
  };

  const handleClearFilters = () => {
    setSearch('');
    setSelectedCategory(null);
    setPriceRange({ min: 0, max: 1000 });
    setPrescriptionRequired(null);
    setInStockOnly(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading medicines</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 sm:px-0">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Medicine Catalog</h1>
            <p className="mt-2 text-gray-600">
              Browse our comprehensive collection of medicines and healthcare products
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Filters Sidebar */}
            <div className="lg:col-span-1">
              <MedicineFilters
                search={search}
                setSearch={setSearch}
                selectedCategory={selectedCategory}
                setSelectedCategory={setSelectedCategory}
                priceRange={priceRange}
                setPriceRange={setPriceRange}
                prescriptionRequired={prescriptionRequired}
                setPrescriptionRequired={setPrescriptionRequired}
                inStockOnly={inStockOnly}
                setInStockOnly={setInStockOnly}
                categories={categories}
                onClearFilters={handleClearFilters}
              />
            </div>

            {/* Medicines Grid */}
            <div className="lg:col-span-3">
              {/* Results Header */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-sm text-gray-600">
                    Showing {filteredMedicines.length} of {medicines.length} medicines
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Sort by:</span>
                  <select className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="name">Name</option>
                    <option value="price-low">Price: Low to High</option>
                    <option value="price-high">Price: High to Low</option>
                    <option value="stock">Stock Level</option>
                  </select>
                </div>
              </div>

              {/* Medicines Grid */}
              {filteredMedicines.length === 0 ? (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No medicines found</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Try adjusting your search or filter criteria.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {filteredMedicines.map((medicine) => (
                    <MedicineCard
                      key={medicine.id}
                      medicine={medicine}
                      onAddToCart={handleAddToCart}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MedicinesPage; 