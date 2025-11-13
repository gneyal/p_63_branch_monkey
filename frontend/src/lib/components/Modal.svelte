<script>
  import { modal, hideModal } from '../stores/store.js';
  import { fade, scale } from 'svelte/transition';

  let inputValue = '';

  $: if ($modal.isOpen && $modal.showInput) {
    inputValue = $modal.inputValue || '';
  }

  function handleConfirm() {
    if ($modal.onConfirm) {
      if ($modal.showInput) {
        $modal.onConfirm(inputValue);
      } else {
        $modal.onConfirm();
      }
    }
    hideModal();
  }

  function handleCancel() {
    if ($modal.onCancel) {
      $modal.onCancel();
    }
    hideModal();
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
      handleCancel();
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && $modal.showInput) {
      e.preventDefault();
      handleConfirm();
    }
  }
</script>

{#if $modal.isOpen}
  <div
    class="modal-backdrop"
    transition:fade="{{ duration: 200 }}"
    on:click={handleBackdropClick}
  >
    <div
      class="modal-dialog"
      transition:scale="{{ duration: 200, start: 0.9 }}"
    >
      {#if $modal.title}
        <h2 class="modal-title">{$modal.title}</h2>
      {/if}

      {#if $modal.message}
        <p class="modal-message">{$modal.message}</p>
      {/if}

      {#if $modal.showInput}
        <input
          type="text"
          bind:value={inputValue}
          placeholder={$modal.inputPlaceholder}
          class="modal-input"
          on:keydown={handleKeydown}
          autofocus
        />
      {/if}

      <div class="modal-actions">
        <button
          class="btn btn-secondary"
          on:click={handleCancel}
        >
          {$modal.cancelText}
        </button>
        <button
          class="btn btn-primary"
          on:click={handleConfirm}
        >
          {$modal.confirmText}
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
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 999;
    backdrop-filter: blur(2px);
  }

  .modal-dialog {
    background: #2d2d2d;
    border-radius: 12px;
    padding: 24px;
    max-width: 500px;
    width: 90%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    border: 1px solid #444;
  }

  .modal-title {
    margin: 0 0 16px 0;
    font-size: 20px;
    font-weight: 600;
    color: #e0e0e0;
  }

  .modal-message {
    margin: 0 0 24px 0;
    font-size: 14px;
    line-height: 1.5;
    color: #b0b0b0;
  }

  .modal-input {
    width: 100%;
    padding: 10px 12px;
    margin-bottom: 24px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-primary);
    border-radius: 4px;
    font-size: 14px;
    font-family: 'Courier', monospace;
    outline: none;
    transition: border-color 0.15s;
  }

  .modal-input:focus {
    border-color: var(--border-hover);
  }

  .modal-input::placeholder {
    color: var(--text-tertiary);
  }

  .modal-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }

  .btn {
    padding: 10px 20px;
    border-radius: 6px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary {
    background: #404040;
    color: #e0e0e0;
  }

  .btn-secondary:hover {
    background: #4a4a4a;
  }

  .btn-primary {
    background: #2196f3;
    color: white;
  }

  .btn-primary:hover {
    background: #1976d2;
  }
</style>
