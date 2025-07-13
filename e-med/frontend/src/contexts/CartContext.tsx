import React, { createContext, useContext, useState, useEffect } from 'react';
import type { Medicine, CartItem } from '../types';

interface CartContextType {
  items: CartItem[];
  addToCart: (medicine: Medicine, quantity: number) => void;
  removeFromCart: (medicineId: number) => void;
  updateQuantity: (medicineId: number, quantity: number) => void;
  clearCart: () => void;
  getCartTotal: () => number;
  getCartItemCount: () => number;
  isInCart: (medicineId: number) => boolean;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

interface CartProviderProps {
  children: React.ReactNode;
}

export const CartProvider: React.FC<CartProviderProps> = ({ children }) => {
  const [items, setItems] = useState<CartItem[]>([]);

  // Load cart from localStorage on mount
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      try {
        setItems(JSON.parse(savedCart));
      } catch (error) {
        console.error('Error loading cart from localStorage:', error);
        localStorage.removeItem('cart');
      }
    }
  }, []);

  // Save cart to localStorage whenever items change
  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(items));
  }, [items]);

  const addToCart = (medicine: Medicine, quantity: number) => {
    console.log('addToCart called with:', { medicine, quantity });
    setItems(prevItems => {
      console.log('Previous items:', prevItems);
      const existingItem = prevItems.find(item => item.medicine_id === medicine.id);
      
      if (existingItem) {
        console.log('Item already exists, updating quantity');
        // Update quantity if item already exists
        return prevItems.map(item =>
          item.medicine_id === medicine.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      } else {
        console.log('Adding new item to cart');
        // Add new item
        const newItem: CartItem = {
          id: Date.now(), // Temporary ID
          medicine_id: medicine.id,
          quantity,
          medicine_name: medicine.name,
          medicine_price: medicine.price,
          total_price: medicine.price * quantity,
          created_at: new Date().toISOString(),
        };
        console.log('New item created:', newItem);
        return [...prevItems, newItem];
      }
    });
  };

  const removeFromCart = (medicineId: number) => {
    setItems(prevItems => prevItems.filter(item => item.medicine_id !== medicineId));
  };

  const updateQuantity = (medicineId: number, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(medicineId);
      return;
    }

    setItems(prevItems =>
      prevItems.map(item =>
        item.medicine_id === medicineId
          ? { ...item, quantity, total_price: (item.medicine_price || 0) * quantity }
          : item
      )
    );
  };

  const clearCart = () => {
    setItems([]);
  };

  const getCartTotal = () => {
    return items.reduce((total, item) => total + (item.total_price || 0), 0);
  };

  const getCartItemCount = () => {
    return items.reduce((count, item) => count + item.quantity, 0);
  };

  const isInCart = (medicineId: number) => {
    return items.some(item => item.medicine_id === medicineId);
  };

  const value: CartContextType = {
    items,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartTotal,
    getCartItemCount,
    isInCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}; 