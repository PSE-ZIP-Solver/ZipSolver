import { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import GridBuilder from './components/GridBuilder';

function App() {
  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#f5f1ed' }}>
      <Navbar />
      <main className="flex-1 w-full pt-2">
        <GridBuilder />
      </main>
      <Footer />
    </div>
  );
}

export default App;
