const Footer: React.FC = () => {
  return (
    <footer className="bg-chrome 
    border-t border-footer-border 
    py-6 mt-12">

      <div className="max-w-7xl mx-auto px-6 text-center text-sm text-footer-text">
        &copy; {new Date().getFullYear()} ZipSolver. All rights reserved.

        <p className="mt-2 text-xs text-footer-text/70">
          Built for experimenting with reinforcement learning on puzzles.
        </p>

      </div>
    </footer>
  );
};

export default Footer;