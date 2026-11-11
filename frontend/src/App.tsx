import { Link, Route, Routes } from "react-router-dom";
import "./App.css";
import { useAuth } from "./auth/AuthContext";
import Home from "./pages/Home";
import { MyOrders } from "./pages/MyOrders";

function App() {
  const { email, logout } = useAuth();

  return (
    <div className="container">
      <div className="header">
        <h1>FoodOps 🍽️</h1>
        <nav className="nav">
          <Link to="/">Home</Link>
          <Link to="/orders">My Orders</Link>
          {email && (
            <>
              <span>Hi, {email}</span>
              <button className="btn" onClick={logout}>Logout</button>
            </>
          )}
        </nav>
      </div>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/orders" element={<MyOrders />} />
        <Route path="*" element={<p>404: Page nahi mila</p>} />
      </Routes>
    </div>
  );
}

export default App;
