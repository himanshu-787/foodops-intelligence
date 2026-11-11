import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth/AuthContext";

type Order = {
  id: number;
  status: string;
  total: number;
  items: { menu_item_id: number; quantity: number; price_at_order: number }[];
};

const STATUS_LABEL: Record<string, string> = {
  PLACED: "🟡 Placed",
  ACCEPTED: "🟠 Accepted",
  PREPARING: "👨‍🍳 Preparing",
  OUT_FOR_DELIVERY: "🛵 Out for delivery",
  DELIVERED: "✅ Delivered",
  CANCELLED: "❌ Cancelled",
};

export function MyOrders() {
  const { email, token, loading: authLoading } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api<Order[]>("/orders", {}, token)
      .then(setOrders)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (authLoading || loading) return <p>Loading...</p>;
  if (!email) return <p>Orders dekhne ke liye pehle <Link to="/">login</Link> karo.</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>My Orders</h2>
      {orders.length === 0 && <p>Abhi koi order nahi.</p>}
      {orders.map((o) => (
        <div className="card order-card" key={o.id}>
          <div className="order-head">
            <b>Order #{o.id}</b>
            <span>{STATUS_LABEL[o.status] ?? o.status}</span>
          </div>
          <p>
            {o.items.reduce((n, i) => n + i.quantity, 0)} items, total ₹{o.total}
          </p>
        </div>
      ))}
    </div>
  );
}