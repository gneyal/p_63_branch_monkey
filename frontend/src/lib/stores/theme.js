import { writable } from 'svelte/store';

// Check for saved theme preference or default to light
const savedTheme = localStorage.getItem('branchMonkeyTheme') || 'light';

export const theme = writable(savedTheme);

// Subscribe to theme changes and save to localStorage
theme.subscribe(value => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('branchMonkeyTheme', value);
    document.documentElement.setAttribute('data-theme', value);
  }
});

export function toggleTheme() {
  theme.update(current => current === 'light' ? 'dark' : 'light');
}
