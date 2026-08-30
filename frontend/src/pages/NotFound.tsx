import { Link } from "react-router-dom";

function NotFound() {
  return (
    <div className="bg-brand-50 min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center text-center px-4">
      <p className="font-heading italic text-6xl text-brand-400/40 mb-4">404</p>
      <h1 className="font-heading text-2xl text-brand-700 mb-2">Halaman tidak ditemukan</h1>
      <p className="text-muted mb-6">Sepertinya kamu tersasar dari rencana perjalanan.</p>
      <Link to="/" className="bg-brand-700 text-white px-5 py-2.5 rounded-md hover:bg-brand-800 transition-colors font-medium">
        Kembali ke Beranda
      </Link>
    </div>
  );
}

export default NotFound;
