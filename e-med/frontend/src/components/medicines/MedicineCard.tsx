import React from 'react';
import type { Medicine } from '../../types';

interface MedicineCardProps {
  medicine: Medicine;
  onAddToCart: (medicineId: number, quantity: number) => void;
}

const MedicineCard: React.FC<MedicineCardProps> = ({ medicine, onAddToCart }) => {
  const [quantity, setQuantity] = React.useState(1);
  const [isAddingToCart, setIsAddingToCart] = React.useState(false);

  const handleAddToCart = () => {
    setIsAddingToCart(true);
    onAddToCart(medicine.id, quantity);
    setTimeout(() => setIsAddingToCart(false), 1000);
  };

  const isOutOfStock = medicine.stock_quantity <= 0;
  const isLowStock = medicine.stock_quantity <= medicine.min_stock_level;

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden">
      {/* Medicine Image Placeholder */}
      <div className="h-48 bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <svg className="h-16 w-16 text-blue-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
          <p className="text-sm text-blue-600 font-medium">Medicine Image</p>
        </div>
      </div>

      <div className="p-4">
        {/* Medicine Name and Generic Name */}
        <div className="mb-2">
          <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">{medicine.name}</h3>
          {medicine.generic_name && (
            <p className="text-sm text-gray-600 mt-1">Generic: {medicine.generic_name}</p>
          )}
        </div>

        {/* Manufacturer and Strength */}
        <div className="mb-3">
          {medicine.manufacturer && (
            <p className="text-sm text-gray-600">By {medicine.manufacturer}</p>
          )}
          {medicine.strength && (
            <p className="text-sm text-gray-600">{medicine.strength}</p>
          )}
        </div>

        {/* Description */}
        {medicine.description && (
          <p className="text-sm text-gray-700 mb-3 line-clamp-2">{medicine.description}</p>
        )}

        {/* Price and Stock Status */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-green-600">${medicine.price.toFixed(2)}</span>
            {medicine.prescription_required && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Prescription Required
              </span>
            )}
          </div>
          
          {/* Stock Status */}
          <div className="flex items-center space-x-1">
            {isOutOfStock ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Out of Stock
              </span>
            ) : isLowStock ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Low Stock
              </span>
            ) : (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                In Stock
              </span>
            )}
          </div>
        </div>

        {/* Stock Quantity */}
        <div className="mb-3">
          <p className="text-sm text-gray-600">
            Available: {medicine.stock_quantity} units
          </p>
        </div>

        {/* Add to Cart Section */}
        {!isOutOfStock && (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <label htmlFor={`quantity-${medicine.id}`} className="text-sm font-medium text-gray-700">
                Quantity:
              </label>
              <select
                id={`quantity-${medicine.id}`}
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[...Array(Math.min(10, medicine.stock_quantity))].map((_, i) => (
                  <option key={i + 1} value={i + 1}>
                    {i + 1}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={handleAddToCart}
              disabled={isAddingToCart}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200 flex items-center justify-center"
            >
              {isAddingToCart ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Adding...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
                  </svg>
                  Add to Cart
                </>
              )}
            </button>
          </div>
        )}

        {/* Out of Stock Message */}
        {isOutOfStock && (
          <div className="text-center py-2">
            <p className="text-sm text-gray-500">Currently out of stock</p>
            <button className="text-sm text-blue-600 hover:text-blue-800 mt-1">
              Notify when available
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MedicineCard; 