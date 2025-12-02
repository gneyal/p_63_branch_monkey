<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { theme, toggleTheme } from '../stores/theme.js';
  import { repoInfo } from '../stores/store.js';
  import { fetchRepoInfo } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Topbar from './Topbar.svelte';
  import GlobalActions from './GlobalActions.svelte';

  // Placeholder for tests data
  let tests = [];

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

  function handleGoToTop() {
    push('/commits');
  }

  function handleGoToBottom() {
    push('/commits');
  }

  function handleShowRemote() {
    push('/commits');
  }

  function handleNameBranches() {
    push('/commits');
  }

  function handleShowPrompts() {
    push('/commits');
  }

  function handleShowContext() {
    push('/commits');
  }
</script>

<main class="tests-page">
  <Topbar activeView="tests" />

  <div class="page-content">
    <div class="tests-container">
      <div class="tests-header">
        <h2>Tests</h2>
        <p class="tests-description">
          Select elements in the Architecture flow view and right-click to create tests.
        </p>
      </div>

      <div class="tests-content">
        {#if tests.length === 0}
          <div class="empty-state">
            <div class="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
            </div>
            <h3>No tests yet</h3>
            <p>Go to the <strong>Architecture</strong> view, select components in the Flow diagram, and right-click to create tests.</p>
          </div>
        {:else}
          <div class="tests-list">
            {#each tests as test}
              <div class="test-item">
                <span class="test-name">{test.name}</span>
                <span class="test-elements">{test.elements.length} elements</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <footer class="app-footer">
    <div class="footer-left">
      <GlobalActions
        onGoToTop={handleGoToTop}
        onGoToBottom={handleGoToBottom}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
        onShowPrompts={handleShowPrompts}
        onShowContext={handleShowContext}
      />
    </div>

    <div class="footer-center">
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
  .tests-page {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .page-content {
    flex: 1;
    min-height: 0;
    overflow: auto;
    padding: 24px;
  }

  .tests-container {
    max-width: 800px;
    margin: 0 auto;
  }

  .tests-header {
    margin-bottom: 24px;
  }

  .tests-header h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .tests-description {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }

  .tests-content {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    min-height: 400px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    text-align: center;
    color: var(--text-tertiary);
  }

  .empty-icon {
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .empty-state h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .empty-state p {
    margin: 0;
    font-size: 14px;
    max-width: 400px;
    line-height: 1.6;
  }

  .empty-state strong {
    color: var(--text-primary);
  }

  .tests-list {
    padding: 16px;
  }

  .test-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .test-item:last-child {
    border-bottom: none;
  }

  .test-name {
    font-size: 14px;
    color: var(--text-primary);
  }

  .test-elements {
    font-size: 12px;
    color: var(--text-tertiary);
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
</style>
