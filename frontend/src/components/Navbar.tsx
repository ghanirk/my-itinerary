import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

const navItems = [
  { to: "/", label: "Beranda" },
  { to: "/places", label: "Jelajahi Tempat" },
  { to: "/plans", label: "Plan Saya" },
];

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLinkClick = () => setIsOpen(false);

  const handleLogout = () => {
    logout();
    setIsOpen(false);
    navigate("/");
  };

  return (
    <nav className="bg-white/90 backdrop-blur-sm border-b border-brand-100 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Title */}
          <NavLink to="/" className="font-heading text-xl font-semibold text-brand-700 italic">
            My Itineraries
          </NavLink>

          {/* Tombol Hamburger (Hanya Tampil di Mobile) */}
          <div className="flex md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} type="button" aria-label="Toggle Menu" className="p-2 rounded-md text-brand-700 hover:bg-brand-50 focus:outline-none">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>

          {/* Menu Navigasi Desktop */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) => `font-body px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive ? "bg-brand-100 text-brand-700" : "text-muted hover:bg-brand-50 hover:text-brand-700"}`}
              >
                {item.label}
              </NavLink>
            ))}

            {isAuthenticated ? (
              <div className="flex items-center gap-3 pl-3 ml-2 border-l border-brand-100">
                <span className="text-sm text-muted">Hai, {user?.name.split(" ")[0]}</span>
                <button
                  onClick={handleLogout}
                  className="font-body px-3 py-2 rounded-md text-sm font-medium text-brand-700 border border-brand-700/40 hover:bg-brand-100 transition-colors"
                >
                  Keluar
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 pl-3 ml-2 border-l border-brand-100">
                <NavLink to="/login" className="font-body px-3 py-2 rounded-md text-sm font-medium text-muted hover:bg-brand-50 hover:text-brand-700 transition-colors">
                  Masuk
                </NavLink>
                <NavLink to="/register" className="font-body px-3 py-2 rounded-md text-sm font-medium bg-brand-700 text-white hover:bg-brand-800 transition-colors">
                  Daftar
                </NavLink>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Menu Navigasi Mobile */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-brand-100 px-4 pt-2 pb-4 space-y-1 shadow-lg">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={handleLinkClick}
              className={({ isActive }) => `block font-body px-3 py-2 rounded-md text-base font-medium transition-colors ${isActive ? "bg-brand-100 text-brand-700" : "text-muted hover:bg-brand-50 hover:text-brand-700"}`}
            >
              {item.label}
            </NavLink>
          ))}

          {isAuthenticated ? (
            <button onClick={handleLogout} className="block w-full text-left font-body px-3 py-2 rounded-md text-base font-medium text-brand-700 hover:bg-brand-50">
              Keluar ({user?.name.split(" ")[0]})
            </button>
          ) : (
            <>
              <NavLink to="/login" onClick={handleLinkClick} className="block font-body px-3 py-2 rounded-md text-base font-medium text-muted hover:bg-brand-50 hover:text-brand-700">
                Masuk
              </NavLink>
              <NavLink to="/register" onClick={handleLinkClick} className="block font-body px-3 py-2 rounded-md text-base font-medium text-brand-700 hover:bg-brand-50">
                Daftar
              </NavLink>
            </>
          )}
        </div>
      )}
    </nav>
  );
}

export default Navbar;
