import { useState } from 'react';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HelpModal from './components/HelpModal';
// import GridBuilder from './components/GridBuilder';

export const App: React.FC = () => {
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
      <Navbar
        onOpenHelp={() => setIsHelpOpen(true)}
      />

      <main className="flex-1 w-full pt-2">
        {/* <GridBuilder /> */}
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