import { writable } from 'svelte/store';

// Vim-inspired color themes
export const themes = [
  // Dark themes
  {
    id: 'gruvbox-dark',
    name: 'Gruvbox Dark',
    type: 'dark',
    preview: { bg: '#282828', fg: '#ebdbb2', accent: '#fabd2f' }
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
    id: 'monokai',
    name: 'Monokai',
    type: 'dark',
    preview: { bg: '#272822', fg: '#f8f8f2', accent: '#a6e22e' }
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
  },
  {
    id: 'kanagawa',
    name: 'Kanagawa',
    type: 'dark',
    preview: { bg: '#1f1f28', fg: '#dcd7ba', accent: '#7e9cd8' }
  },
  {
    id: 'nightfox',
    name: 'Nightfox',
    type: 'dark',
    preview: { bg: '#192330', fg: '#cdcecf', accent: '#719cd6' }
  },
  {
    id: 'material',
    name: 'Material',
    type: 'dark',
    preview: { bg: '#263238', fg: '#eeffff', accent: '#82aaff' }
  },
  {
    id: 'palenight',
    name: 'Palenight',
    type: 'dark',
    preview: { bg: '#292d3e', fg: '#a6accd', accent: '#c792ea' }
  },
  {
    id: 'ayu-dark',
    name: 'Ayu Dark',
    type: 'dark',
    preview: { bg: '#0d1017', fg: '#bfbdb6', accent: '#e6b450' }
  },
  {
    id: 'github-dark',
    name: 'GitHub Dark',
    type: 'dark',
    preview: { bg: '#0d1117', fg: '#c9d1d9', accent: '#58a6ff' }
  },
  {
    id: 'horizon',
    name: 'Horizon',
    type: 'dark',
    preview: { bg: '#1c1e26', fg: '#d5d8da', accent: '#e95678' }
  },
  {
    id: 'iceberg',
    name: 'Iceberg',
    type: 'dark',
    preview: { bg: '#161821', fg: '#c6c8d1', accent: '#84a0c6' }
  },
  {
    id: 'solarized-dark',
    name: 'Solarized Dark',
    type: 'dark',
    preview: { bg: '#002b36', fg: '#839496', accent: '#2aa198' }
  },
  // Light themes
  {
    id: 'gruvbox-light',
    name: 'Gruvbox Light',
    type: 'light',
    preview: { bg: '#fbf1c7', fg: '#3c3836', accent: '#d79921' }
  },
  {
    id: 'one-light',
    name: 'One Light',
    type: 'light',
    preview: { bg: '#fafafa', fg: '#383a42', accent: '#4078f2' }
  },
  {
    id: 'github-light',
    name: 'GitHub Light',
    type: 'light',
    preview: { bg: '#ffffff', fg: '#24292f', accent: '#0969da' }
  },
  {
    id: 'solarized-light',
    name: 'Solarized Light',
    type: 'light',
    preview: { bg: '#fdf6e3', fg: '#657b83', accent: '#2aa198' }
  },
  {
    id: 'ayu-light',
    name: 'Ayu Light',
    type: 'light',
    preview: { bg: '#fafafa', fg: '#5c6166', accent: '#ff9940' }
  },
  {
    id: 'rose-pine-dawn',
    name: 'Rose Pine Dawn',
    type: 'light',
    preview: { bg: '#faf4ed', fg: '#575279', accent: '#d7827e' }
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
