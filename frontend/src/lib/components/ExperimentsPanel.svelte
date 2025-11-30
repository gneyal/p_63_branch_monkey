<script>
  import { experiments, activeExperiment, showToast, showModal } from '../stores/store.js';
  import { switchExperiment, createExperiment, discardExperiment } from '../services/api.js';

  let isCreating = false;
  let newExperimentName = '';
  let newExperimentDescription = '';

  async function handleSwitch(experiment) {
    try {
      await switchExperiment(experiment.name);
      showToast(`Switched to experiment: ${experiment.name}`, 'success');
      // Refresh experiments list
      window.location.reload();
    } catch (error) {
      showToast(error.message, 'error');
    }
  }

  async function handleCreate() {
    if (!newExperimentName.trim()) {
      showToast('Please enter an experiment name', 'error');
      return;
    }

    try {
      await createExperiment(newExperimentName, newExperimentDescription);
      showToast(`Created experiment: ${newExperimentName}`, 'success');
      newExperimentName = '';
      newExperimentDescription = '';
      isCreating = false;
      // Refresh experiments list
      window.location.reload();
    } catch (error) {
      showToast(error.message, 'error');
    }
  }

  function handleDiscard(experiment) {
    showModal({
      title: 'Discard Experiment',
      message: `Are you sure you want to discard "${experiment.name}"? This cannot be undone.`,
      confirmText: 'Discard',
      cancelText: 'Cancel',
      onConfirm: async () => {
        try {
          await discardExperiment(experiment.name);
          showToast(`Discarded experiment: ${experiment.name}`, 'success');
          window.location.reload();
        } catch (error) {
          showToast(error.message, 'error');
        }
      },
    });
  }

  function cancelCreate() {
    isCreating = false;
    newExperimentName = '';
    newExperimentDescription = '';
  }
</script>

<div class="experiments-panel">
  <div class="panel-header">
    <h2 class="panel-title">🔬 Experiments</h2>
    <button class="btn-create" on:click={() => isCreating = true}>
      + New
    </button>
  </div>

  {#if isCreating}
    <div class="create-form">
      <input
        type="text"
        placeholder="Experiment name"
        bind:value={newExperimentName}
        class="input-field"
        autofocus
      />
      <textarea
        placeholder="Description (optional)"
        bind:value={newExperimentDescription}
        class="textarea-field"
        rows="3"
      />
      <div class="form-actions">
        <button class="btn btn-secondary" on:click={cancelCreate}>
          Cancel
        </button>
        <button class="btn btn-primary" on:click={handleCreate}>
          Create
        </button>
      </div>
    </div>
  {/if}

  <div class="experiments-list">
    {#if $experiments.length === 0}
      <div class="empty-state">
        <p>No experiments yet</p>
        <p class="empty-hint">Create one to start experimenting!</p>
      </div>
    {:else}
      {#each $experiments as experiment}
        <div
          class="experiment-item"
          class:active={experiment.is_active}
        >
          <div class="experiment-content">
            <div class="experiment-header">
              <span class="experiment-name">{experiment.name}</span>
              <span class="experiment-status">{experiment.status}</span>
            </div>

            {#if experiment.description}
              <p class="experiment-description">{experiment.description}</p>
            {/if}

            <div class="experiment-meta">
              <span class="meta-item">
                Base: <strong>{experiment.base_branch}</strong>
              </span>
              <span class="meta-item">{experiment.age}</span>
              {#if experiment.commits_ahead > 0}
                <span class="meta-item commits-ahead">
                  ↑ {experiment.commits_ahead} ahead
                </span>
              {/if}
              {#if experiment.commits_behind > 0}
                <span class="meta-item commits-behind">
                  ↓ {experiment.commits_behind} behind
                </span>
              {/if}
            </div>
          </div>

          <div class="experiment-actions">
            {#if !experiment.is_active}
              <button
                class="btn-action"
                on:click={() => handleSwitch(experiment)}
                title="Switch to this experiment"
              >
                Switch
              </button>
            {/if}
            <button
              class="btn-action btn-danger"
              on:click={() => handleDiscard(experiment)}
              title="Discard experiment"
              disabled={experiment.is_active}
            >
              Discard
            </button>
          </div>
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
  .experiments-panel {
    background: #1e1e1e;
    border-radius: 12px;
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .panel-title {
    margin: 0;
    font-size: 24px;
    color: #e0e0e0;
    font-weight: 600;
  }

  .btn-create {
    padding: 8px 16px;
    background: #2196f3;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-create:hover {
    background: #1976d2;
  }

  .create-form {
    background: #2d2d2d;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .input-field,
  .textarea-field {
    width: 100%;
    padding: 10px;
    background: #1e1e1e;
    border: 1px solid #444;
    border-radius: 6px;
    color: #e0e0e0;
    font-size: 14px;
    font-family: inherit;
  }

  .input-field:focus,
  .textarea-field:focus {
    outline: none;
    border-color: #2196f3;
  }

  .textarea-field {
    resize: vertical;
  }

  .form-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }

  .experiments-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #808080;
    text-align: center;
  }

  .empty-state p {
    margin: 0;
  }

  .empty-hint {
    font-size: 12px;
    margin-top: 8px !important;
  }

  .experiment-item {
    background: #2d2d2d;
    border-radius: 8px;
    padding: 16px;
    border: 2px solid transparent;
    transition: all 0.2s;
  }

  .experiment-item:hover {
    border-color: #444;
  }

  .experiment-item.active {
    border-color: #4caf50;
    background: #2a3f2a;
  }

  .experiment-content {
    margin-bottom: 12px;
  }

  .experiment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .experiment-name {
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
  }

  .experiment-status {
    font-size: 12px;
    color: #808080;
  }

  .experiment-description {
    margin: 0 0 8px 0;
    font-size: 13px;
    color: #b0b0b0;
    line-height: 1.4;
  }

  .experiment-meta {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    font-size: 11px;
    color: #808080;
  }

  .meta-item strong {
    color: #b0b0b0;
  }

  .commits-ahead {
    color: #4caf50;
  }

  .commits-behind {
    color: #ff9800;
  }

  .experiment-actions {
    display: flex;
    gap: 8px;
  }

  .btn,
  .btn-action {
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
    font-size: 13px;
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

  .btn-action {
    background: #404040;
    color: #e0e0e0;
    font-size: 12px;
    padding: 6px 12px;
  }

  .btn-action:hover:not(:disabled) {
    background: #4a4a4a;
  }

  .btn-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-danger {
    background: #5c2828;
    color: #ff6b6b;
  }

  .btn-danger:hover:not(:disabled) {
    background: #752e2e;
  }
</style>
