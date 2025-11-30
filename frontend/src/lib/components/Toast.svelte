<script>
  import { toasts, dismissToast } from '../stores/store.js';
  import { fade, fly } from 'svelte/transition';
</script>

<div class="toast-container">
  {#each $toasts as toast (toast.id)}
    <div
      class="toast toast-{toast.type}"
      transition:fly="{{ y: 50, duration: 300 }}"
    >
      <div class="toast-content">
        <span class="toast-icon">
          {#if toast.type === 'success'}✓{/if}
          {#if toast.type === 'error'}✕{/if}
          {#if toast.type === 'info'}ℹ{/if}
        </span>
        <span class="toast-message">{toast.message}</span>
      </div>
      <button
        class="toast-close"
        on:click={() => dismissToast(toast.id)}
      >
        ✕
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 10px;
    pointer-events: none;
  }

  .toast {
    pointer-events: auto;
    background: #2d2d2d;
    color: #e0e0e0;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    min-width: 300px;
    max-width: 400px;
    border-left: 4px solid;
  }

  .toast-success {
    border-left-color: #4caf50;
  }

  .toast-error {
    border-left-color: #f44336;
  }

  .toast-info {
    border-left-color: #2196f3;
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
  }

  .toast-icon {
    font-weight: bold;
    font-size: 16px;
  }

  .toast-success .toast-icon {
    color: #4caf50;
  }

  .toast-error .toast-icon {
    color: #f44336;
  }

  .toast-info .toast-icon {
    color: #2196f3;
  }

  .toast-message {
    font-size: 14px;
    line-height: 1.4;
  }

  .toast-close {
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    font-size: 16px;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s;
  }

  .toast-close:hover {
    color: #fff;
  }
</style>
