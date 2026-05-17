import { useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';

export default function HelpModal({ isOpen, onClose }) {
  const { theme } = useTheme();
  // Handle Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-4 z-50 transition-all duration-200"
      style={{ 
        backgroundColor: isOpen ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0)',
        pointerEvents: isOpen ? 'auto' : 'none'
      }}
      onClick={onClose}
    >
      <div
        className="rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto shadow-lg transition-opacity duration-200 dark:border-gray-700"
        onClick={(e) => e.stopPropagation()}
        style={{ 
          opacity: isOpen ? 1 : 0,
          backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
          color: theme === 'dark' ? '#e5e5e5' : '#1a1a1a'
        }}
      >
        {/* Close Button */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 sticky top-0 backdrop-blur-none z-10" style={{ backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff' }}>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">How to Use ZipSolver</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl font-bold w-8 h-8 flex items-center justify-center hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-8">
          {/* Game Rules Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">🎮</span> Game Rules
            </h3>
            <div className="space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                <strong>Objective:</strong> Solve the puzzle by finding the correct path from the start cell to the end cell.
              </p>
              <p>
                <strong>How to Build:</strong>
              </p>
              <ul className="list-disc list-inside space-y-2 ml-2">
                <li>Left-click on grid cells to create walls</li>
                <li>Right-click to remove walls</li>
                <li>Create a connected path using vertical and horizontal walls</li>
                <li>The solver will find the optimal path through your maze</li>
              </ul>
              <p>
                <strong>Challenge:</strong> Design increasingly complex puzzles and see how the solver navigates through them.
              </p>
            </div>
          </section>

          {/* Interface Guide Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">🎯</span> Interface Guide
            </h3>
            <div className="space-y-4 text-gray-700 dark:text-gray-300">
              <div>
                <p className="font-semibold text-gray-900 dark:text-gray-100">Grid Panel</p>
                <p className="mt-1">The main canvas where you design your maze. Click and drag to draw walls or use right-click to erase.</p>
              </div>
              <div>
                <p className="font-semibold text-gray-900 dark:text-gray-100">Controls Panel</p>
                <p className="mt-1">
                  Contains buttons to manage your puzzle:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2 mt-2">
                  <li><strong>SOLVE ALL</strong> - Run the solver algorithm</li>
                  <li><strong>RESET</strong> - Clear the grid</li>
                  <li><strong>EXPORT</strong> - Save your puzzle as JSON</li>
                  <li><strong>IMPORT</strong> - Load a saved puzzle</li>
                </ul>
              </div>
              <div>
                <p className="font-semibold text-gray-900 dark:text-gray-100">Metrics Panel</p>
                <p className="mt-1">Displays statistics about your current puzzle including grid dimensions, wall count, and path length.</p>
              </div>
              <div>
                <p className="font-semibold text-gray-900 dark:text-gray-100">Navigation</p>
                <p className="mt-1">
                  Use <span className="font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">← →</span> arrow keys or Previous/Next buttons to step through the solution animation.
                </p>
              </div>
            </div>
          </section>

          {/* Tips Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">💡</span> Tips & Tricks
            </h3>
            <ul className="space-y-2 text-gray-700 dark:text-gray-300 list-disc list-inside">
              <li>Start with simple designs before attempting complex mazes</li>
              <li>Use the Step Counter to trace the solution path step by step</li>
              <li>Export your puzzles to share or save your best designs</li>
              <li>The solver works with any maze size you create</li>
            </ul>
          </section>
        </div>

        {/* Footer Button */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 sticky bottom-0 flex justify-end z-10" style={{ backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff' }}>
          <button
            onClick={onClose}
            className="btn-primary px-6 py-2 rounded-lg"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  );
}
