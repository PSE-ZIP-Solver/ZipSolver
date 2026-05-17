import { useState } from 'react';
import logo from '../assets/logoNoBg.png';
import HelpModal from './HelpModal';
import { useTheme } from '../context/ThemeContext';

export default function Navbar() {
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  return (
    <>
      <nav className="bg-white dark:bg-gray-800 shadow-md border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between gap-3">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <img src={logo} alt="ZipSolver Logo" className="h-14 w-14 object-contain flex-shrink-0" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Zip <span className="text-orange-500">Solver</span>
            </h1>
          </div>

          {/* Right Side Buttons */}
          <div className="flex items-center gap-3">
            {/* Help Button */}
            <button
              onClick={() => setIsHelpOpen(true)}
              className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-200 transition-all duration-200"
              title="Help"
              aria-label="Open help"
            >
              <span className="text-xl font-bold">?</span>
            </button>

            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-200 transition-all duration-200"
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              aria-label="Toggle theme"
            >
              <span className="text-xl">{theme === 'dark' ? '☀️' : '🌙'}</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Help Modal */}
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </>
  );
}
