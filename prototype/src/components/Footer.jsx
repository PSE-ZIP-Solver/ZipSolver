export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 py-6 mt-12">
      <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-600">
          &copy; {new Date().getFullYear()} ZipSolver. All rights reserved.
        <p className="mt-2 text-xs text-gray-500">
          Built for reinforcement learning puzzle solver training
        </p>
      </div>
    </footer>
  );
}
