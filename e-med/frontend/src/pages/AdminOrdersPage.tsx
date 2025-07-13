import React, { useEffect, useState } from 'react';
import { orderAPI } from '../services/api';
import type { Order, OrderStatus, User } from '../types';
import { OrderStatus as OrderStatusEnum } from '../types';
import { userAPI } from '../services/api';

const AdminOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [deliveryPartners, setDeliveryPartners] = useState<User[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<{ [orderId: number]: number }>({});
  const [assignLoadingId, setAssignLoadingId] = useState<number | null>(null);
  const [assignError, setAssignError] = useState<string | null>(null);

  useEffect(() => {
    fetchOrders();
    fetchDeliveryPartners();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await orderAPI.getOrders();
      setOrders(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const fetchDeliveryPartners = async () => {
    try {
      const users = await userAPI.getUsers({ role: 'delivery_partner' });
      setDeliveryPartners(Array.isArray(users) ? users : []);
    } catch (err) {
      setDeliveryPartners([]);
    }
  };

  const handleStatusUpdate = async (orderId: number, status: OrderStatus, notes?: string) => {
    setActionLoadingId(orderId);
    setActionError(null);
    try {
      await orderAPI.updateOrderStatus(orderId, status, notes);
      await fetchOrders();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : 'Failed to update order status');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleAssignPartner = async (orderId: number) => {
    if (!selectedPartner[orderId]) return;
    setAssignLoadingId(orderId);
    setAssignError(null);
    try {
      await orderAPI.assignDeliveryPartner(orderId, selectedPartner[orderId]);
      await fetchOrders();
    } catch (err: unknown) {
      setAssignError(err instanceof Error ? err.message : 'Failed to assign delivery partner');
    } finally {
      setAssignLoadingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <span className="text-red-800">{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Management</h1>
          <p className="text-gray-600">View and manage all orders</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assign Partner</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {orders.map(order => (
                <tr key={order.id}>
                  <td className="px-6 py-4 whitespace-nowrap font-semibold">{order.order_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{order.user_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap capitalize">{order.status.replace('_', ' ')}</td>
                  <td className="px-6 py-4 whitespace-nowrap capitalize">{order.order_type.replace('_', ' ')}</td>
                  <td className="px-6 py-4 whitespace-nowrap">${order.total_amount.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{new Date(order.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap space-x-2">
                    {order.status === OrderStatusEnum.PENDING && (
                      <>
                        <button
                          onClick={() => handleStatusUpdate(order.id, OrderStatusEnum.CONFIRMED)}
                          disabled={actionLoadingId === order.id}
                          className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                        >
                          {actionLoadingId === order.id ? 'Accepting...' : 'Accept'}
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(order.id, OrderStatusEnum.CANCELLED)}
                          disabled={actionLoadingId === order.id}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
                        >
                          {actionLoadingId === order.id ? 'Declining...' : 'Decline'}
                        </button>
                      </>
                    )}
                    {order.status === OrderStatusEnum.CONFIRMED && (
                      <button
                        onClick={() => handleStatusUpdate(order.id, OrderStatusEnum.PREPARING)}
                        disabled={actionLoadingId === order.id}
                        className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
                      >
                        {actionLoadingId === order.id ? 'Updating...' : 'Mark Preparing'}
                      </button>
                    )}
                    {order.status === OrderStatusEnum.PREPARING && (
                      <button
                        onClick={() => handleStatusUpdate(order.id, OrderStatusEnum.OUT_FOR_DELIVERY)}
                        disabled={actionLoadingId === order.id}
                        className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                      >
                        {actionLoadingId === order.id ? 'Updating...' : 'Out for Delivery'}
                      </button>
                    )}
                    {order.status === OrderStatusEnum.OUT_FOR_DELIVERY && (
                      <button
                        onClick={() => handleStatusUpdate(order.id, OrderStatusEnum.DELIVERED)}
                        disabled={actionLoadingId === order.id}
                        className="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
                      >
                        {actionLoadingId === order.id ? 'Updating...' : 'Mark Delivered'}
                      </button>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {(!order.delivery_partner_id && (order.status === OrderStatusEnum.PREPARING || order.status === OrderStatusEnum.CONFIRMED)) ? (
                      <div className="flex items-center space-x-2">
                        <select
                          className="border rounded px-2 py-1"
                          value={selectedPartner[order.id] || ''}
                          onChange={e => setSelectedPartner(prev => ({ ...prev, [order.id]: Number(e.target.value) }))}
                        >
                          <option value="">Select Partner</option>
                          {deliveryPartners.map(partner => (
                            <option key={partner.id} value={partner.id}>{partner.full_name} ({partner.phone})</option>
                          ))}
                        </select>
                        <button
                          onClick={() => handleAssignPartner(order.id)}
                          disabled={assignLoadingId === order.id || !selectedPartner[order.id]}
                          className="px-3 py-1 bg-indigo-500 text-white rounded hover:bg-indigo-600 disabled:opacity-50"
                        >
                          {assignLoadingId === order.id ? 'Assigning...' : 'Assign'}
                        </button>
                      </div>
                    ) : order.delivery_partner_id ? (
                      <span className="text-green-700 font-medium">Assigned</span>
                    ) : (
                      <span className="text-gray-400">N/A</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {actionError && <div className="p-4 text-red-600 text-sm">{actionError}</div>}
          {assignError && <div className="p-4 text-red-600 text-sm">{assignError}</div>}
        </div>
      </div>
    </div>
  );
};

export default AdminOrdersPage; 