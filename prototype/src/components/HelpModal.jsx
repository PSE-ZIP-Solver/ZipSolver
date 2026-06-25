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
      className="fixed inset-0 flex items-center justify-center p-4 z-[9999] transition-all duration-200"
      style={{ 
        backgroundColor: isOpen ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0)',
        pointerEvents: isOpen ? 'auto' : 'none'
      }}
      onClick={onClose}
    >
      <div
        className="rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto shadow-lg transition-opacity duration-200 border border-gray-300 dark:border-gray-600"
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
        <div className="p-6 space-y-6">
          {/* What is ZipSolver Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">❓</span> What is ZipSolver?
            </h3>
            <div className="text-gray-700 dark:text-gray-300 space-y-2">
              <p>
                ZipSolver is a web-based tool for creating, editing, validating, and solving Zip puzzles. The solver uses a Reinforcement Learning (RL) agent to search for valid solutions.
              </p>
            </div>
          </section>

          <hr className="border-gray-200 dark:border-gray-700" />

          {/* How do I create a puzzle Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">🎮</span> How do I create a puzzle?
            </h3>
            <ol className="space-y-2 text-gray-700 dark:text-gray-300 list-decimal list-inside">
              <li>Select a grid size.</li>
              <li>Place numbered waypoints on the board.</li>
              <li>Add walls between adjacent cells if needed.</li>
              <li>Click <strong>Solve</strong> to start the solver.</li>
            </ol>
          </section>

          <hr className="border-gray-200 dark:border-gray-700" />

          {/* Validation Failed Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">⚠️</span> What does "Validation Failed" mean?
            </h3>
            <div className="text-gray-700 dark:text-gray-300 space-y-2">
              <p>
                The puzzle configuration is not valid and cannot be solved yet.
              </p>
              <p>
                Correct the reported issue and try again.
              </p>
            </div>
          </section>

          <hr className="border-gray-200 dark:border-gray-700" />

          {/* No Solution Found Section */}
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span className="text-orange-500">🔍</span> What does "No Solution Found" mean?
            </h3>
            <div className="text-gray-700 dark:text-gray-300 space-y-2">
              <p>
                The puzzle is valid, but the solver could not find a valid path for the current configuration.
              </p>
            </div>
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
