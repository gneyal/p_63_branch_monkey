<script>
  export let onGoToTop = () => {};
  export let onGoToBottom = () => {};
  export let onShowRemote = () => {};
  export let onNameBranches = () => {};
  export let onShowPrompts = () => {};

  function handleGoToTop() {
    onGoToTop();
  }

  function handleGoToBottom() {
    onGoToBottom();
  }

  function handleShowRemote() {
    onShowRemote();
  }

  function handleNameBranches() {
    onNameBranches();
  }

  function handleShowPrompts() {
    onShowPrompts();
  }
</script>

<div class="global-actions">
  <button class="action-item" on:click={handleGoToTop} title="Go to newest">
    <span>⬆</span>
  </button>

  <button class="action-item" on:click={handleGoToBottom} title="Go to oldest">
    <span>⬇</span>
  </button>

  <button class="action-item" on:click={handleShowRemote} title="Check cloud sync">
    <span>Cloud</span>
  </button>

  <button class="action-item" on:click={handleNameBranches} title="Show all branches">
    <span>Branches</span>
  </button>

  <button class="action-item" on:click={handleShowPrompts} title="View prompts library">
    <span>Prompts</span>
  </button>
</div>

<style>
  .global-actions {
    display: flex;
    gap: 6px;
    align-items: center;
  }

  .action-item {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .action-item:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .action-item:active {
    transform: translateY(1px);
  }
</style>
