<script>
  import { Handle, Position } from '@xyflow/svelte';

  export let data;

  const { date, commits, formattedDate, height } = data;

  function getBuildingHeight(commitCount) {
    return Math.min(commitCount * 40, 600);
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
        title="{commit.message}"
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
</style>
