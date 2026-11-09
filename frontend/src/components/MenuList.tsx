import { useEffect, useState } from "react";
import { api } from "../api";

export type MenuItem = {
  id: number;
  name: string;
  price: number;
  is_veg: boolean;
  stock: number;
};

export function MenuList() {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<MenuItem[]>("/menu")
      .then(setItems)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Menu load ho raha hai...</p>;
  if (error) return <p className="error">Error: {error}</p>;
  if (items.length === 0) return <p>Menu khaali hai. Backend mein items add karo.</p>;

  return (
    <div className="grid">
      {items.map((item) => (
        <div className="card" key={item.id}>
          <h3>{item.name}</h3>
          <p>{item.is_veg ? "🟢 Veg" : "🔴 Non-veg"}</p>
          <p>₹{item.price}</p>
          <p>{item.stock > 0 ? `Stock: ${item.stock}` : "❌ Out of stock"}</p>
        </div>
      ))}
    </div>
  );
}