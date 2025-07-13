import React, { useEffect, useState } from 'react';
import { orderAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Order } from '../types';
import { Link } from 'react-router-dom';
import { useWebSocket } from '../contexts/WebSocketContext';

const MyDeliveriesPage: React.FC = () => {
  const { user } = useAuth();
  const { sendMessage, isConnected, connect } = useWebSocket();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [locationLoading, setLocationLoading] = useState<{ [orderId: number]: boolean }>({});
  const [locationError, setLocationError] = useState<{ [orderId: number]: string | null }>({});

  useEffect(() => {
    if (user && user.role === 'delivery_partner') {
      fetchMyDeliveries();
      if (!isConnected) connect();
    }
    // eslint-disable-next-line
  }, [user]);

  const fetchMyDeliveries = async () => {
    try {
      setLoading(true);
      const data = await orderAPI.getOrders({ delivery_partner_id: user?.id });
      setOrders(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load deliveries');
    } finally {
      setLoading(false);
    }
  };

  const handleShareLocation = (orderId: number) => {
    setLocationLoading(prev => ({ ...prev, [orderId]: true }));
    setLocationError(prev => ({ ...prev, [orderId]: null }));
    if (!navigator.geolocation) {
      setLocationError(prev => ({ ...prev, [orderId]: 'Geolocation not supported' }));
      setLocationLoading(prev => ({ ...prev, [orderId]: false }));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        sendMessage({
          type: 'location_update',
          data: {
            order_id: orderId,
            location: {
              lat: pos.coords.latitude,
              lng: pos.coords.longitude,
            },
          },
        });
        setLocationLoading(prev => ({ ...prev, [orderId]: false }));
      },
      (err) => {
        setLocationError(prev => ({ ...prev, [orderId]: err.message }));
        setLocationLoading(prev => ({ ...prev, [orderId]: false }));
      }
    );
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }
  if (error) {
    return <div className="min-h-screen flex items-center justify-center text-red-600">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold mb-6">My Deliveries</h1>
        {orders.length === 0 ? (
          <div className="text-gray-600">No deliveries assigned yet.</div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order #</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer Address</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {orders.map(order => (
                  <tr key={order.id}>
                    <td className="px-6 py-4 whitespace-nowrap font-semibold">{order.order_number}</td>
                    <td className="px-6 py-4 whitespace-nowrap capitalize">{order.status.replace('_', ' ')}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{order.delivery_address}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link to={`/orders/${order.id}`} className="text-blue-600 underline">View</Link>
                      {user?.role === 'delivery_partner' && (
                        <button
                          onClick={() => handleShareLocation(order.id)}
                          disabled={locationLoading[order.id]}
                          className="ml-2 px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                        >
                          {locationLoading[order.id] ? 'Sharing...' : 'Share Location'}
                        </button>
                      )}
                      {locationError[order.id] && <div className="text-xs text-red-600">{locationError[order.id]}</div>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyDeliveriesPage; 