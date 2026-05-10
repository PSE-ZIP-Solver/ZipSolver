import logo from '../assets/logo.png';

export default function Navbar() {
  return (
    <nav className="bg-gray-100 shadow-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
        <img src={logo} alt="ZipSolver Logo" className="h-6 w-6 object-contain flex-shrink-0" />
        <h1 className="text-3xl font-bold">
          Zip <span className="text-orange-500">Solver</span>
        </h1>
      </div>
    </nav>
  );
}
