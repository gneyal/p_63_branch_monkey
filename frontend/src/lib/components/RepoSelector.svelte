<script>
  import { repoInfo, showToast } from '../stores/store.js';
  import { searchRepoPaths, setRepoPath, fetchRepoInfo } from '../services/api.js';

  let inputValue = '';
  let fullPath = ''; // Store the full path separately
  let isEditing = false; // Track if user is typing a new path
  let suggestions = [];
  let showSuggestions = false;
  let searchTimeout = null;
  let isFocused = false;

  // Recent/Favorites state
  let showRepoMenu = false;
  let activeTab = 'recent';
  let recentRepos = [];
  let favorites = [];

  // Load data from localStorage
  function loadData() {
    const storedRecent = localStorage.getItem('branchMonkeyRecent');
    recentRepos = storedRecent ? JSON.parse(storedRecent) : [];

    const storedFavorites = localStorage.getItem('branchMonkeyFavorites');
    favorites = storedFavorites ? JSON.parse(storedFavorites) : [];
  }

  // Save recent repo (max 20)
  function saveRecentRepo(path) {
    if (!path) return;
    recentRepos = recentRepos.filter(r => r !== path);
    recentRepos.unshift(path);
    recentRepos = recentRepos.slice(0, 20);
    localStorage.setItem('branchMonkeyRecent', JSON.stringify(recentRepos));
  }

  // Toggle favorite
  function toggleFavorite(path) {
    if (favorites.includes(path)) {
      favorites = favorites.filter(f => f !== path);
      showToast('Removed from favorites', 'info');
    } else {
      favorites = [...favorites, path];
      showToast('Added to favorites', 'success');
    }
    localStorage.setItem('branchMonkeyFavorites', JSON.stringify(favorites));
  }

  // Check if current repo is a favorite
  $: isFavorite = $repoInfo.path && favorites.includes($repoInfo.path);

  // Load on mount
  loadData();

  // Save current repo when it changes
  $: if ($repoInfo.path) {
    saveRecentRepo($repoInfo.path);
  }

  // Extract project name from full path
  function getProjectName(path) {
    if (!path) return '';
    const parts = path.split('/');
    return parts[parts.length - 1] || path;
  }

  // Update input when repoInfo changes - show only project name
  $: if ($repoInfo.path && !isEditing) {
    fullPath = $repoInfo.path;
    inputValue = getProjectName($repoInfo.path);
  }

  async function selectRepo(path) {
    try {
      await setRepoPath(path);
      const info = await fetchRepoInfo();
      repoInfo.set(info);
      saveRecentRepo(path);
      showRepoMenu = false;
      showSuggestions = false;
      showToast('Repository changed', 'success');
      window.location.reload();
    } catch (error) {
      showToast(error.message, 'error');
    }
  }

  async function handleInput(e) {
    const query = e.target.value;
    inputValue = query;
    isEditing = true;
    showRepoMenu = false; // Hide recent/favorites when typing

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
    isEditing = true;
    fullPath = path;
    showSuggestions = false;
    suggestions = [];
    await selectRepo(path);
  }

  async function switchRepo() {
    const pathToSwitch = isEditing ? inputValue.trim() : fullPath;

    if (!pathToSwitch) {
      showToast('Please enter a repository path', 'error');
      return;
    }

    await selectRepo(pathToSwitch);
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
      showRepoMenu = false;
    }
  }

  function handleFocus() {
    isFocused = true;
    // Show recent/favorites on focus if not editing
    if (!isEditing && !inputValue.includes('/')) {
      showRepoMenu = true;
      showSuggestions = false;
    } else if (suggestions.length > 0) {
      showSuggestions = true;
    }
  }

  function handleBlur() {
    setTimeout(() => {
      isFocused = false;
      showSuggestions = false;
      showRepoMenu = false;
      if (isEditing && inputValue === getProjectName(fullPath)) {
        isEditing = false;
      }
    }, 200);
  }

  function toggleRepoMenu() {
    showRepoMenu = !showRepoMenu;
    showSuggestions = false;
  }

  function handleClickOutside(e) {
    if (!e.target.closest('.repo-selector')) {
      showRepoMenu = false;
      showSuggestions = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} />

<div class="repo-selector">
  <button class="home-btn" on:click|stopPropagation={toggleRepoMenu} title="Recent repositories">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  </button>

  <div class="input-wrapper">
    <input
      type="text"
      bind:value={inputValue}
      on:input={handleInput}
      on:keydown={handleKeydown}
      on:blur={handleBlur}
      on:focus={handleFocus}
      on:click|stopPropagation={() => { if (!isEditing) showRepoMenu = true; }}
      placeholder="Repository path..."
      class="repo-input"
    />
    {#if isFocused}
      <button on:click={switchRepo} class="switch-btn">Switch</button>
    {/if}
  </div>

  {#if showSuggestions && suggestions.length > 0}
    <div class="dropdown suggestions-dropdown">
      {#each suggestions as suggestion}
        <div class="suggestion-item" on:click|stopPropagation={() => selectPath(suggestion)}>
          {suggestion}
        </div>
      {/each}
    </div>
  {/if}

  {#if showRepoMenu}
    <div class="dropdown repo-menu-dropdown" on:click|stopPropagation>
      <div class="menu-tabs">
        <button
          class="menu-tab"
          class:active={activeTab === 'recent'}
          on:click={() => activeTab = 'recent'}
        >
          Recent
        </button>
        <button
          class="menu-tab"
          class:active={activeTab === 'favorites'}
          on:click={() => activeTab = 'favorites'}
        >
          Favorites
        </button>
      </div>

      <div class="menu-content">
        {#if activeTab === 'recent'}
          {#if recentRepos.length === 0}
            <div class="empty-state">No recent repositories</div>
          {:else}
            {#each recentRepos as repo}
              <div class="repo-item">
                <button class="repo-path" on:click={() => selectRepo(repo)} title={repo}>
                  {repo.split('/').slice(-2).join('/')}
                </button>
                <button
                  class="star-btn"
                  class:starred={favorites.includes(repo)}
                  on:click|stopPropagation={() => toggleFavorite(repo)}
                  title={favorites.includes(repo) ? 'Remove from favorites' : 'Add to favorites'}
                >
                  ★
                </button>
              </div>
            {/each}
          {/if}
        {:else}
          {#if favorites.length === 0}
            <div class="empty-state">No favorite repositories</div>
          {:else}
            {#each favorites as repo}
              <div class="repo-item">
                <button class="repo-path" on:click={() => selectRepo(repo)} title={repo}>
                  {repo.split('/').slice(-2).join('/')}
                </button>
                <button
                  class="remove-btn"
                  on:click|stopPropagation={() => toggleFavorite(repo)}
                  title="Remove from favorites"
                >
                  ×
                </button>
              </div>
            {/each}
          {/if}
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .repo-selector {
    position: relative;
    width: 100%;
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .home-btn {
    padding: 6px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .home-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .input-wrapper {
    display: flex;
    gap: 8px;
    flex: 1;
  }

  .repo-input {
    flex: 1;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-primary);
    padding: 6px 10px;
    border-radius: 1px;
    font-size: 11px;
    font-family: 'Courier', monospace;
    outline: none;
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .repo-input:focus {
    border-color: var(--border-hover);
    background: var(--bg-hover);
    cursor: text;
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
    font-size: 9px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .switch-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 6px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    max-height: 400px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: var(--shadow-large);
  }

  .suggestions-dropdown {
    left: 30px;
  }

  .suggestion-item {
    padding: 10px 12px;
    color: var(--text-primary);
    font-size: 11px;
    font-family: 'Courier', monospace;
    cursor: pointer;
    border-bottom: 1px solid var(--border-secondary);
    transition: all 0.2s ease;
  }

  .suggestion-item:last-child {
    border-bottom: none;
  }

  .suggestion-item:hover {
    background: var(--bg-secondary);
  }

  .menu-tabs {
    display: flex;
    border-bottom: 1px solid var(--border-secondary);
  }

  .menu-tab {
    flex: 1;
    padding: 10px;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .menu-tab:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .menu-tab.active {
    color: var(--text-primary);
    border-bottom-color: var(--text-primary);
  }

  .menu-content {
    max-height: 350px;
    overflow-y: auto;
  }

  .empty-state {
    padding: 32px;
    text-align: center;
    color: var(--text-tertiary);
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .repo-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-secondary);
    transition: all 0.2s ease;
  }

  .repo-item:last-child {
    border-bottom: none;
  }

  .repo-item:hover {
    background: var(--bg-secondary);
  }

  .repo-path {
    flex: 1;
    text-align: left;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 11px;
    font-family: 'Courier', monospace;
    cursor: pointer;
    padding: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: color 0.2s ease;
  }

  .repo-path:hover {
    color: var(--text-primary);
  }

  .star-btn, .remove-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 18px;
    cursor: pointer;
    padding: 4px;
    line-height: 1;
    transition: color 0.15s;
  }

  .star-btn:hover {
    color: var(--accent-primary);
  }

  .star-btn.starred {
    color: var(--accent-primary);
  }

  .remove-btn:hover {
    color: var(--text-primary);
  }
</style>
