<script>
  import { onMount } from 'svelte';
  import { repoInfo } from '../stores/store.js';
  import { fetchRepoInfo, fetchPromptLogs, fetchPromptStats, deletePromptLog } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Topbar from './Topbar.svelte';
  import ThemePicker from './ThemePicker.svelte';

  let prompts = [];
  let stats = null;
  let loading = true;
  let error = null;
  let sortColumn = 'timestamp';
  let sortDirection = 'desc';
  let searchQuery = '';

  // Pricing table state
  let showPricing = false;
  let pricingData = [];
  let pricingLoading = false;
  let pricingError = null;
  let pricingSearch = '';
  let pricingProvider = 'all';
  let pricingSortColumn = 'input_cost';
  let pricingSortDirection = 'asc';

  const LITELLM_PRICING_URL = 'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json';

  async function loadPricing() {
    if (pricingData.length > 0) return; // Already loaded
    pricingLoading = true;
    pricingError = null;
    try {
      const response = await fetch(LITELLM_PRICING_URL);
      const data = await response.json();

      // Transform to array, filter out sample_spec and non-chat models
      pricingData = Object.entries(data)
        .filter(([key, val]) => {
          if (key === 'sample_spec') return false;
          if (!val.input_cost_per_token && !val.input_cost_per_character) return false;
          // Skip image-only models
          if (val.mode === 'image_generation') return false;
          return true;
        })
        .map(([model, info]) => {
          // Extract provider from model name or litellm_provider
          let provider = info.litellm_provider || 'unknown';
          if (model.startsWith('gpt-') || model.startsWith('o1') || model.startsWith('o3') || model.startsWith('o4')) provider = 'openai';
          else if (model.includes('claude')) provider = 'anthropic';
          else if (model.includes('gemini')) provider = 'google';
          else if (model.includes('mistral') || model.includes('mixtral')) provider = 'mistral';
          else if (model.includes('llama')) provider = 'meta';
          else if (model.includes('command')) provider = 'cohere';
          else if (model.includes('deepseek')) provider = 'deepseek';

          const inputCost = (info.input_cost_per_token || 0) * 1_000_000;
          const outputCost = (info.output_cost_per_token || 0) * 1_000_000;

          return {
            model,
            provider,
            input_cost: inputCost,
            output_cost: outputCost,
            max_input: info.max_input_tokens || info.max_tokens || 0,
            max_output: info.max_output_tokens || 0,
            supports_vision: info.supports_vision || false,
            supports_function_calling: info.supports_function_calling || false
          };
        })
        .filter(m => m.input_cost > 0 || m.output_cost > 0);
    } catch (err) {
      console.error('Failed to load pricing:', err);
      pricingError = err.message;
    } finally {
      pricingLoading = false;
    }
  }

  function togglePricing() {
    showPricing = !showPricing;
    if (showPricing) {
      loadPricing();
    }
  }

  function sortPricingBy(column) {
    if (pricingSortColumn === column) {
      pricingSortDirection = pricingSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      pricingSortColumn = column;
      pricingSortDirection = 'asc';
    }
  }

  function formatPrice(price) {
    if (price === 0) return '-';
    if (price < 0.01) return `$${price.toFixed(4)}`;
    if (price < 1) return `$${price.toFixed(3)}`;
    return `$${price.toFixed(2)}`;
  }

  function formatContext(tokens) {
    if (!tokens) return '-';
    if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
    if (tokens >= 1000) return `${Math.round(tokens / 1000)}k`;
    return tokens.toString();
  }

  $: uniqueProviders = [...new Set(pricingData.map(m => m.provider))].sort();

  $: filteredPricing = pricingData.filter(m => {
    const matchesSearch = m.model.toLowerCase().includes(pricingSearch.toLowerCase()) ||
                          m.provider.toLowerCase().includes(pricingSearch.toLowerCase());
    const matchesProvider = pricingProvider === 'all' || m.provider === pricingProvider;
    return matchesSearch && matchesProvider;
  });

  $: sortedPricing = [...filteredPricing].sort((a, b) => {
    let aVal = a[pricingSortColumn];
    let bVal = b[pricingSortColumn];
    if (typeof aVal === 'string') {
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }
    if (pricingSortDirection === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  async function loadPrompts() {
    loading = true;
    error = null;
    try {
      const [logsResult, statsResult] = await Promise.all([
        fetchPromptLogs({ limit: 500 }),
        fetchPromptStats()
      ]);
      prompts = logsResult.prompts || [];
      stats = statsResult.stats || null;
    } catch (err) {
      console.error('Failed to load prompts:', err);
      error = err.message;
      prompts = [];
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    if (!$repoInfo || !$repoInfo.path) {
      try {
        const info = await fetchRepoInfo();
        repoInfo.set(info);
      } catch (err) {
        console.error('Failed to load repo info:', err);
      }
    }
    await loadPrompts();
  });

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

  $: totalCost = stats?.totalCost ?? prompts.reduce((sum, p) => sum + (p.cost || 0), 0);
  $: totalTokens = stats?.totalTokens ?? prompts.reduce((sum, p) => sum + (p.totalTokens || 0), 0);
  $: totalPrompts = stats?.totalPrompts ?? prompts.length;

  let copiedId = null;
  let selectedPrompt = null;
  let selectedIds = new Set();
  let copiedModal = null;
  let copiedMulti = false;

  function copyPromptJson(prompt, event) {
    event.stopPropagation();
    const json = JSON.stringify(prompt, null, 2);
    navigator.clipboard.writeText(json).then(() => {
      copiedId = prompt.id;
      setTimeout(() => copiedId = null, 2000);
    });
  }

  function copyPromptText(text, field) {
    navigator.clipboard.writeText(text).then(() => {
      copiedModal = field;
      setTimeout(() => copiedModal = null, 2000);
    });
  }

  function openModal(prompt) {
    selectedPrompt = prompt;
  }

  function closeModal() {
    selectedPrompt = null;
  }

  function handleKeydown(event) {
    if (event.key === 'Escape' && selectedPrompt) {
      closeModal();
    }
  }

  function toggleSelect(id, event) {
    event.stopPropagation();
    if (selectedIds.has(id)) {
      selectedIds.delete(id);
    } else {
      selectedIds.add(id);
    }
    selectedIds = selectedIds; // trigger reactivity
  }

  function toggleSelectAll() {
    if (selectedIds.size === sortedPrompts.length) {
      selectedIds = new Set();
    } else {
      selectedIds = new Set(sortedPrompts.map(p => p.id));
    }
  }

  function copySelectedPrompts() {
    const selected = sortedPrompts.filter(p => selectedIds.has(p.id));
    const json = JSON.stringify(selected, null, 2);
    navigator.clipboard.writeText(json).then(() => {
      copiedMulti = true;
      setTimeout(() => copiedMulti = false, 2000);
    });
  }

  function clearSelection() {
    selectedIds = new Set();
  }

  $: hasSelection = selectedIds.size > 0;
</script>

<svelte:window on:keydown={handleKeydown} />

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
          <span class="stat-value">{totalPrompts}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Total Tokens</span>
          <span class="stat-value">{formatTokens(totalTokens)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Total Cost</span>
          <span class="stat-value">{formatCost(totalCost)}</span>
        </div>
        {#if stats?.avgDuration}
          <div class="stat">
            <span class="stat-label">Avg Duration</span>
            <span class="stat-value">{formatDuration(stats.avgDuration)}</span>
          </div>
        {/if}
        {#if stats?.errorCount > 0}
          <div class="stat stat-error">
            <span class="stat-label">Errors</span>
            <span class="stat-value">{stats.errorCount}</span>
          </div>
        {/if}
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
          {#if hasSelection}
            <div class="selection-bar">
              <span>{selectedIds.size} selected</span>
              <button class="selection-btn" class:copied={copiedMulti} on:click={copySelectedPrompts}>
                {copiedMulti ? '✓ Copied' : 'Copy Selected'}
              </button>
              <button class="selection-btn clear" on:click={clearSelection}>Clear</button>
            </div>
          {/if}
          <table class="prompts-table">
            <thead>
              <tr>
                <th class="checkbox-col">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === sortedPrompts.length && sortedPrompts.length > 0}
                    on:change={toggleSelectAll}
                  />
                </th>
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
                <th class="sortable" class:sorted={sortColumn === 'totalTokens'} on:click={() => sortBy('totalTokens')}>
                  Total
                  {#if sortColumn === 'totalTokens'}
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
                <th>Response</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {#each sortedPrompts as prompt (prompt.id)}
                <tr class:error={prompt.status === 'error'} class:selected={selectedIds.has(prompt.id)} class="clickable-row" on:click={() => openModal(prompt)}>
                  <td class="checkbox-col" on:click|stopPropagation>
                    <input
                      type="checkbox"
                      checked={selectedIds.has(prompt.id)}
                      on:change={(e) => toggleSelect(prompt.id, e)}
                    />
                  </td>
                  <td class="timestamp">{formatTimestamp(prompt.timestamp)}</td>
                  <td>
                    <span class="provider-badge" class:anthropic={prompt.provider === 'anthropic'} class:openai={prompt.provider === 'openai'}>
                      {prompt.provider}
                    </span>
                  </td>
                  <td class="model">{prompt.model}</td>
                  <td class="tokens">{formatTokens(prompt.inputTokens)}</td>
                  <td class="tokens">{formatTokens(prompt.outputTokens)}</td>
                  <td class="tokens">{formatTokens(prompt.totalTokens)}</td>
                  <td class="cost">{formatCost(prompt.cost)}</td>
                  <td class="duration">{formatDuration(prompt.duration)}</td>
                  <td class="preview">{prompt.promptPreview}</td>
                  <td class="preview">{prompt.responsePreview}</td>
                  <td>
                    <span class="status-badge" class:success={prompt.status === 'success'} class:error={prompt.status === 'error'}>
                      {prompt.status}
                    </span>
                  </td>
                  <td class="actions">
                    <button
                      class="copy-btn"
                      class:copied={copiedId === prompt.id}
                      on:click={(e) => copyPromptJson(prompt, e)}
                      title="Copy JSON"
                    >
                      {copiedId === prompt.id ? '✓' : '⧉'}
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>

      <!-- LLM Pricing Table -->
      <div class="pricing-section">
        <button class="pricing-toggle" on:click={togglePricing}>
          <span class="toggle-icon">{showPricing ? '▼' : '▶'}</span>
          <span>LLM Pricing Reference</span>
          <span class="pricing-source">via LiteLLM</span>
        </button>

        {#if showPricing}
          <div class="pricing-content">
            <div class="pricing-header">
              <div class="pricing-filters">
                <input
                  type="text"
                  placeholder="Search models..."
                  bind:value={pricingSearch}
                  class="pricing-search"
                />
                <select bind:value={pricingProvider} class="pricing-provider-select">
                  <option value="all">All Providers</option>
                  {#each uniqueProviders as provider}
                    <option value={provider}>{provider}</option>
                  {/each}
                </select>
              </div>
              <span class="pricing-count">{filteredPricing.length} models</span>
            </div>

            {#if pricingLoading}
              <div class="pricing-loading">Loading pricing data...</div>
            {:else if pricingError}
              <div class="pricing-error">Failed to load pricing: {pricingError}</div>
            {:else}
              <div class="pricing-table-wrapper">
                <table class="pricing-table">
                  <thead>
                    <tr>
                      <th class="sortable" class:sorted={pricingSortColumn === 'provider'} on:click={() => sortPricingBy('provider')}>
                        Provider
                        {#if pricingSortColumn === 'provider'}
                          <span class="sort-indicator">{pricingSortDirection === 'asc' ? '↑' : '↓'}</span>
                        {/if}
                      </th>
                      <th class="sortable" class:sorted={pricingSortColumn === 'model'} on:click={() => sortPricingBy('model')}>
                        Model
                        {#if pricingSortColumn === 'model'}
                          <span class="sort-indicator">{pricingSortDirection === 'asc' ? '↑' : '↓'}</span>
                        {/if}
                      </th>
                      <th class="sortable" class:sorted={pricingSortColumn === 'input_cost'} on:click={() => sortPricingBy('input_cost')}>
                        Input/1M
                        {#if pricingSortColumn === 'input_cost'}
                          <span class="sort-indicator">{pricingSortDirection === 'asc' ? '↑' : '↓'}</span>
                        {/if}
                      </th>
                      <th class="sortable" class:sorted={pricingSortColumn === 'output_cost'} on:click={() => sortPricingBy('output_cost')}>
                        Output/1M
                        {#if pricingSortColumn === 'output_cost'}
                          <span class="sort-indicator">{pricingSortDirection === 'asc' ? '↑' : '↓'}</span>
                        {/if}
                      </th>
                      <th class="sortable" class:sorted={pricingSortColumn === 'max_input'} on:click={() => sortPricingBy('max_input')}>
                        Context
                        {#if pricingSortColumn === 'max_input'}
                          <span class="sort-indicator">{pricingSortDirection === 'asc' ? '↑' : '↓'}</span>
                        {/if}
                      </th>
                      <th>Features</th>
                    </tr>
                  </thead>
                  <tbody>
                    {#each sortedPricing.slice(0, 100) as model (model.model)}
                      <tr>
                        <td>
                          <span class="provider-badge provider-{model.provider}">{model.provider}</span>
                        </td>
                        <td class="model-name">{model.model}</td>
                        <td class="price">{formatPrice(model.input_cost)}</td>
                        <td class="price">{formatPrice(model.output_cost)}</td>
                        <td class="context">{formatContext(model.max_input)}</td>
                        <td class="features">
                          {#if model.supports_vision}
                            <span class="feature-tag" title="Vision">V</span>
                          {/if}
                          {#if model.supports_function_calling}
                            <span class="feature-tag" title="Function Calling">F</span>
                          {/if}
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
              {#if sortedPricing.length > 100}
                <div class="pricing-more">Showing 100 of {sortedPricing.length} models. Use search to filter.</div>
              {/if}
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <footer class="app-footer">
    <div class="footer-left">
    </div>

    <div class="footer-center">
    </div>

    <div class="footer-right">
      <ThemePicker compact={true} />
    </div>
  </footer>

  <Toast />

  {#if selectedPrompt}
    <div class="modal-overlay" on:click={closeModal}>
      <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
          <h3>Prompt Details</h3>
          <button class="modal-close" on:click={closeModal}>×</button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Time</span>
              <span class="detail-value">{formatTimestamp(selectedPrompt.timestamp)}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Provider</span>
              <span class="detail-value">{selectedPrompt.provider}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Model</span>
              <span class="detail-value">{selectedPrompt.model}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Session ID</span>
              <span class="detail-value mono">{selectedPrompt.sessionId || '-'}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Input Tokens</span>
              <span class="detail-value">{formatTokens(selectedPrompt.inputTokens)}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Output Tokens</span>
              <span class="detail-value">{formatTokens(selectedPrompt.outputTokens)}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Total Tokens</span>
              <span class="detail-value">{formatTokens(selectedPrompt.totalTokens)}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Cost</span>
              <span class="detail-value">{formatCost(selectedPrompt.cost)}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Duration</span>
              <span class="detail-value">{formatDuration(selectedPrompt.duration)}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status</span>
              <span class="detail-value">
                <span class="status-badge" class:success={selectedPrompt.status === 'success'} class:error={selectedPrompt.status === 'error'}>
                  {selectedPrompt.status}
                </span>
              </span>
            </div>
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4>Prompt</h4>
              {#if selectedPrompt.promptPreview}
                <button
                  class="copy-text-btn"
                  class:copied={copiedModal === 'prompt'}
                  on:click={() => copyPromptText(selectedPrompt.promptPreview, 'prompt')}
                >
                  {copiedModal === 'prompt' ? '✓' : 'Copy'}
                </button>
              {/if}
            </div>
            <div class="detail-text">{selectedPrompt.promptPreview || '(empty)'}</div>
          </div>

          <div class="detail-section">
            <div class="section-header">
              <h4>Response</h4>
              {#if selectedPrompt.responsePreview}
                <button
                  class="copy-text-btn"
                  class:copied={copiedModal === 'response'}
                  on:click={() => copyPromptText(selectedPrompt.responsePreview, 'response')}
                >
                  {copiedModal === 'response' ? '✓' : 'Copy'}
                </button>
              {/if}
            </div>
            <div class="detail-text">{selectedPrompt.responsePreview || '(empty)'}</div>
          </div>

          {#if selectedPrompt.errorMessage}
            <div class="detail-section error-section">
              <h4>Error</h4>
              <div class="detail-text error-text">{selectedPrompt.errorMessage}</div>
            </div>
          {/if}

          <div class="detail-section">
            <h4>JSON</h4>
            <pre class="json-preview">{JSON.stringify(selectedPrompt, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  {/if}
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

  .stat-error .stat-value {
    color: #ef4444;
  }

  .prompts-content {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    overflow-x: auto;
    overflow-y: hidden;
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
    min-width: 1200px;
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

  .actions {
    text-align: center;
    width: 40px;
  }

  .copy-btn {
    padding: 4px 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 3px;
    color: var(--text-secondary);
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .copy-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    border-color: var(--accent-primary);
  }

  .copy-btn.copied {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border-color: #22c55e;
  }

  .clickable-row {
    cursor: pointer;
  }

  .clickable-row:hover {
    background: var(--bg-hover);
  }

  .clickable-row.selected {
    background: rgba(59, 130, 246, 0.1);
  }

  .checkbox-col {
    width: 40px;
    text-align: center;
  }

  .checkbox-col input {
    cursor: pointer;
  }

  .selection-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--accent-primary);
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    font-size: 13px;
    color: var(--text-primary);
  }

  .selection-btn {
    padding: 4px 12px;
    background: var(--accent-primary);
    border: none;
    border-radius: 3px;
    color: white;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .selection-btn:hover {
    opacity: 0.9;
  }

  .selection-btn.copied {
    background: #22c55e;
  }

  .selection-btn.clear {
    background: transparent;
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
  }

  .selection-btn.clear:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  /* Modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    width: 90%;
    max-width: 700px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-primary);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 24px;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  .modal-close:hover {
    color: var(--text-primary);
  }

  .modal-body {
    padding: 20px;
    overflow-y: auto;
  }

  .detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .detail-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .detail-value {
    font-size: 14px;
    color: var(--text-primary);
  }

  .detail-value.mono {
    font-family: 'Courier New', monospace;
    font-size: 12px;
  }

  .detail-section {
    margin-bottom: 20px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .section-header h4 {
    margin: 0;
  }

  .copy-text-btn {
    padding: 3px 10px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 3px;
    color: var(--text-secondary);
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .copy-text-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    border-color: var(--accent-primary);
  }

  .copy-text-btn.copied {
    background: rgba(34, 197, 94, 0.15);
    color: #22c55e;
    border-color: #22c55e;
  }

  .detail-section h4 {
    margin: 0 0 8px 0;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .detail-text {
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .error-section .detail-text {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: #ef4444;
  }

  .json-preview {
    margin: 0;
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-secondary);
    overflow-x: auto;
    max-height: 200px;
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

  /* Pricing Section */
  .pricing-section {
    margin-top: 24px;
  }

  .pricing-toggle {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .pricing-toggle:hover {
    background: var(--bg-hover);
    border-color: var(--accent-primary);
  }

  .toggle-icon {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .pricing-source {
    margin-left: auto;
    font-size: 11px;
    color: var(--text-tertiary);
    font-weight: 400;
  }

  .pricing-content {
    margin-top: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    overflow: hidden;
  }

  .pricing-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-primary);
    background: var(--bg-secondary);
  }

  .pricing-filters {
    display: flex;
    gap: 8px;
  }

  .pricing-search {
    padding: 6px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 3px;
    color: var(--text-primary);
    font-size: 12px;
    width: 180px;
  }

  .pricing-search:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .pricing-provider-select {
    padding: 6px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 3px;
    color: var(--text-primary);
    font-size: 12px;
  }

  .pricing-count {
    font-size: 12px;
    color: var(--text-tertiary);
  }

  .pricing-loading,
  .pricing-error {
    padding: 32px;
    text-align: center;
    color: var(--text-secondary);
  }

  .pricing-error {
    color: #ef4444;
  }

  .pricing-table-wrapper {
    max-height: 400px;
    overflow: auto;
  }

  .pricing-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }

  .pricing-table th {
    padding: 10px 12px;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 1;
  }

  .pricing-table td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-secondary);
    color: var(--text-primary);
  }

  .pricing-table tr:hover {
    background: var(--bg-hover);
  }

  .pricing-table .model-name {
    font-family: 'Courier New', monospace;
    font-size: 11px;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .pricing-table .price {
    font-family: 'Courier New', monospace;
    text-align: right;
    color: var(--accent-primary);
  }

  .pricing-table .context {
    font-family: 'Courier New', monospace;
    text-align: right;
    color: var(--text-secondary);
  }

  .pricing-table .features {
    display: flex;
    gap: 4px;
  }

  .feature-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 600;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
  }

  .provider-badge.provider-anthropic { background: rgba(204, 119, 34, 0.15); color: #cc7722; }
  .provider-badge.provider-openai { background: rgba(16, 163, 127, 0.15); color: #10a37f; }
  .provider-badge.provider-google { background: rgba(66, 133, 244, 0.15); color: #4285f4; }
  .provider-badge.provider-mistral { background: rgba(255, 107, 53, 0.15); color: #ff6b35; }
  .provider-badge.provider-meta { background: rgba(0, 122, 255, 0.15); color: #007aff; }
  .provider-badge.provider-cohere { background: rgba(117, 81, 233, 0.15); color: #7551e9; }
  .provider-badge.provider-deepseek { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }

  .pricing-more {
    padding: 12px;
    text-align: center;
    font-size: 12px;
    color: var(--text-tertiary);
    border-top: 1px solid var(--border-primary);
    background: var(--bg-secondary);
  }
</style>
