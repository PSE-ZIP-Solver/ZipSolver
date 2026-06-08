import { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  // Theme state
  const [theme, setThemeState] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  // Advanced Mode state
  const [advancedMode, setAdvancedModeState] = useState(() => {
    const savedAdvancedMode = localStorage.getItem('advancedMode');
    return savedAdvancedMode ? JSON.parse(savedAdvancedMode) : false;
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    const htmlElement = document.documentElement;
    if (theme === 'dark') {
      htmlElement.classList.add('dark');
    } else {
      htmlElement.classList.remove('dark');
    }
  }, [theme]);

  // Save advanced mode to local storage
  useEffect(() => {
    localStorage.setItem('advancedMode', JSON.stringify(advancedMode));
  }, [advancedMode]);

  const toggleTheme = () => {
    setThemeState((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const setTheme = (newTheme) => {
    setThemeState(newTheme);
  };

  const toggleAdvancedMode = () => {
    setAdvancedModeState((prev) => !prev);
  };

  const setAdvancedMode = (value) => {
    setAdvancedModeState(value);
  };

  return (
    <ThemeContext.Provider value={{ 
      theme, 
      toggleTheme, 
      setTheme,
      advancedMode,
      toggleAdvancedMode,
      setAdvancedMode
    }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
