import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "../api";

const TOKEN_KEY = "foodops_token";

type AuthState = {
  email: string | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [email, setEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem(TOKEN_KEY)));

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setEmail(null);
  }

  // Page load par: saved token abhi bhi valid hai? (expire ya tamper to nahi hua)
  useEffect(() => {
    if (!token) return;
    api<{ email: string }>("/auth/me", {}, token)
      .then((user) => setEmail(user.email))
      .catch(() => logout())
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(emailInput: string, password: string) {
    // Backend form-encoded maangta hai, field ka naam `username` hai
    const body = new URLSearchParams({ username: emailInput, password });
    const data = await api<{ access_token: string }>("/auth/login", { method: "POST", body });
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    setEmail(emailInput);
  }

  async function register(emailInput: string, password: string) {
    await api("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: emailInput, password }),
    });
    await login(emailInput, password);
  }

  return (
    <AuthContext.Provider value={{ email, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth ko AuthProvider ke andar use karo");
  return ctx;
}