import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';

const OrderNotificationListener: React.FC = () => {
  const { user } = useAuth();
  const { lastMessage } = useWebSocket();
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    if (window.Notification && Notification.permission === 'default') {
      setShowBanner(true);
    }
  }, []);

  // Show notification on order_update
  useEffect(() => {
    if (
      lastMessage &&
      typeof lastMessage === 'object' &&
      lastMessage !== null &&
      'type' in lastMessage &&
      lastMessage.type === 'order_update' &&
      lastMessage.data &&
      user &&
      (lastMessage.data.user_id === undefined || lastMessage.data.user_id === user.id)
    ) {
      const status = lastMessage.data.status?.replace('_', ' ');
      const orderId = lastMessage.data.order_id;
      const message = `Your order #${orderId} status changed to ${status}`;
      if (window.Notification && Notification.permission === 'granted') {
        new Notification('Order Status Update', { body: message });
      }
    }
  }, [lastMessage, user]);

  const handleEnableNotifications = () => {
    if (window.Notification && Notification.permission === 'default') {
      Notification.requestPermission().then(() => {
        setShowBanner(false);
      });
    } else {
      setShowBanner(false);
    }
  };

  if (showBanner) {
    return (
      <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-3 rounded shadow-lg z-50 flex items-center space-x-4">
        <span>Enable browser notifications for order updates?</span>
        <button
          className="bg-white text-blue-600 px-3 py-1 rounded font-semibold hover:bg-blue-100"
          onClick={handleEnableNotifications}
        >
          Enable
        </button>
        <button
          className="ml-2 text-white hover:text-gray-200"
          onClick={() => setShowBanner(false)}
        >
          Dismiss
        </button>
      </div>
    );
  }

  return null;
};

export default OrderNotificationListener; 