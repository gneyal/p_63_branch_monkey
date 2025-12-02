<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { repoInfo } from '../stores/store.js';
  import { fetchRepoInfo } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Topbar from './Topbar.svelte';
  import GlobalActions from './GlobalActions.svelte';
  import ThemePicker from './ThemePicker.svelte';

  // Placeholder for prompts data
  let prompts = [];
  let loading = false;
  let sortColumn = 'timestamp';
  let sortDirection = 'desc';
  let searchQuery = '';

  // Mock data for now - this will be replaced with API calls
  const mockPrompts = [
    {
      id: 1,
      timestamp: '2024-12-02T10:30:00Z',
      provider: 'anthropic',
      model: 'claude-3-opus',
      inputTokens: 1250,
      outputTokens: 850,
      totalTokens: 2100,
      cost: 0.0315,
      duration: 3.2,
      promptPreview: 'Explain the architecture of this codebase...',
      status: 'success'
    },
    {
      id: 2,
      timestamp: '2024-12-02T10:25:00Z',
      provider: 'anthropic',
      model: 'claude-3-sonnet',
      inputTokens: 800,
      outputTokens: 1200,
      totalTokens: 2000,
      cost: 0.012,
      duration: 2.1,
      promptPreview: 'Write a function that handles user authentication...',
      status: 'success'
    },
    {
      id: 3,
      timestamp: '2024-12-02T10:20:00Z',
      provider: 'openai',
      model: 'gpt-4-turbo',
      inputTokens: 500,
      outputTokens: 300,
      totalTokens: 800,
      cost: 0.024,
      duration: 1.8,
      promptPreview: 'Debug this error in the payment processing...',
      status: 'success'
    },
    {
      id: 4,
      timestamp: '2024-12-02T10:15:00Z',
      provider: 'anthropic',
      model: 'claude-3-haiku',
      inputTokens: 200,
      outputTokens: 150,
      totalTokens: 350,
      cost: 0.0007,
      duration: 0.5,
      promptPreview: 'Format this JSON data...',
      status: 'success'
    },
    {
      id: 5,
      timestamp: '2024-12-02T10:10:00Z',
      provider: 'openai',
      model: 'gpt-4',
      inputTokens: 1500,
      outputTokens: 2000,
      totalTokens: 3500,
      cost: 0.105,
      duration: 8.5,
      promptPreview: 'Refactor this entire module to use TypeScript...',
      status: 'error'
    }
  ];

  onMount(async () => {
    if (!$repoInfo || !$repoInfo.path) {
      try {
        const info = await fetchRepoInfo();
        repoInfo.set(info);
      } catch (err) {
        console.error('Failed to load repo info:', err);
      }
    }
    // Load mock data for now
    prompts = mockPrompts;
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
    // Already on prompts page
  }

  function handleShowContext() {
    push('/commits');
  }

  function formatTimestamp(ts) {
    const date = new Date(ts);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function formatCost(cost) {
    return `$${cost.toFixed(4)}`;
  }

  function formatDuration(seconds) {
    return `${seconds.toFixed(1)}s`;
  }

  function formatTokens(tokens) {
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(1)}k`;
    }
    return tokens.toString();
  }

  function sortBy(column) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'desc';
    }
  }

  $: filteredPrompts = prompts.filter(p =>
    p.promptPreview.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.model.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.provider.toLowerCase().includes(searchQuery.toLowerCase())
  );

  $: sortedPrompts = [...filteredPrompts].sort((a, b) => {
    let aVal = a[sortColumn];
    let bVal = b[sortColumn];

    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }

    if (sortDirection === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  $: totalCost = prompts.reduce((sum, p) => sum + p.cost, 0);
  $: totalTokens = prompts.reduce((sum, p) => sum + p.totalTokens, 0);
</script>

<main class="prompts-page">
  <Topbar activeView="prompts" />

  <div class="page-content">
    <div class="prompts-container">
      <div class="prompts-header">
        <div class="header-left">
          <h2>Prompts</h2>
          <p class="prompts-description">
            History of AI prompts with token usage, costs, and performance metrics.
          </p>
        </div>
        <div class="header-right">
          <div class="search-box">
            <input
              type="text"
              placeholder="Search prompts..."
              bind:value={searchQuery}
            />
          </div>
        </div>
      </div>

      <div class="stats-bar">
        <div class="stat">
          <span class="stat-label">Total Prompts</span>
          <span class="stat-value">{prompts.length}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Total Tokens</span>
          <span class="stat-value">{formatTokens(totalTokens)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Total Cost</span>
          <span class="stat-value">{formatCost(totalCost)}</span>
        </div>
      </div>

      <div class="prompts-content">
        {#if loading}
          <div class="loading-state">Loading prompts...</div>
        {:else if sortedPrompts.length === 0}
          <div class="empty-state">
            <div class="empty-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"/>
              </svg>
            </div>
            <h3>No prompts yet</h3>
            <p>Prompt history will appear here as you interact with AI assistants.</p>
          </div>
        {:else}
          <table class="prompts-table">
            <thead>
              <tr>
                <th class="sortable" class:sorted={sortColumn === 'timestamp'} on:click={() => sortBy('timestamp')}>
                  Time
                  {#if sortColumn === 'timestamp'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th class="sortable" class:sorted={sortColumn === 'provider'} on:click={() => sortBy('provider')}>
                  Provider
                  {#if sortColumn === 'provider'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th class="sortable" class:sorted={sortColumn === 'model'} on:click={() => sortBy('model')}>
                  Model
                  {#if sortColumn === 'model'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th class="sortable" class:sorted={sortColumn === 'inputTokens'} on:click={() => sortBy('inputTokens')}>
                  Input
                  {#if sortColumn === 'inputTokens'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th class="sortable" class:sorted={sortColumn === 'outputTokens'} on:click={() => sortBy('outputTokens')}>
                  Output
                  {#if sortColumn === 'outputTokens'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th class="sortable" class:sorted={sortColumn === 'cost'} on:click={() => sortBy('cost')}>
                  Cost
                  {#if sortColumn === 'cost'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th class="sortable" class:sorted={sortColumn === 'duration'} on:click={() => sortBy('duration')}>
                  Duration
                  {#if sortColumn === 'duration'}
                    <span class="sort-indicator">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  {/if}
                </th>
                <th>Prompt</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {#each sortedPrompts as prompt (prompt.id)}
                <tr class:error={prompt.status === 'error'}>
                  <td class="timestamp">{formatTimestamp(prompt.timestamp)}</td>
                  <td>
                    <span class="provider-badge" class:anthropic={prompt.provider === 'anthropic'} class:openai={prompt.provider === 'openai'}>
                      {prompt.provider}
                    </span>
                  </td>
                  <td class="model">{prompt.model}</td>
                  <td class="tokens">{formatTokens(prompt.inputTokens)}</td>
                  <td class="tokens">{formatTokens(prompt.outputTokens)}</td>
                  <td class="cost">{formatCost(prompt.cost)}</td>
                  <td class="duration">{formatDuration(prompt.duration)}</td>
                  <td class="preview">{prompt.promptPreview}</td>
                  <td>
                    <span class="status-badge" class:success={prompt.status === 'success'} class:error={prompt.status === 'error'}>
                      {prompt.status}
                    </span>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
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
      <ThemePicker compact={true} />
    </div>
  </footer>

  <Toast />
</main>

<style>
  .prompts-page {
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

  .prompts-container {
    max-width: 1400px;
    margin: 0 auto;
  }

  .prompts-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    gap: 24px;
  }

  .header-left h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .prompts-description {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }

  .search-box input {
    padding: 8px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 13px;
    width: 250px;
  }

  .search-box input:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .search-box input::placeholder {
    color: var(--text-tertiary);
  }

  .stats-bar {
    display: flex;
    gap: 24px;
    margin-bottom: 16px;
    padding: 12px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .stat-label {
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .stat-value {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .prompts-content {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    overflow: hidden;
  }

  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    color: var(--text-secondary);
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

  .prompts-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  .prompts-table th {
    padding: 12px 16px;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
    white-space: nowrap;
  }

  .prompts-table th.sortable {
    cursor: pointer;
    user-select: none;
  }

  .prompts-table th.sortable:hover {
    color: var(--text-primary);
  }

  .prompts-table th.sorted {
    color: var(--accent-primary);
  }

  .sort-indicator {
    margin-left: 4px;
  }

  .prompts-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    color: var(--text-primary);
  }

  .prompts-table tr:last-child td {
    border-bottom: none;
  }

  .prompts-table tr:hover {
    background: var(--bg-hover);
  }

  .prompts-table tr.error {
    background: rgba(239, 68, 68, 0.05);
  }

  .timestamp {
    color: var(--text-secondary);
    font-size: 12px;
    white-space: nowrap;
  }

  .model {
    font-family: 'Courier New', monospace;
    font-size: 12px;
  }

  .tokens {
    font-family: 'Courier New', monospace;
    text-align: right;
  }

  .cost {
    font-family: 'Courier New', monospace;
    color: var(--accent-primary);
    text-align: right;
  }

  .duration {
    font-family: 'Courier New', monospace;
    text-align: right;
    color: var(--text-secondary);
  }

  .preview {
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--text-secondary);
  }

  .provider-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .provider-badge.anthropic {
    background: rgba(204, 119, 34, 0.15);
    color: #cc7722;
  }

  .provider-badge.openai {
    background: rgba(16, 163, 127, 0.15);
    color: #10a37f;
  }

  .status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .status-badge.success {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
  }

  .status-badge.error {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
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

  @media (max-width: 768px) {
    .prompts-header {
      flex-direction: column;
    }

    .search-box input {
      width: 100%;
    }

    .stats-bar {
      flex-wrap: wrap;
    }

    .app-footer {
      grid-template-columns: 1fr;
      gap: 8px;
      padding: 8px 16px;
    }

    .footer-left,
    .footer-center,
    .footer-right {
      justify-content: center;
    }
  }
</style>
