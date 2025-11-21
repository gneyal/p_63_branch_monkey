<script>
  import { Handle, Position } from '@xyflow/svelte';
  import { showToast } from '../stores/store.js';

  export let data;

  const { date, commits, formattedDate, height } = data;

  let selectedCommit = null;

  function getBuildingHeight(commitCount) {
    return Math.min(commitCount * 40, 600);
  }

  function handleCommitClick(commit, event) {
    event.stopPropagation();
    selectedCommit = selectedCommit?.sha === commit.sha ? null : commit;
    showToast(`Selected: ${commit.sha} - ${commit.message}`, 'info');
  }

  function copySHA(sha, event) {
    event.stopPropagation();
    navigator.clipboard.writeText(sha);
    showToast('SHA copied to clipboard', 'success');
  }
</script>

<div class="building-node">
  <div class="date-label">{formattedDate}</div>
  <div
    class="building"
    style="height: {height}px;"
  >
    {#each commits as commit, i}
      <div
        class="commit-floor"
        class:selected={selectedCommit?.sha === commit.sha}
        title="{commit.message}"
        on:click={(e) => handleCommitClick(commit, e)}
      >
        <div class="floor-content">
          <span class="commit-sha">{commit.sha}</span>
          <span class="commit-message">
            {commit.message.length > 30 ? commit.message.substring(0, 30) + '...' : commit.message}
          </span>
        </div>
      </div>
    {/each}
  </div>
  <div class="commit-count">{commits.length} commit{commits.length !== 1 ? 's' : ''}</div>
</div>

{#if selectedCommit}
  <div class="commit-detail-panel z-[1100]" on:click|stopPropagation>
    <div class="panel-header">
      <div class="panel-title">
        <span class="detail-sha">{selectedCommit.sha}</span>
        <button class="copy-btn" on:click={(e) => copySHA(selectedCommit.fullSha || selectedCommit.sha, e)} title="Copy SHA">
          📋
        </button>
      </div>
      <button class="close-btn" on:click={() => selectedCommit = null}>✕</button>
    </div>
    <div class="panel-content">
      <div class="detail-section">
        <label>Message</label>
        <p>{selectedCommit.message}</p>
      </div>
      <div class="detail-section">
        <label>Author</label>
        <p>{selectedCommit.author}</p>
      </div>
      <div class="detail-section">
        <label>Age</label>
        <p>{selectedCommit.age}</p>
      </div>
    </div>
  </div>
{/if}

<style>
  .building-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .date-label {
    font-size: 10px;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    white-space: nowrap;
  }

  .building {
    width: 60px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px 2px 0 0;
    display: flex;
    flex-direction: column-reverse;
    transition: all 0.2s ease;
    position: relative;
  }

  .building:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-large);
    border-color: var(--border-hover);
    z-index: 10;
  }

  .building:hover .commit-floor {
    opacity: 1;
  }

  .commit-floor {
    min-height: 40px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    align-items: center;
    padding: 4px;
    transition: all 0.2s;
    opacity: 0.7;
    cursor: pointer;
  }

  .commit-floor:last-child {
    border-bottom: none;
  }

  .commit-floor:hover {
    background: var(--bg-hover);
    opacity: 1;
    transform: scale(1.05);
    z-index: 5;
  }

  .commit-floor.selected {
    background: var(--accent-primary);
    opacity: 1;
  }

  .commit-floor.selected .commit-sha,
  .commit-floor.selected .commit-message {
    color: var(--bg-primary);
  }

  .floor-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    font-size: 8px;
    overflow: hidden;
    width: 100%;
  }

  .commit-sha {
    font-family: 'Courier', monospace;
    color: var(--text-primary);
    font-weight: 600;
    font-size: 9px;
  }

  .commit-message {
    color: var(--text-tertiary);
    font-size: 7px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .commit-count {
    font-size: 9px;
    color: var(--text-tertiary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .commit-detail-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    width: 400px;
    max-width: 90vw;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
    animation: panelSlideIn 0.2s ease;
    z-index: 1100;
  }

  @keyframes panelSlideIn {
    from {
      opacity: 0;
      transform: translate(-50%, -50%) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translate(-50%, -50%) scale(1);
    }
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-primary);
    background: var(--bg-secondary);
  }

  .panel-title {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .detail-sha {
    font-family: 'Courier', monospace;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .copy-btn {
    padding: 4px 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .copy-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .close-btn {
    padding: 4px 8px;
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .close-btn:hover {
    color: var(--text-primary);
  }

  .panel-content {
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .detail-section {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .detail-section label {
    font-size: 9px;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .detail-section p {
    margin: 0;
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.5;
  }
</style>
