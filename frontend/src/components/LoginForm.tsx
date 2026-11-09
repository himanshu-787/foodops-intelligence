import { useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";

export function LoginForm() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();               // page reload mat hone do
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kuch galat hua");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card auth-form" onSubmit={handleSubmit}>
      <h3>{mode === "login" ? "Login" : "Naya account"}</h3>
      <input
        className="input"
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <input
        className="input"
        type="password"
        placeholder="Password (min 8 akshar)"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        minLength={8}
        required
      />
      {error && <p className="error">{error}</p>}
      <button className="btn" type="submit" disabled={submitting}>
        {submitting ? "Ruko..." : mode === "login" ? "Login" : "Register"}
      </button>
      <button
        type="button"
        className="link"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
      >
        {mode === "login" ? "Naya account banao" : "Pehle se account hai? Login"}
      </button>
    </form>
  );
}