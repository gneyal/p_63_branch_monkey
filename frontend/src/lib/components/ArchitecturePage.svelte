<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { theme, toggleTheme } from '../stores/theme.js';
  import { repoInfo } from '../stores/store.js';
  import { fetchRepoInfo } from '../services/api.js';
  import Toast from './Toast.svelte';
  import ArchitectureLibrary from './ArchitectureLibrary.svelte';
  import RecentRepos from './RecentRepos.svelte';
  import RepoSelector from './RepoSelector.svelte';
  import GlobalActions from './GlobalActions.svelte';

  onMount(async () => {
    if (!$repoInfo || !$repoInfo.path) {
      try {
        const info = await fetchRepoInfo();
        repoInfo.set(info);
      } catch (err) {
        console.error('Failed to load repo info:', err);
      }
    }
  });

  function goBack() {
    push('/');
  }

  function handleGoToTop() {
    push('/');
  }

  function handleGoToBottom() {
    push('/');
  }

  function handleShowRemote() {
    push('/');
  }

  function handleNameBranches() {
    push('/');
  }

  function handleShowPrompts() {
    push('/');
  }

  function handleShowContext() {
    push('/');
  }

  function handleShowArchitecture() {
    // Already on architecture page
  }
</script>

<main class="architecture-page">
  <header class="app-header">
    <div class="header-left">
      <div class="title-container">
        <h1 class="app-title" on:click={goBack} style="cursor: pointer;">branch/monkey</h1>
      </div>
      <RecentRepos />
    </div>

    <div class="header-center">
      <RepoSelector />
    </div>

    <div class="header-right">
      <div class="view-toggle">
        <button
          class="view-btn"
          on:click={goBack}
          title="Back to commits"
        >
          Commits
        </button>
        <button
          class="view-btn"
          on:click={() => push('/tasks')}
          title="Tasks view"
        >
          Tasks
        </button>
        <button
          class="view-btn active"
          title="Architecture view"
        >
          Arch
        </button>
      </div>
    </div>
  </header>

  <div class="page-content">
    <ArchitectureLibrary inline={true} />
  </div>

  <footer class="app-footer">
    <div class="footer-left">
      <GlobalActions
        onGoToTop={handleGoToTop}
        onGoToBottom={handleGoToBottom}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
        onShowPrompts={handleShowPrompts}
        onShowArchitecture={handleShowArchitecture}
        onShowContext={handleShowContext}
      />
    </div>

    <div class="footer-center">
      <span class="page-indicator">Architecture</span>
    </div>

    <div class="footer-right">
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
  </footer>

  <Toast />
</main>

<style>
  .architecture-page {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .app-header {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 24px;
    align-items: center;
    padding: 12px 24px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
    box-shadow: var(--shadow-small);
  }

  .header-left {
    display: flex;
    gap: 16px;
    align-items: center;
    justify-content: flex-start;
  }

  .title-container {
    position: relative;
  }

  .app-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 1px;
    text-transform: lowercase;
    margin: 0;
    font-family: 'Courier New', monospace;
  }

  .app-title:hover {
    color: var(--accent-primary);
  }

  .header-center {
    display: flex;
    justify-content: center;
  }

  .header-right {
    display: flex;
    gap: 12px;
    align-items: center;
    justify-content: flex-end;
  }

  .view-toggle {
    display: flex;
    gap: 0;
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    overflow: hidden;
  }

  .view-btn {
    padding: 6px 12px;
    background: var(--bg-primary);
    border: none;
    border-right: 1px solid var(--border-primary);
    color: var(--text-secondary);
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-btn:last-child {
    border-right: none;
  }

  .view-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .view-btn.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .page-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .app-footer {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 24px;
    align-items: center;
    padding: 8px 24px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-primary);
    box-shadow: var(--shadow-small);
  }

  .footer-left {
    display: flex;
    justify-content: flex-start;
  }

  .footer-center {
    display: flex;
    justify-content: center;
  }

  .footer-right {
    display: flex;
    justify-content: flex-end;
  }

  .page-indicator {
    font-size: 10px;
    color: var(--text-tertiary);
    font-family: 'Courier New', monospace;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .theme-toggle {
    padding: 6px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .theme-toggle:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  @media (max-width: 768px) {
    .app-header {
      grid-template-columns: 1fr;
      gap: 12px;
      padding: 12px 16px;
    }

    .header-left,
    .header-center,
    .header-right {
      justify-content: center;
    }

    .app-footer {
      grid-template-columns: 1fr;
      gap: 8px;
      padding: 8px 16px;
    }

    .footer-left,
    .footer-center,
    .footer-right {
      justify-content: center;
    }
  }
</style>
