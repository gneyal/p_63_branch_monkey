import { writable } from 'svelte/store';

// Vim-inspired color themes
export const themes = [
  {
    id: 'gruvbox-dark',
    name: 'Gruvbox Dark',
    type: 'dark',
    preview: { bg: '#282828', fg: '#ebdbb2', accent: '#fabd2f' }
  },
  {
    id: 'gruvbox-light',
    name: 'Gruvbox Light',
    type: 'light',
    preview: { bg: '#fbf1c7', fg: '#3c3836', accent: '#d79921' }
  },
  {
    id: 'nord',
    name: 'Nord',
    type: 'dark',
    preview: { bg: '#2e3440', fg: '#eceff4', accent: '#88c0d0' }
  },
  {
    id: 'dracula',
    name: 'Dracula',
    type: 'dark',
    preview: { bg: '#282a36', fg: '#f8f8f2', accent: '#bd93f9' }
  },
  {
    id: 'one-dark',
    name: 'One Dark',
    type: 'dark',
    preview: { bg: '#282c34', fg: '#abb2bf', accent: '#61afef' }
  },
  {
    id: 'solarized-dark',
    name: 'Solarized Dark',
    type: 'dark',
    preview: { bg: '#002b36', fg: '#839496', accent: '#2aa198' }
  },
  {
    id: 'solarized-light',
    name: 'Solarized Light',
    type: 'light',
    preview: { bg: '#fdf6e3', fg: '#657b83', accent: '#2aa198' }
  },
  {
    id: 'monokai',
    name: 'Monokai',
    type: 'dark',
    preview: { bg: '#272822', fg: '#f8f8f2', accent: '#a6e22e' }
  },
  {
    id: 'tokyo-night',
    name: 'Tokyo Night',
    type: 'dark',
    preview: { bg: '#1a1b26', fg: '#c0caf5', accent: '#7aa2f7' }
  },
  {
    id: 'catppuccin',
    name: 'Catppuccin',
    type: 'dark',
    preview: { bg: '#1e1e2e', fg: '#cdd6f4', accent: '#cba6f7' }
  },
  {
    id: 'everforest',
    name: 'Everforest',
    type: 'dark',
    preview: { bg: '#2d353b', fg: '#d3c6aa', accent: '#a7c080' }
  },
  {
    id: 'rose-pine',
    name: 'Rose Pine',
    type: 'dark',
    preview: { bg: '#191724', fg: '#e0def4', accent: '#ebbcba' }
  }
];

// Check for saved theme preference or default to gruvbox-dark
const savedTheme = typeof localStorage !== 'undefined'
  ? localStorage.getItem('branchMonkeyTheme') || 'gruvbox-dark'
  : 'gruvbox-dark';

export const theme = writable(savedTheme);

// Subscribe to theme changes and save to localStorage
theme.subscribe(value => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('branchMonkeyTheme', value);
    document.documentElement.setAttribute('data-theme', value);
  }
});

export function setTheme(themeId) {
  theme.set(themeId);
}

// Legacy toggle for backward compatibility (cycles through themes)
export function toggleTheme() {
  theme.update(current => {
    const currentIndex = themes.findIndex(t => t.id === current);
    const nextIndex = (currentIndex + 1) % themes.length;
    return themes[nextIndex].id;
  });
}

// Get theme type (light/dark) for a theme ID
export function getThemeType(themeId) {
  const t = themes.find(theme => theme.id === themeId);
  return t?.type || 'dark';
}
