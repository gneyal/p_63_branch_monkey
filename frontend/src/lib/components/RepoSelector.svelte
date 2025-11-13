<script>
  import { repoInfo, showToast } from '../stores/store.js';
  import { searchRepoPaths, setRepoPath, fetchRepoInfo } from '../services/api.js';

  let inputValue = '';
  let suggestions = [];
  let showSuggestions = false;
  let searchTimeout = null;
  let favorites = [];
  let showFavorites = false;

  // Load favorites from localStorage
  function loadFavorites() {
    const stored = localStorage.getItem('branchMonkeyFavorites');
    favorites = stored ? JSON.parse(stored) : [];
  }

  // Save favorites to localStorage
  function saveFavorites() {
    localStorage.setItem('branchMonkeyFavorites', JSON.stringify(favorites));
  }

  // Check if current repo is a favorite
  $: isFavorite = $repoInfo.path && favorites.includes($repoInfo.path);

  // Load favorites on mount
  loadFavorites();

  // Update input when repoInfo changes
  $: if ($repoInfo.path) {
    inputValue = $repoInfo.path;
  }

  function toggleFavorite() {
    if (!$repoInfo.path) return;

    if (isFavorite) {
      favorites = favorites.filter(f => f !== $repoInfo.path);
      showToast('Removed from favorites', 'info');
    } else {
      favorites = [...favorites, $repoInfo.path];
      showToast('Added to favorites', 'success');
    }
    saveFavorites();
  }

  function removeFavorite(path) {
    favorites = favorites.filter(f => f !== path);
    saveFavorites();
  }

  async function selectFavorite(path) {
    inputValue = path;
    await switchRepo();
  }

  async function handleInput(e) {
    const query = e.target.value;
    inputValue = query;

    clearTimeout(searchTimeout);

    if (!query || query.length < 2) {
      suggestions = [];
      showSuggestions = false;
      return;
    }

    searchTimeout = setTimeout(async () => {
      try {
        suggestions = await searchRepoPaths(query);
        showSuggestions = suggestions.length > 0;
      } catch (error) {
        console.error('Failed to search paths:', error);
        suggestions = [];
        showSuggestions = false;
      }
    }, 300);
  }

  async function selectPath(path) {
    inputValue = path;
    showSuggestions = false;
    suggestions = [];
    await switchRepo();
  }

  async function switchRepo() {
    if (!inputValue.trim()) {
      showToast('Please enter a repository path', 'error');
      return;
    }

    try {
      await setRepoPath(inputValue.trim());
      const info = await fetchRepoInfo();
      repoInfo.set(info);
      showToast('Repository changed successfully', 'success');

      // Trigger page reload to fetch new repo data
      window.location.reload();
    } catch (error) {
      showToast(error.message, 'error');
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') {
      if (showSuggestions && suggestions.length > 0) {
        selectPath(suggestions[0]);
      } else {
        switchRepo();
      }
    } else if (e.key === 'Escape') {
      showSuggestions = false;
    }
  }

  function handleBlur() {
    // Delay to allow click on suggestion
    setTimeout(() => {
      showSuggestions = false;
    }, 200);
  }
</script>

<div class="repo-selector">
  <div class="input-wrapper">
    <button
      on:click={toggleFavorite}
      class="favorite-btn"
      class:is-favorite={isFavorite}
      title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
    >
      ★
    </button>
    <input
      type="text"
      bind:value={inputValue}
      on:input={handleInput}
      on:keydown={handleKeydown}
      on:blur={handleBlur}
      on:focus={() => suggestions.length > 0 && (showSuggestions = true)}
      placeholder="Repository path..."
      class="repo-input"
    />
    <button on:click={switchRepo} class="switch-btn">Switch</button>
  </div>

  {#if showSuggestions && suggestions.length > 0}
    <div class="suggestions">
      {#each suggestions as suggestion}
        <div class="suggestion-item" on:click={() => selectPath(suggestion)}>
          {suggestion}
        </div>
      {/each}
    </div>
  {/if}

  {#if $repoInfo.path}
    <div class="current-repo" title={$repoInfo.path}>
      Current: {$repoInfo.path}
    </div>
  {/if}

  {#if favorites.length > 0}
    <div class="favorites-section">
      <button on:click={() => showFavorites = !showFavorites} class="favorites-toggle">
        {showFavorites ? '▼' : '▶'} Favorites ({favorites.length})
      </button>

      {#if showFavorites}
        <div class="favorites-list">
          {#each favorites as favorite}
            <div class="favorite-item">
              <button
                on:click={() => selectFavorite(favorite)}
                class="favorite-path"
                title={favorite}
              >
                {favorite.split('/').slice(-2).join('/')}
              </button>
              <button
                on:click={() => removeFavorite(favorite)}
                class="remove-favorite"
                title="Remove"
              >
                ×
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .repo-selector {
    position: relative;
    width: 100%;
  }

  .input-wrapper {
    display: flex;
    gap: 8px;
    width: 100%;
  }

  .repo-input {
    flex: 1;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-primary);
    padding: 6px 10px;
    border-radius: 1px;
    font-size: 12px;
    font-family: 'Courier', monospace;
    outline: none;
    transition: border-color 0.15s;
  }

  .repo-input:focus {
    border-color: var(--border-hover);
  }

  .repo-input::placeholder {
    color: var(--text-tertiary);
  }

  .switch-btn {
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    font-size: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .switch-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 80px;
    margin-top: 4px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: var(--shadow-medium);
  }

  .suggestion-item {
    padding: 10px 12px;
    color: var(--text-primary);
    font-size: 12px;
    font-family: 'Courier', monospace;
    cursor: pointer;
    border-bottom: 1px solid var(--border-secondary);
    transition: background 0.15s;
  }

  .suggestion-item:last-child {
    border-bottom: none;
  }

  .suggestion-item:hover {
    background: var(--bg-hover);
  }

  .current-repo {
    margin-top: 6px;
    font-size: 10px;
    color: var(--text-tertiary);
    font-family: 'Courier', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .favorite-btn {
    padding: 6px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-tertiary);
    border-radius: 1px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1;
  }

  .favorite-btn:hover {
    border-color: var(--border-hover);
    color: var(--text-secondary);
  }

  .favorite-btn.is-favorite {
    color: var(--accent-primary);
    border-color: var(--accent-primary);
    background: var(--bg-secondary);
  }

  .favorites-section {
    margin-top: 6px;
  }

  .favorites-toggle {
    width: 100%;
    text-align: left;
    padding: 6px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    font-size: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .favorites-toggle:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .favorites-list {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .favorite-item {
    display: flex;
    gap: 6px;
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 1px;
    padding: 6px;
    transition: background 0.15s;
  }

  .favorite-item:hover {
    background: var(--bg-hover);
  }

  .favorite-path {
    flex: 1;
    text-align: left;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 11px;
    font-family: 'Courier', monospace;
    cursor: pointer;
    padding: 4px 8px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: color 0.15s;
  }

  .favorite-path:hover {
    color: var(--text-secondary);
  }

  .remove-favorite {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 16px;
    cursor: pointer;
    padding: 0 6px;
    transition: all 0.15s;
    line-height: 1;
  }

  .remove-favorite:hover {
    color: var(--text-primary);
  }
</style>
