import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";
import { useAuth } from "../context/useAuth";
import { ApiError } from "../api/client";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const token = await registerUser({ name, email, password });
      login(token);
      navigate("/plans");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Gagal mendaftar, coba lagi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-brand-50 min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-16">
      <div className="w-full max-w-sm bg-white border border-brand-100 rounded-lg p-8">
        <h1 className="font-heading text-2xl text-brand-700 mb-1">Daftar</h1>
        <p className="text-sm text-muted mb-6">Buat akun untuk mulai berkontribusi dan menyusun plan.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Nama</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-brand-100 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400/40"
            />
            <p className="text-xs text-muted mt-1">Minimal 8 karakter.</p>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-700 text-white py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium disabled:opacity-60"
          >
            {loading ? "Memproses..." : "Daftar"}
          </button>
        </form>

        <p className="text-sm text-muted text-center mt-6">
          Sudah punya akun?{" "}
          <Link to="/login" className="text-brand-700 font-medium underline underline-offset-4">
            Masuk
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;
