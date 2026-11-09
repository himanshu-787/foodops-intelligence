import { useEffect, useState } from "react";
import "./App.css";

import { api } from "./api";
import { useAuth } from "./auth/AuthContext";
import { Cart, type CartLine } from "./components/Cart";
import { CuisineFilter } from "./components/CuisineFilter";
import { LoginForm } from "./components/LoginForm";
import { MenuList, type MenuItem } from "./components/MenuList";
import { Pagination } from "./components/Pagination";
import { RestaurantCard, type Restaurant } from "./components/RestaurantCard";
import { SearchBar } from "./components/SearchBar";
import { useDebounce } from "./hooks/useDebounce";

const API_URL = "http://127.0.0.1:8000";
const PAGE_SIZE = 12;
const MAX_QTY_PER_ITEM = 20;
const MIN_SEARCH_LENGTH = 2; // backend returns 422 for shorter queries

type RestaurantPage = {
  total: number;
  items: Restaurant[];
};

const maxQty = (item: MenuItem) => Math.min(MAX_QTY_PER_ITEM, item.stock);

function App() {
  const { email, token, loading: authLoading, logout } = useAuth();

  // ---------- Cart and order ----------
  const [cart, setCart] = useState<Record<number, CartLine>>({});
  const [placing, setPlacing] = useState(false);
  const [orderMsg, setOrderMsg] = useState<string | null>(null);
  const [orderErr, setOrderErr] = useState<string | null>(null);
  const [menuRefresh, setMenuRefresh] = useState(0);

  // One order attempt = one idempotency key. If the cart changes, make a new key.
  const [idemKey, setIdemKey] = useState(() => crypto.randomUUID());
  const resetIdemKey = () => setIdemKey(crypto.randomUUID());

  function addToCart(item: MenuItem) {
    setCart((prev) => {
      const current = prev[item.id]?.quantity ?? 0;
      const quantity = Math.min(current + 1, maxQty(item));
      return { ...prev, [item.id]: { item, quantity } };
    });
    resetIdemKey();
    setOrderMsg(null);
  }

  function changeQty(itemId: number, delta: number) {
    setCart((prev) => {
      const line = prev[itemId];
      if (!line) return prev;

      const quantity = Math.min(line.quantity + delta, maxQty(line.item));
      if (quantity <= 0) {
        const { [itemId]: _removed, ...rest } = prev;
        return rest;
      }
      return { ...prev, [itemId]: { ...line, quantity } };
    });
    resetIdemKey();
  }

  async function placeOrder() {
    if (placing) return; // guard against double click
    setPlacing(true);
    setOrderErr(null);
    setOrderMsg(null);

    try {
      const body = {
        items: Object.values(cart).map((line) => ({
          menu_item_id: line.item.id,
          quantity: line.quantity,
        })),
      };

      const order = await api<{ id: number; total: number }>(
        "/orders",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Idempotency-Key": idemKey,
          },
          body: JSON.stringify(body),
        },
        token,
      );

      setOrderMsg(`Order #${order.id} placed! Total ₹${order.total}`);
      setCart({});
      resetIdemKey(); // success: use a new key for the next order
    } catch (err) {
      // On failure the key stays the same, so retrying is safe
      setOrderErr(err instanceof Error ? err.message : "Order failed");
    } finally {
      setMenuRefresh((n) => n + 1); // reload stock either way
      setPlacing(false);
    }
  }

  // ---------- Restaurants: search, filter, pagination ----------
  const [query, setQuery] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [page, setPage] = useState(1);

  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 400);

  useEffect(() => {
    const controller = new AbortController();

    const params = new URLSearchParams({
      page: String(page),
      page_size: String(PAGE_SIZE),
    });
    const q = debouncedQuery.trim();
    if (q.length >= MIN_SEARCH_LENGTH) params.set("q", q);
    if (cuisine) params.set("cuisine", cuisine);

    setLoading(true);
    setError(null);

    fetch(`${API_URL}/restaurants?${params}`, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json() as Promise<RestaurantPage>;
      })
      .then((data) => {
        setRestaurants(data.items);
        setTotal(data.total);
      })
      .catch((err) => {
        if (err.name !== "AbortError") setError(err.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    // If a filter changes before this request ends, cancel the old request
    return () => controller.abort();
  }, [debouncedQuery, cuisine, page]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  // When a filter changes, go back to page 1
  function handleQueryChange(value: string) {
    setQuery(value);
    setPage(1);
  }

  function handleCuisineChange(value: string) {
    setCuisine(value);
    setPage(1);
  }

  return (
    <div className="container">
      <div className="header">
        <h1>FoodOps 🍽️</h1>
        {email && (
          <div>
            <span>Hi, {email} </span>
            <button className="btn" onClick={logout}>
              Logout
            </button>
          </div>
        )}
      </div>

      {!authLoading && !email && <LoginForm />}

      <h2>Menu</h2>
      <MenuList refreshKey={menuRefresh} onAdd={addToCart} />

      <Cart
        lines={Object.values(cart)}
        placing={placing}
        message={orderMsg}
        error={orderErr}
        loggedIn={Boolean(email)}
        onChangeQty={changeQty}
        onPlaceOrder={placeOrder}
      />

      <h2>Restaurants</h2>
      <SearchBar value={query} onChange={handleQueryChange} />
      <CuisineFilter value={cuisine} onChange={handleCuisineChange} />

      <p>{total} restaurants found</p>

      {error && <p className="error">Error: {error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && !error && restaurants.length === 0 && (
        <p>No restaurants found. Try changing the filters.</p>
      )}

      <div className="grid">
        {restaurants.map((r) => (
          <RestaurantCard key={r.id} restaurant={r} />
        ))}
      </div>

      <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </div>
  );
}

export default App;