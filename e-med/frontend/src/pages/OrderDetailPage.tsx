import React, { useState, useEffect } from 'react';
import { useParams, useLocation, Link } from 'react-router-dom';
import { orderAPI } from '../services/api';
import type { Order } from '../types';
import { OrderStatus } from '../types';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';

const OrderDetailPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const location = useLocation();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelLoading, setCancelLoading] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);
  const [cancelSuccess, setCancelSuccess] = useState(false);
  const [tracking, setTracking] = useState<Record<string, any> | null>(null); // Replace 'any' with Record<string, any> for now
  const [trackingLoading, setTrackingLoading] = useState(false);
  const [proofFile, setProofFile] = useState<File | null>(null);
  const [proofUploading, setProofUploading] = useState(false);
  const [proofError, setProofError] = useState<string | null>(null);
  const [proofSuccess, setProofSuccess] = useState<string | null>(null);

  const { user } = useAuth();
  const { lastMessage } = useWebSocket();

  // Get order data from navigation state or fetch from API
  useEffect(() => {
    const fetchOrder = async () => {
      if (!orderId) return;
      try {
        setLoading(true);
        const orderData = await orderAPI.getOrder(parseInt(orderId));
        setOrder(orderData);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load order details');
      } finally {
        setLoading(false);
      }
    };
    if (location.state?.orderId === orderId) {
      setOrder({
        id: location.state.orderId,
        order_number: location.state.orderNumber,
        total_amount: location.state.total,
        status: 'pending',
        order_type: 'normal',
        subtotal: 0,
        delivery_fee: 5,
        emergency_fee: 0,
        delivery_address: '',
        delivery_instructions: '',
        is_emergency: false,
        created_at: new Date().toISOString(),
        items: [],
        user_id: 0,
        updated_at: new Date().toISOString()
      } as Order);
      setLoading(false);
    } else {
      fetchOrder();
    }
  }, [orderId, location.state]);

  // Fetch tracking info
  const fetchTracking = async () => {
    if (!orderId) return;
    setTrackingLoading(true);
    try {
      const data = await orderAPI.trackOrder(parseInt(orderId));
      setTracking(data);
    } catch (err: unknown) {
      // ignore for now
    } finally {
      setTrackingLoading(false);
    }
  };
  useEffect(() => { fetchTracking(); }, [orderId]);
  // Listen for WebSocket order/delivery updates
  useEffect(() => {
    if (!lastMessage) return;
    if (
      typeof lastMessage === 'object' &&
      lastMessage !== null &&
      'type' in lastMessage &&
      (lastMessage as any).type === 'order_update' || (lastMessage as any).type === 'delivery_update'
    ) {
      fetchOrder();
      fetchTracking();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lastMessage]);
  // Delivery proof upload handler
  const handleProofChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setProofFile(e.target.files[0]);
  };
  const handleProofUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!proofFile || !order) return;
    setProofUploading(true);
    setProofError(null);
    setProofSuccess(null);
    try {
      await orderAPI.uploadDeliveryProof(order.id, proofFile);
      setProofSuccess('Delivery proof uploaded!');
      setProofFile(null);
      fetchOrder();
      fetchTracking();
    } catch (err: unknown) {
      setProofError(err instanceof Error ? err.message : 'Failed to upload proof');
    } finally {
      setProofUploading(false);
    }
  };

  const handleCancelOrder = async () => {
    if (!order) return;
    setCancelLoading(true);
    setCancelError(null);
    setCancelSuccess(false);
    try {
      await orderAPI.cancelOrder(order.id);
      setCancelSuccess(true);
      setOrder({ ...order, status: OrderStatus.CANCELLED });
    } catch (err: unknown) {
      setCancelError(err instanceof Error ? err.message : 'Failed to cancel order');
    } finally {
      setCancelLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'preparing': return 'bg-orange-100 text-orange-800';
      case 'out_for_delivery': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
      case 'confirmed': return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
      case 'preparing': return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      );
      case 'out_for_delivery': return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      );
      case 'delivered': return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
      default: return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="text-red-800">{error || 'Order not found'}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Details</h1>
              <p className="text-gray-600">Order #{order.order_number}</p>
            </div>
            <Link
              to="/orders"
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Orders
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Order Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Status */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Status</h2>
              <div className="flex items-center space-x-3">
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                  {getStatusIcon(order.status)}
                  <span className="ml-2 capitalize">{order.status.replace('_', ' ')}</span>
                </div>
                {order.is_emergency && (
                  <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    Emergency
                  </div>
                )}
              </div>
            </div>

            {/* Order Items */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Items</h2>
              <div className="space-y-4">
                {order.items.map((item) => (
                  <div key={item.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-medium text-gray-900">
                        {item.medicine_name || `Medicine #${item.medicine_id}`}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Quantity: {item.quantity} × ${item.unit_price?.toFixed(2)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">
                        ${item.total_price?.toFixed(2)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Delivery Information */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Delivery Information</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Address</label>
                  <p className="text-gray-900">{order.delivery_address}</p>
                </div>
                {order.delivery_instructions && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Instructions</label>
                    <p className="text-gray-900">{order.delivery_instructions}</p>
                  </div>
                )}
                {order.emergency_reason && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Emergency Reason</label>
                    <p className="text-gray-900">{order.emergency_reason}</p>
                  </div>
                )}
              </div>
            </div>
            {/* Delivery Proof Section */}
            {order.delivery_proof_url && (
              <div className="bg-white rounded-xl shadow-sm border border-green-200 p-6 mt-6">
                <h2 className="text-lg font-semibold text-green-700 mb-2">Delivery Proof</h2>
                {order.delivery_proof_url.match(/\.(jpg|jpeg|png|gif)$/i) ? (
                  <img src={order.delivery_proof_url} alt="Delivery Proof" className="max-h-64 rounded shadow mb-2" />
                ) : (
                  <a href={order.delivery_proof_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">View Proof</a>
                )}
              </div>
            )}
            {/* Delivery Partner/Admin Proof Upload */}
            {user && (user.role === 'delivery_partner' || user.role === 'pharmacy_admin' || user.role === 'system_admin') && order.status === OrderStatus.OUT_FOR_DELIVERY && !order.delivery_proof_url && (
              <div className="bg-white rounded-xl shadow-sm border border-blue-200 p-6 mt-6">
                <h2 className="text-lg font-semibold text-blue-700 mb-2">Upload Delivery Proof</h2>
                <form onSubmit={handleProofUpload} className="flex flex-col gap-4">
                  <input type="file" accept="image/*,.pdf" onChange={handleProofChange} />
                  {proofError && <div className="text-red-600 text-sm">{proofError}</div>}
                  {proofSuccess && <div className="text-green-600 text-sm">{proofSuccess}</div>}
                  <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50" disabled={proofUploading || !proofFile}>{proofUploading ? 'Uploading...' : 'Upload Proof'}</button>
                </form>
              </div>
            )}
            {/* Order Tracking Section */}
            <div className="bg-white rounded-xl shadow-sm border border-purple-200 p-6 mt-6">
              <h2 className="text-lg font-semibold text-purple-700 mb-2">Order Tracking</h2>
              {trackingLoading ? (
                <div>Loading tracking info...</div>
              ) : tracking ? (
                <div className="space-y-2">
                  <div>Status: <span className="font-semibold">{tracking.status.replace('_', ' ')}</span></div>
                  <div>Created: {new Date(tracking.created_at).toLocaleString()}</div>
                  {tracking.confirmed_at && <div>Confirmed: {new Date(tracking.confirmed_at).toLocaleString()}</div>}
                  {tracking.preparing_at && <div>Preparing: {new Date(tracking.preparing_at).toLocaleString()}</div>}
                  {tracking.out_for_delivery_at && <div>Out for Delivery: {new Date(tracking.out_for_delivery_at).toLocaleString()}</div>}
                  {tracking.delivered_at && <div>Delivered: {new Date(tracking.delivered_at).toLocaleString()}</div>}
                  {tracking.delivery_partner_id && <div>Delivery Partner ID: {tracking.delivery_partner_id}</div>}
                  {tracking.delivery_proof_url && (
                    <div>Proof: <a href={tracking.delivery_proof_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">View</a></div>
                  )}
                </div>
              ) : (
                <div>No tracking info available.</div>
              )}
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 sticky top-8">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h2>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">${order.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Delivery Fee</span>
                  <span className="font-medium">${order.delivery_fee.toFixed(2)}</span>
                </div>
                {order.emergency_fee > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Emergency Fee</span>
                    <span className="font-medium text-red-600">${order.emergency_fee.toFixed(2)}</span>
                  </div>
                )}
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between text-lg font-semibold">
                    <span>Total</span>
                    <span>${order.total_amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Order Info */}
              <div className="space-y-3 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Order Date:</span>
                  <p>{new Date(order.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="font-medium">Order Type:</span>
                  <p className="capitalize">{order.order_type.replace('_', ' ')}</p>
                </div>
                {order.estimated_delivery_time && (
                  <div>
                    <span className="font-medium">Estimated Delivery:</span>
                    <p>{new Date(order.estimated_delivery_time).toLocaleString()}</p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-6 space-y-3">
                {order.status === 'pending' && (
                  <button 
                    className="w-full bg-red-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors duration-200 disabled:opacity-60"
                    onClick={handleCancelOrder}
                    disabled={cancelLoading}
                  >
                    {cancelLoading ? 'Cancelling...' : 'Cancel Order'}
                  </button>
                )}
                {cancelError && (
                  <div className="text-sm text-red-600 mt-2">{cancelError}</div>
                )}
                {cancelSuccess && (
                  <div className="text-sm text-green-600 mt-2">Order cancelled successfully.</div>
                )}
                <Link
                  to="/medicines"
                  className="block w-full text-center bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors duration-200"
                >
                  Order Again
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetailPage; 