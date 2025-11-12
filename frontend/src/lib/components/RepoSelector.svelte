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
    background: #2d2d2d;
    border: 1px solid #444;
    color: #e0e0e0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-family: 'Monaco', 'Courier New', monospace;
    outline: none;
    transition: border-color 0.2s;
  }

  .repo-input:focus {
    border-color: #2196f3;
  }

  .repo-input::placeholder {
    color: #808080;
  }

  .switch-btn {
    padding: 4px 10px;
    background: #444;
    border: 1px solid #555;
    color: #e0e0e0;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .switch-btn:hover {
    background: #555;
    border-color: #666;
  }

  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 80px;
    margin-top: 4px;
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 6px;
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
  }

  .suggestion-item {
    padding: 10px 12px;
    color: #e0e0e0;
    font-size: 13px;
    font-family: 'Monaco', 'Courier New', monospace;
    cursor: pointer;
    border-bottom: 1px solid #444;
    transition: background 0.15s;
  }

  .suggestion-item:last-child {
    border-bottom: none;
  }

  .suggestion-item:hover {
    background: #3d3d3d;
  }

  .current-repo {
    margin-top: 4px;
    font-size: 10px;
    color: #808080;
    font-family: 'Monaco', 'Courier New', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .favorite-btn {
    padding: 4px 8px;
    background: #2d2d2d;
    border: 1px solid #444;
    color: #808080;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s;
    line-height: 1;
  }

  .favorite-btn:hover {
    border-color: #f59e0b;
    color: #f59e0b;
  }

  .favorite-btn.is-favorite {
    color: #f59e0b;
    border-color: #f59e0b;
    background: rgba(245, 158, 11, 0.1);
  }

  .favorites-section {
    margin-top: 6px;
  }

  .favorites-toggle {
    width: 100%;
    text-align: left;
    padding: 4px 8px;
    background: #2d2d2d;
    border: 1px solid #444;
    color: #e0e0e0;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .favorites-toggle:hover {
    background: #3d3d3d;
    border-color: #555;
  }

  .favorites-list {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .favorite-item {
    display: flex;
    gap: 6px;
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 6px;
    transition: background 0.2s;
  }

  .favorite-item:hover {
    background: #3d3d3d;
  }

  .favorite-path {
    flex: 1;
    text-align: left;
    background: transparent;
    border: none;
    color: #e0e0e0;
    font-size: 12px;
    font-family: 'Monaco', 'Courier New', monospace;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: color 0.2s;
  }

  .favorite-path:hover {
    color: #2196f3;
  }

  .remove-favorite {
    background: transparent;
    border: none;
    color: #808080;
    font-size: 20px;
    cursor: pointer;
    padding: 0 8px;
    border-radius: 4px;
    transition: all 0.2s;
    line-height: 1;
  }

  .remove-favorite:hover {
    background: #752e2e;
    color: #ff6b6b;
  }
</style>
