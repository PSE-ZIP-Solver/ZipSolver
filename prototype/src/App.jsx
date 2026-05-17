import { useState } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import GridBuilder from './components/GridBuilder';
import { ThemeProvider } from './context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <div className="min-h-screen flex flex-col ">
        <Navbar />
        <main className="flex-1 w-full pt-2">
          <GridBuilder />
        </main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default App;
