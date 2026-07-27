import { useState } from 'react';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HelpModal from './components/HelpModal';
import GridBuilder from './components/GridBuilder';

export const App: React.FC = () => {
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [advancedMode, setAdvancedMode] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-transparent text-text">
      <Navbar
        onOpenHelp={() => setIsHelpOpen(true)}
        advancedMode={
          advancedMode
        }
        onToggleAdvanced={() =>
          setAdvancedMode(
            previous => !previous
          )
        }
      />

      <main className="flex-1 w-full px-4 py-6 sm:px-6 lg:px-8">
        <GridBuilder
          advancedMode={
            advancedMode
          }
        />
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