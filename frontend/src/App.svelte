<script>
  import { onMount } from 'svelte';
  import { commitTree, isLoading, showToast, repoInfo } from './lib/stores/store.js';
  import { theme, toggleTheme } from './lib/stores/theme.js';
  import { fetchCommitTree, fetchRepoInfo } from './lib/services/api.js';
  import Toast from './lib/components/Toast.svelte';
  import Modal from './lib/components/Modal.svelte';
  import CommitTree from './lib/components/CommitTree.svelte';
  import RepoSelector from './lib/components/RepoSelector.svelte';
  import RecentRepos from './lib/components/RecentRepos.svelte';
  import GlobalActions from './lib/components/GlobalActions.svelte';
  import LandingPage from './lib/components/LandingPage.svelte';

  let error = null;
  let showLanding = localStorage.getItem('showLanding') !== 'false';
  let commitTreeComponent;

  onMount(async () => {
    await loadRepoInfo();
    await loadData();
    // Refresh data every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  });

  async function loadRepoInfo() {
    try {
      const info = await fetchRepoInfo();
      repoInfo.set(info);
    } catch (err) {
      console.error('Failed to load repo info:', err);
    }
  }

  async function loadData() {
    try {
      isLoading.set(true);
      const treeData = await fetchCommitTree();
      console.log('Loaded commit tree data:', treeData);
      commitTree.set(treeData);
      error = null;
    } catch (err) {
      console.error('Failed to load data:', err);
      error = err.message;
      showToast(`Failed to load data: ${err.message}`, 'error');
    } finally {
      isLoading.set(false);
    }
  }

  function handleNodeClick(node) {
    showToast(`Selected commit: ${node.sha.substring(0, 7)}`, 'info');
  }

  function handleGetStarted() {
    showLanding = false;
    localStorage.setItem('showLanding', 'false');
  }

  function handleGoToTop() {
    if (commitTreeComponent && commitTreeComponent.goToTop) {
      commitTreeComponent.goToTop();
    }
  }

  function handleShowRemote() {
    // To be implemented
  }

  function handleNameBranches() {
    // To be implemented
  }
</script>

{#if showLanding}
  <LandingPage onGetStarted={handleGetStarted} />
{:else}
<main class="app-main">
  <header class="app-header">
    <div class="header-left">
      <h1 class="app-title">Branch Monkey</h1>
      <RecentRepos />
    </div>

    <div class="header-center">
      <RepoSelector />
    </div>

    <div class="header-right">
      <GlobalActions
        onGoToTop={handleGoToTop}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
      />

      <button class="theme-toggle" on:click={toggleTheme} title="Toggle theme">
        {#if $theme === 'light'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
        {:else}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        {/if}
      </button>
    </div>
  </header>

  {#if error}
    <div class="error-banner">
      <span>{error}</span>
      <button on:click={loadData} class="retry-btn">Retry</button>
    </div>
  {/if}

  <div class="app-content">
    <CommitTree bind:this={commitTreeComponent} onNodeClick={handleNodeClick} />
  </div>

  <Toast />
  <Modal />
</main>
{/if}

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :global(:root[data-theme="light"]) {
    --bg-primary: #ffffff;
    --bg-secondary: #fafafa;
    --bg-hover: #f5f5f5;
    --text-primary: #171717;
    --text-secondary: #404040;
    --text-tertiary: #737373;
    --border-primary: #d4d4d4;
    --border-secondary: #e5e5e5;
    --border-hover: #a3a3a3;
    --accent-primary: #404040;
    --accent-secondary: #737373;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.15);

    /* Branch colors - light mode */
    --branch-main: #2563eb;
    --branch-experiment: #059669;
    --branch-feature: #7c3aed;
    --branch-fix: #dc2626;
    --branch-default: #6b7280;
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

  .app-main {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .app-header {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: 24px;
    align-items: center;
    padding: 16px 32px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-primary);
  }

  .header-left {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .app-title {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 1px;
    white-space: nowrap;
  }

  .header-center {
    display: flex;
    justify-content: center;
  }

  .header-right {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    align-items: center;
  }

  .theme-toggle {
    padding: 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .theme-toggle:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .error-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 32px;
    background: #fef2f2;
    color: #991b1b;
    border-bottom: 1px solid #fecaca;
    font-size: 13px;
  }

  :global([data-theme="dark"]) .error-banner {
    background: #3f1f1f;
    color: #fca5a5;
    border-bottom-color: #7f1d1d;
  }

  .retry-btn {
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 2px;
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .retry-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .app-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .app {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    padding: 0;
    gap: 0;
    overflow: hidden;
  }

  .app-header {
    text-align: center;
    padding: 8px 16px;
    background: #1a1a1a;
    border-bottom: 1px solid #333;
  }

  .app-title {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: #fff;
  }

  .repo-selector-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 16px;
  }

  .error-banner {
    background: #5c2828;
    color: #ff6b6b;
    padding: 12px 16px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #752e2e;
  }

  .retry-btn {
    background: #752e2e;
    color: #ff6b6b;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: background 0.2s;
  }

  .retry-btn:hover {
    background: #8a3434;
  }

  .app-content {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    width: 100%;
    overflow: hidden;
  }

  .panel {
    flex: 1;
    min-height: 0;
    width: 100%;
  }

  @media (max-width: 768px) {
    .app-title {
      font-size: 28px;
    }

    .app-subtitle {
      font-size: 14px;
    }

    .app-header {
      padding: 16px;
    }
  }
</style>
