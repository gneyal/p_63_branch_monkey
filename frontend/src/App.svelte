<script>
  import Router from 'svelte-spa-router';
  import LandingPage from './lib/components/LandingPage.svelte';
  import MainApp from './lib/components/MainApp.svelte';
  import { push } from 'svelte-spa-router';

  const routes = {
    '/': MainApp,
    '/home': LandingPage,
  };

  function handleGetStarted() {
    push('/');
  }
</script>

<Router {routes} useHash={false} />

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :global(:root[data-theme="light"]) {
    --bg-primary: #fafaf8;
    --bg-secondary: #f0f0ed;
    --bg-hover: #e8e8e3;
    --text-primary: #1a1a1a;
    --text-secondary: #4a4a4a;
    --text-tertiary: #7a7a7a;
    --border-primary: #d0d0c8;
    --border-secondary: #e0e0d8;
    --border-hover: #a0a098;
    --accent-primary: #4a4a4a;
    --accent-secondary: #7a7a7a;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.1);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.15);

    /* Branch colors - light mode - muted */
    --branch-main: #4a7dc9;
    --branch-experiment: #3a9679;
    --branch-feature: #8e6cbd;
    --branch-fix: #c84a4a;
    --branch-default: #7a8290;
  }

  :global(:root[data-theme="dark"]) {
    --bg-primary: #1a1a1a;
    --bg-secondary: #121212;
    --bg-hover: #262626;
    --text-primary: #e5e5e5;
    --text-secondary: #a3a3a3;
    --text-tertiary: #737373;
    --border-primary: #404040;
    --border-secondary: #2d2d2d;
    --border-hover: #525252;
    --accent-primary: #e5e5e5;
    --accent-secondary: #a3a3a3;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.4);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.5);

    /* Branch colors - dark mode */
    --branch-main: #3b82f6;
    --branch-experiment: #10b981;
    --branch-feature: #8b5cf6;
    --branch-fix: #ef4444;
    --branch-default: #9ca3af;
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
