<script>
  import { showToast } from '../stores/store.js';

  export let onGoToTop = () => {};
  export let onShowRemote = () => {};
  export let onNameBranches = () => {};

  function handleGoToTop() {
    onGoToTop();
  }

  function handleShowRemote() {
    onShowRemote();
    showToast('Show remote functionality coming soon', 'info');
  }

  function handleNameBranches() {
    onNameBranches();
  }
</script>

<div class="global-actions">
  <button class="action-item" on:click={handleGoToTop} title="Go to top">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="18 15 12 9 6 15"/>
    </svg>
    <span>Top</span>
  </button>

  <button class="action-item" on:click={handleShowRemote} title="Show remote">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <line x1="2" y1="12" x2="22" y2="12"/>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    </svg>
    <span>Remote</span>
  </button>

  <button class="action-item" on:click={handleNameBranches} title="Name all branches">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="6" y1="3" x2="6" y2="15"/>
      <circle cx="18" cy="6" r="3"/>
      <circle cx="6" cy="18" r="3"/>
      <path d="M18 9a9 9 0 0 1-9 9"/>
    </svg>
    <span>Names</span>
  </button>
</div>

<style>
  .global-actions {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .action-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
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

  .action-item:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .action-item svg {
    flex-shrink: 0;
  }
</style>
