<script>
  import Router from 'svelte-spa-router';
  import LandingPage from './lib/components/LandingPage.svelte';
  import MainApp from './lib/components/MainApp.svelte';
  import TasksPage from './lib/components/TasksPage.svelte';
  import ArchitecturePage from './lib/components/ArchitecturePage.svelte';
  import TestsPage from './lib/components/TestsPage.svelte';
  import { push } from 'svelte-spa-router';

  const routes = {
    '/': MainApp,
    '/commits': MainApp,
    '/home': LandingPage,
    '/tasks': TasksPage,
    '/architecture': ArchitecturePage,
    '/tests': TestsPage,
  };

  function handleGetStarted() {
    push('/commits');
  }
</script>

<Router {routes} />

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* Gruvbox Dark - warm retro theme */
  :global(:root[data-theme="gruvbox-dark"]) {
    --bg-primary: #282828;
    --bg-secondary: #1d2021;
    --bg-hover: #3c3836;
    --text-primary: #ebdbb2;
    --text-secondary: #bdae93;
    --text-tertiary: #928374;
    --border-primary: #504945;
    --border-secondary: #3c3836;
    --border-hover: #665c54;
    --accent-primary: #fabd2f;
    --accent-secondary: #d79921;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #83a598;
    --branch-experiment: #b8bb26;
    --branch-feature: #d3869b;
    --branch-fix: #fb4934;
    --branch-default: #a89984;
  }

  /* Gruvbox Light */
  :global(:root[data-theme="gruvbox-light"]) {
    --bg-primary: #fbf1c7;
    --bg-secondary: #f2e5bc;
    --bg-hover: #ebdbb2;
    --text-primary: #3c3836;
    --text-secondary: #504945;
    --text-tertiary: #7c6f64;
    --border-primary: #d5c4a1;
    --border-secondary: #ebdbb2;
    --border-hover: #bdae93;
    --accent-primary: #d79921;
    --accent-secondary: #b57614;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #458588;
    --branch-experiment: #79740e;
    --branch-feature: #8f3f71;
    --branch-fix: #cc241d;
    --branch-default: #7c6f64;
  }

  /* Nord - arctic blue theme */
  :global(:root[data-theme="nord"]) {
    --bg-primary: #2e3440;
    --bg-secondary: #242933;
    --bg-hover: #3b4252;
    --text-primary: #eceff4;
    --text-secondary: #d8dee9;
    --text-tertiary: #a3b1c7;
    --border-primary: #4c566a;
    --border-secondary: #3b4252;
    --border-hover: #5c6a82;
    --accent-primary: #88c0d0;
    --accent-secondary: #81a1c1;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #81a1c1;
    --branch-experiment: #a3be8c;
    --branch-feature: #b48ead;
    --branch-fix: #bf616a;
    --branch-default: #d8dee9;
  }

  /* Dracula - purple dark theme */
  :global(:root[data-theme="dracula"]) {
    --bg-primary: #282a36;
    --bg-secondary: #21222c;
    --bg-hover: #44475a;
    --text-primary: #f8f8f2;
    --text-secondary: #d0d0d0;
    --text-tertiary: #6272a4;
    --border-primary: #44475a;
    --border-secondary: #363848;
    --border-hover: #6272a4;
    --accent-primary: #bd93f9;
    --accent-secondary: #ff79c6;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #8be9fd;
    --branch-experiment: #50fa7b;
    --branch-feature: #bd93f9;
    --branch-fix: #ff5555;
    --branch-default: #f8f8f2;
  }

  /* One Dark - Atom theme */
  :global(:root[data-theme="one-dark"]) {
    --bg-primary: #282c34;
    --bg-secondary: #21252b;
    --bg-hover: #2c313a;
    --text-primary: #abb2bf;
    --text-secondary: #9da5b4;
    --text-tertiary: #5c6370;
    --border-primary: #3e4451;
    --border-secondary: #2c313a;
    --border-hover: #4b5363;
    --accent-primary: #61afef;
    --accent-secondary: #528bff;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #61afef;
    --branch-experiment: #98c379;
    --branch-feature: #c678dd;
    --branch-fix: #e06c75;
    --branch-default: #abb2bf;
  }

  /* Solarized Dark */
  :global(:root[data-theme="solarized-dark"]) {
    --bg-primary: #002b36;
    --bg-secondary: #073642;
    --bg-hover: #094555;
    --text-primary: #839496;
    --text-secondary: #93a1a1;
    --text-tertiary: #657b83;
    --border-primary: #094555;
    --border-secondary: #073642;
    --border-hover: #586e75;
    --accent-primary: #2aa198;
    --accent-secondary: #268bd2;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #268bd2;
    --branch-experiment: #859900;
    --branch-feature: #6c71c4;
    --branch-fix: #dc322f;
    --branch-default: #93a1a1;
  }

  /* Solarized Light */
  :global(:root[data-theme="solarized-light"]) {
    --bg-primary: #fdf6e3;
    --bg-secondary: #eee8d5;
    --bg-hover: #e4ddc8;
    --text-primary: #657b83;
    --text-secondary: #586e75;
    --text-tertiary: #93a1a1;
    --border-primary: #d3cbb7;
    --border-secondary: #eee8d5;
    --border-hover: #93a1a1;
    --accent-primary: #2aa198;
    --accent-secondary: #268bd2;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #268bd2;
    --branch-experiment: #859900;
    --branch-feature: #6c71c4;
    --branch-fix: #dc322f;
    --branch-default: #586e75;
  }

  /* Monokai - classic dark theme */
  :global(:root[data-theme="monokai"]) {
    --bg-primary: #272822;
    --bg-secondary: #1e1f1a;
    --bg-hover: #3e3d32;
    --text-primary: #f8f8f2;
    --text-secondary: #cfcfc2;
    --text-tertiary: #75715e;
    --border-primary: #3e3d32;
    --border-secondary: #2d2e27;
    --border-hover: #525246;
    --accent-primary: #a6e22e;
    --accent-secondary: #f92672;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #66d9ef;
    --branch-experiment: #a6e22e;
    --branch-feature: #ae81ff;
    --branch-fix: #f92672;
    --branch-default: #f8f8f2;
  }

  /* Tokyo Night - Japanese neon theme */
  :global(:root[data-theme="tokyo-night"]) {
    --bg-primary: #1a1b26;
    --bg-secondary: #16161e;
    --bg-hover: #24283b;
    --text-primary: #c0caf5;
    --text-secondary: #a9b1d6;
    --text-tertiary: #565f89;
    --border-primary: #292e42;
    --border-secondary: #1f2335;
    --border-hover: #3b4261;
    --accent-primary: #7aa2f7;
    --accent-secondary: #bb9af7;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #7aa2f7;
    --branch-experiment: #9ece6a;
    --branch-feature: #bb9af7;
    --branch-fix: #f7768e;
    --branch-default: #a9b1d6;
  }

  /* Catppuccin Mocha - pastel dark theme */
  :global(:root[data-theme="catppuccin"]) {
    --bg-primary: #1e1e2e;
    --bg-secondary: #181825;
    --bg-hover: #313244;
    --text-primary: #cdd6f4;
    --text-secondary: #bac2de;
    --text-tertiary: #6c7086;
    --border-primary: #45475a;
    --border-secondary: #313244;
    --border-hover: #585b70;
    --accent-primary: #cba6f7;
    --accent-secondary: #f5c2e7;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #89b4fa;
    --branch-experiment: #a6e3a1;
    --branch-feature: #cba6f7;
    --branch-fix: #f38ba8;
    --branch-default: #bac2de;
  }

  /* Everforest - soft green theme */
  :global(:root[data-theme="everforest"]) {
    --bg-primary: #2d353b;
    --bg-secondary: #272e33;
    --bg-hover: #343f44;
    --text-primary: #d3c6aa;
    --text-secondary: #9da9a0;
    --text-tertiary: #7a8478;
    --border-primary: #414b50;
    --border-secondary: #343f44;
    --border-hover: #4f585e;
    --accent-primary: #a7c080;
    --accent-secondary: #83c092;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #7fbbb3;
    --branch-experiment: #a7c080;
    --branch-feature: #d699b6;
    --branch-fix: #e67e80;
    --branch-default: #9da9a0;
  }

  /* Rose Pine - elegant dark theme */
  :global(:root[data-theme="rose-pine"]) {
    --bg-primary: #191724;
    --bg-secondary: #1f1d2e;
    --bg-hover: #26233a;
    --text-primary: #e0def4;
    --text-secondary: #908caa;
    --text-tertiary: #6e6a86;
    --border-primary: #403d52;
    --border-secondary: #26233a;
    --border-hover: #524f67;
    --accent-primary: #ebbcba;
    --accent-secondary: #f6c177;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #9ccfd8;
    --branch-experiment: #31748f;
    --branch-feature: #c4a7e7;
    --branch-fix: #eb6f92;
    --branch-default: #908caa;
  }

  /* Legacy fallbacks for 'light' and 'dark' */
  :global(:root[data-theme="light"]) {
    --bg-primary: #fbf1c7;
    --bg-secondary: #f2e5bc;
    --bg-hover: #ebdbb2;
    --text-primary: #3c3836;
    --text-secondary: #504945;
    --text-tertiary: #7c6f64;
    --border-primary: #d5c4a1;
    --border-secondary: #ebdbb2;
    --border-hover: #bdae93;
    --accent-primary: #d79921;
    --accent-secondary: #b57614;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #458588;
    --branch-experiment: #79740e;
    --branch-feature: #8f3f71;
    --branch-fix: #cc241d;
    --branch-default: #7c6f64;
  }

  :global(:root[data-theme="dark"]) {
    --bg-primary: #282828;
    --bg-secondary: #1d2021;
    --bg-hover: #3c3836;
    --text-primary: #ebdbb2;
    --text-secondary: #bdae93;
    --text-tertiary: #928374;
    --border-primary: #504945;
    --border-secondary: #3c3836;
    --border-hover: #665c54;
    --accent-primary: #fabd2f;
    --accent-secondary: #d79921;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #83a598;
    --branch-experiment: #b8bb26;
    --branch-feature: #d3869b;
    --branch-fix: #fb4934;
    --branch-default: #a89984;
  }

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  :global(*) {
    box-sizing: border-box;
  }
</style>
