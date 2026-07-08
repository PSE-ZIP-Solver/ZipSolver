const Footer: React.FC = () => {
  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-6 mt-12">
      <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-600 dark:text-gray-400">
        &copy; {new Date().getFullYear()} ZipSolver. All rights reserved.
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-500">
          Built for experimenting with reinforcement learning on puzzles.
        </p>
      </div>
    </footer>
  );
};

export default Footer;