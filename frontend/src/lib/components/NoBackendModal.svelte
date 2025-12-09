<script>
  import { push } from 'svelte-spa-router';
  import { noBackendDetected, isDemoMode } from '../stores/store.js';

  function goToInstall() {
    noBackendDetected.set(false);
    push('/install');
  }

  function dismiss() {
    noBackendDetected.set(false);
  }
</script>

{#if $noBackendDetected && !$isDemoMode}
  <div class="modal-backdrop" on:click={dismiss}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Local Installation Required</h2>
      </div>

      <div class="modal-body">
        <p>Branch Monkey is a <strong>local-first app</strong> that runs on your machine alongside your Git repositories.</p>

        <p>To use features like Tasks, Commits, and Prompts, you'll need to:</p>

        <ol>
          <li>Clone the repository to your local machine</li>
          <li>Run the Python backend server</li>
          <li>Open the app at <code>localhost:5176</code></li>
        </ol>

        <p class="hint">This web preview is for demonstration purposes only.</p>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" on:click={dismiss}>
          Continue Browsing
        </button>
        <button class="btn-primary" on:click={goToInstall}>
          View Install Guide
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
  }

  .modal-content {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    padding: 24px;
    max-width: 480px;
    width: 90%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .modal-header h2 {
    margin: 0 0 16px;
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .modal-body {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.6;
  }

  .modal-body p {
    margin: 0 0 12px;
  }

  .modal-body ol {
    margin: 0 0 16px;
    padding-left: 20px;
  }

  .modal-body li {
    margin-bottom: 6px;
  }

  .modal-body code {
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 13px;
  }

  .modal-body strong {
    color: var(--text-primary);
  }

  .hint {
    font-size: 12px;
    color: var(--text-tertiary);
    font-style: italic;
  }

  .modal-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 20px;
  }

  .btn-primary, .btn-secondary {
    padding: 10px 20px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background: var(--accent-primary);
    border: none;
    color: var(--bg-primary);
  }

  .btn-primary:hover {
    opacity: 0.9;
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
  }

  .btn-secondary:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }
</style>
