import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';
import { WebSocketService } from '../services/api';
import type { WebSocketMessage, OrderUpdateMessage, InventoryUpdateMessage, PrescriptionUpdateMessage } from '../types';

interface WebSocketContextType {
  isConnected: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  lastMessage: WebSocketMessage | null;
  isEnabled: boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [isEnabled, setIsEnabled] = useState(false); // Disable by default
  const wsServiceRef = useRef<WebSocketService | null>(null);

  useEffect(() => {
    // Only try to connect if WebSocket is enabled and user is authenticated
    if (isEnabled && isAuthenticated && user) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isEnabled, isAuthenticated, user]);

  const connect = async () => {
    try {
      if (!user || !isEnabled) return;

      const token = localStorage.getItem('access_token');
      if (!token) return;

      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      wsServiceRef.current = new WebSocketService(baseUrl, token);

      // Override the handleMessage method to update our state
      const originalHandleMessage = (wsServiceRef.current as any).handleMessage;
      (wsServiceRef.current as any).handleMessage = (message: any) => {
        setLastMessage(message);
        originalHandleMessage.call(wsServiceRef.current, message);
      };

      await wsServiceRef.current.connect(user.id);
      setIsConnected(true);
      console.log('WebSocket connected successfully');
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnected(false);
      // Disable WebSocket after failed attempts
      setIsEnabled(false);
    }
  };

  const disconnect = () => {
    if (wsServiceRef.current) {
      wsServiceRef.current.disconnect();
      wsServiceRef.current = null;
    }
    setIsConnected(false);
    setLastMessage(null);
  };

  const sendMessage = (message: any) => {
    if (wsServiceRef.current && isConnected) {
      wsServiceRef.current.sendMessage(message);
    }
  };

  const value: WebSocketContextType = {
    isConnected,
    connect,
    disconnect,
    sendMessage,
    lastMessage,
    isEnabled,
  };

  return <WebSocketContext.Provider value={value}>{children}</WebSocketContext.Provider>;
}; 