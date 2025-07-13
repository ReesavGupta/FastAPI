import React from 'react';
import type { Category } from '../../types';

interface MedicineFiltersProps {
  search: string;
  setSearch: (search: string) => void;
  selectedCategory: number | null;
  setSelectedCategory: (categoryId: number | null) => void;
  minPrice: number;
  setMinPrice: (price: number) => void;
  maxPrice: number;
  setMaxPrice: (price: number) => void;
  prescriptionRequired: boolean | null;
  setPrescriptionRequired: (required: boolean | null) => void;
  inStock: boolean | null;
  setInStock: (inStock: boolean | null) => void;
  categories: Category[];
  onClearFilters: () => void;
}

const MedicineFilters: React.FC<MedicineFiltersProps> = ({
  search,
  setSearch,
  selectedCategory,
  setSelectedCategory,
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  prescriptionRequired,
  setPrescriptionRequired,
  inStock,
  setInStock,
  categories,
  onClearFilters,
}) => {
  const hasActiveFilters = search || selectedCategory || minPrice || maxPrice || prescriptionRequired !== null || inStock !== null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-6">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search Medicines
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, generic name, or description..."
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
            />
          </div>
        </div>

        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            value={selectedCategory || ''}
            onChange={(e) => setSelectedCategory(e.target.value ? Number(e.target.value) : null)}
            className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        {/* Price Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Price Range
          </label>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Min Price</label>
              <input
                type="number"
                value={minPrice || ''}
                onChange={(e) => setMinPrice(e.target.value ? Number(e.target.value) : 0)}
                placeholder="0"
                min="0"
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Max Price</label>
              <input
                type="number"
                value={maxPrice || ''}
                onChange={(e) => setMaxPrice(e.target.value ? Number(e.target.value) : 0)}
                placeholder="1000"
                min="0"
                className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
              />
            </div>
          </div>
        </div>

        {/* Prescription Required */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Prescription Required
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="prescription"
                checked={prescriptionRequired === null}
                onChange={() => setPrescriptionRequired(null)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">All Medicines</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="prescription"
                checked={prescriptionRequired === true}
                onChange={() => setPrescriptionRequired(true)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Prescription Required</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="prescription"
                checked={prescriptionRequired === false}
                onChange={() => setPrescriptionRequired(false)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Over the Counter</span>
            </label>
          </div>
        </div>

        {/* Stock Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Stock Status
          </label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="stock"
                checked={inStock === null}
                onChange={() => setInStock(null)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">All Items</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="stock"
                checked={inStock === true}
                onChange={() => setInStock(true)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">In Stock Only</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="stock"
                checked={inStock === false}
                onChange={() => setInStock(false)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">Out of Stock</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MedicineFilters; 