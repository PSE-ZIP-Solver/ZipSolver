import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

const THEME_STORAGE_KEY = "zipsolver-theme";

function resolveInitialTheme() {
  const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);

  if (savedTheme === "dark") {
    return true;
  }

  if (savedTheme === "light") {
    return false;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

const initialDarkTheme = resolveInitialTheme();
document.documentElement.classList.toggle("dark", initialDarkTheme);
document.documentElement.style.colorScheme = initialDarkTheme ? "dark" : "light";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
