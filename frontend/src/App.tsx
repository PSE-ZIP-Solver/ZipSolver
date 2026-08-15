import { useEffect, useState } from 'react';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HelpModal from './components/HelpModal';
import GridBuilder from './components/GridBuilder.tsx';

export const App: React.FC = () => {
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(() => {
    if (typeof document === "undefined") {
      return false;
    }

    return document.documentElement.classList.contains("dark");
  });

  useEffect(() => {
    const root = document.documentElement;
    root.classList.add("theme-switching");

    root.classList.toggle("dark", isDarkTheme);
    root.style.colorScheme = isDarkTheme ? "dark" : "light";
    window.localStorage.setItem("zipsolver-theme", isDarkTheme ? "dark" : "light");

    const frameId = window.requestAnimationFrame(() => {
      root.classList.remove("theme-switching");
    });

    return () => {
      window.cancelAnimationFrame(frameId);
      root.classList.remove("theme-switching");
    };
  }, [isDarkTheme]);

  return (
    <div className="min-h-screen flex flex-col bg-transparent text-text">
      <Navbar
        onOpenHelp={() => setIsHelpOpen(true)}
        isDarkTheme={isDarkTheme}
        onToggleTheme={() => setIsDarkTheme((previous) => !previous)}
      />

      <main className="flex-1 w-full px-4 py-6 sm:px-6 lg:px-8">
        <GridBuilder />
      </main>

      <Footer />

      <HelpModal
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
      />
    </div>
  );
};

export default App;