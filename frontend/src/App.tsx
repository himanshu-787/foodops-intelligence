import { useEffect, useState } from "react";
import "./App.css";
import { useAuth } from "./auth/AuthContext";
import { LoginForm } from "./components/LoginForm";
import { MenuList } from "./components/MenuList";
import { CuisineFilter } from "./components/CuisineFilter";
import { Pagination } from "./components/Pagination";
import { RestaurantCard, type Restaurant } from "./components/RestaurantCard";
import { SearchBar } from "./components/SearchBar";
import { useDebounce } from "./hooks/useDebounce";


const API_URL = "http://127.0.0.1:8000";
const PAGE_SIZE = 12;

type RestaurantPage = {
  total: number;
  items: Restaurant[];
};

function App() {
  const { email, loading: authLoading, logout } = useAuth();
  const [query, setQuery] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [page, setPage] = useState(1);

  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 400);

  useEffect(() => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(PAGE_SIZE),
    });
    // Backend min 2 akshar maangta hai, warna 422
    if (debouncedQuery.trim().length >= 2) params.set("q", debouncedQuery.trim());
    if (cuisine) params.set("cuisine", cuisine);

    setLoading(true);
    setError(null);

    fetch(`${API_URL}/restaurants?${params}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json() as Promise<RestaurantPage>;
      })
      .then((data) => {
        setRestaurants(data.items);
        setTotal(data.total);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [debouncedQuery, cuisine, page]);   // inme se koi badla toh dobara fetch

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  // Filter badla toh page 1 par wapas
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
            <button className="btn" onClick={logout}>Logout</button>
          </div>
        )}
      </div>

      {!authLoading && !email && <LoginForm />}

      <h2>Menu</h2>
      <MenuList />

      <h2>Restaurants</h2>

      <div className="filters">
        <SearchBar value={query} onChange={handleQueryChange} />
        <CuisineFilter value={cuisine} onChange={handleCuisineChange} />
      </div>

      <p>{total} restaurants mile</p>

      {error && <p className="error">Error: {error}</p>}
      {loading && <p>Loading...</p>}

      {!loading && !error && restaurants.length === 0 && (
        <p>Koi restaurant nahi mila. Filter badal ke dekho.</p>
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