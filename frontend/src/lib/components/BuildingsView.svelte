<script>
  import { onMount } from 'svelte';

  export let commits = [];

  let groupBy = 'day'; // 'day' or 'week'
  let buildings = [];

  $: if (commits.length > 0) {
    buildTimeline();
  }

  function buildTimeline() {
    // Group commits by date
    const groups = new Map();

    commits.forEach(commit => {
      const date = new Date(commit.timestamp || Date.now());
      let key;

      if (groupBy === 'day') {
        key = date.toISOString().split('T')[0]; // YYYY-MM-DD
      } else {
        // Week grouping
        const weekStart = getWeekStart(date);
        key = weekStart.toISOString().split('T')[0];
      }

      if (!groups.has(key)) {
        groups.set(key, {
          date: key,
          commits: []
        });
      }

      groups.get(key).commits.push(commit);
    });

    // Convert to array and sort by date
    buildings = Array.from(groups.values()).sort((a, b) =>
      new Date(a.date) - new Date(b.date)
    );
  }

  function getWeekStart(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr);
    if (groupBy === 'day') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else {
      return `Week of ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
    }
  }

  function getBuildingHeight(commitCount) {
    return Math.min(commitCount * 40, 600); // 40px per commit, max 600px
  }
</script>

<div class="buildings-view">
  <div class="view-controls">
    <div class="group-toggle">
      <button
        class="toggle-btn"
        class:active={groupBy === 'day'}
        on:click={() => groupBy = 'day'}
      >
        Day
      </button>
      <button
        class="toggle-btn"
        class:active={groupBy === 'week'}
        on:click={() => groupBy = 'week'}
      >
        Week
      </button>
    </div>
  </div>

  <div class="timeline-container">
    <div class="timeline">
      {#each buildings as building}
        <div class="building-column">
          <div class="date-label">{formatDate(building.date)}</div>
          <div
            class="building"
            style="height: {getBuildingHeight(building.commits.length)}px;"
          >
            {#each building.commits as commit, i}
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
          <div class="commit-count">{building.commits.length} commit{building.commits.length !== 1 ? 's' : ''}</div>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .buildings-view {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
  }

  .view-controls {
    padding: 16px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: center;
  }

  .group-toggle {
    display: flex;
    gap: 4px;
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    overflow: hidden;
  }

  .toggle-btn {
    padding: 6px 16px;
    background: var(--bg-primary);
    border: none;
    color: var(--text-secondary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .toggle-btn.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .timeline-container {
    flex: 1;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 32px;
  }

  .timeline {
    display: flex;
    gap: 24px;
    align-items: flex-end;
    min-height: 100%;
    padding-bottom: 60px;
  }

  .building-column {
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
    writing-mode: horizontal-tb;
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
