import logo from "../assets/logoNoBg.png";

export default function Navbar() {
  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-2 flex items-center justify-between">
        {/* Logo and Application Name */}
        <div className="flex items-center gap-3">
          <img
            src={logo}
            alt="ZipSolver Logo"
            className="h-14 w-14 object-contain"
          />

          <h1 className="text-3xl font-bold text-gray-900">
            Zip <span className="text-orange-500">Solver</span>
          </h1>
        </div>

        {/* Navigation Actions */}
        <div className="flex items-center gap-3">
          {/* TODO: Implement advanced mode state and context integration */}
          <button
            className="px-3 py-2 rounded-lg hover:bg-gray-300 text-gray-900 transition-colors"
            aria-label="Toggle advanced mode"
          >
            <span className="text-sm font-semibold">
              ⚙️ Advanced
            </span>
          </button>

          {/* TODO: Implement help dialog integration */}
          <button
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-200 hover:text-gray-900 transition-colors"
            aria-label="Open help"
          >
            <span className="text-xl font-bold">?</span>
          </button>

          {/* TODO: Implement theme context integration */}
          <button
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-200 hover:text-gray-900 transition-colors"
            aria-label="Toggle theme"
          >
            <span className="text-xl">🌙</span>
          </button>
        </div>
      </div>
    </nav>
  );
}