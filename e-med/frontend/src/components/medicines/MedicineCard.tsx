import React from 'react';
import type { Medicine } from '../../types';
import { useCart } from '../../contexts/CartContext';

interface MedicineCardProps {
  medicine: Medicine;
}

const MedicineCard: React.FC<MedicineCardProps> = ({ medicine }) => {
  const { addToCart, isInCart } = useCart();
  const isInCartItem = isInCart(medicine.id);

  const handleAddToCart = () => {
    console.log('Adding to cart:', medicine);
    console.log('Current cart state before adding:', isInCartItem);
    addToCart(medicine, 1);
    console.log('Add to cart function called');
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all duration-300 overflow-hidden group">
      {/* Medicine Image Placeholder */}
      <div className="h-48 bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center relative overflow-hidden">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        
        {/* Stock Badge */}
        <div className="absolute top-3 right-3">
          {medicine.stock_quantity > 0 ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              In Stock
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Out of Stock
            </span>
          )}
        </div>

        {/* Prescription Badge */}
        {medicine.prescription_required && (
          <div className="absolute top-3 left-3">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
              Prescription Required
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Category */}
        {medicine.category && (
          <div className="mb-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {medicine.category.name}
            </span>
          </div>
        )}

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors duration-200">
          {medicine.name}
        </h3>

        {/* Generic Name */}
        {medicine.generic_name && (
          <p className="text-sm text-gray-600 mb-3">
            {medicine.generic_name}
          </p>
        )}

        {/* Description */}
        {medicine.description && (
          <p className="text-sm text-gray-500 mb-4 line-clamp-2">
            {medicine.description}
          </p>
        )}

        {/* Price and Stock */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-gray-900">
              ${medicine.price.toFixed(2)}
            </span>
          </div>
          
          <div className="text-sm text-gray-500">
            {medicine.stock_quantity > 0 ? (
              <span className="text-green-600 font-medium">
                {medicine.stock_quantity} available
              </span>
            ) : (
              <span className="text-red-600 font-medium">
                Out of stock
              </span>
            )}
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleAddToCart}
          disabled={medicine.stock_quantity === 0 || isInCartItem}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
            medicine.stock_quantity === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : isInCartItem
              ? 'bg-green-100 text-green-700 border border-green-200'
              : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 shadow-md hover:shadow-lg transform hover:-translate-y-0.5'
          }`}
        >
          {medicine.stock_quantity === 0 ? (
            'Out of Stock'
          ) : isInCartItem ? (
            <span className="flex items-center justify-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Added to Cart
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
              </svg>
              Add to Cart
            </span>
          )}
        </button>
      </div>
    </div>
  );
};

export default MedicineCard; 