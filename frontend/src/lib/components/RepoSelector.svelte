<script>
  import { repoInfo, showToast } from '../stores/store.js';
  import { searchRepoPaths, setRepoPath, fetchRepoInfo } from '../services/api.js';

  let inputValue = '';
  let fullPath = ''; // Store the full path separately
  let isEditing = false; // Track if user is typing a new path
  let suggestions = [];
  let showSuggestions = false;
  let searchTimeout = null;
  let favorites = [];
  let showFavorites = false;
  let isFocused = false;

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
    fullPath = path;
    isEditing = true;
    await switchRepo();
  }

  async function handleInput(e) {
    const query = e.target.value;
    inputValue = query;
    isEditing = true; // User is now typing a new path

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
    isEditing = true; // Mark as editing since we're setting a full path
    fullPath = path; // Store the full path
    showSuggestions = false;
    suggestions = [];
    await switchRepo();
  }

  async function switchRepo() {
    // Use the full path if not editing (clicking switch on current repo name)
    // Otherwise use the inputValue (user typed a new path)
    const pathToSwitch = isEditing ? inputValue.trim() : fullPath;

    if (!pathToSwitch) {
      showToast('Please enter a repository path', 'error');
      return;
    }

    try {
      await setRepoPath(pathToSwitch);
      const info = await fetchRepoInfo();
      repoInfo.set(info);
      showToast('Repository changed successfully', 'success');
      isEditing = false; // Reset editing state

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

  function handleFocus() {
    isFocused = true;
    if (suggestions.length > 0) {
      showSuggestions = true;
    }
  }

  function handleBlur() {
    // Delay to allow click on suggestion or switch button
    setTimeout(() => {
      isFocused = false;
      showSuggestions = false;
      // Reset to project name if user didn't change anything meaningful
      if (isEditing && inputValue === getProjectName(fullPath)) {
        isEditing = false;
      }
    }, 200);
  }
</script>

<div class="repo-selector">
  <div class="input-wrapper">
    <input
      type="text"
      bind:value={inputValue}
      on:input={handleInput}
      on:keydown={handleKeydown}
      on:blur={handleBlur}
      on:focus={handleFocus}
      placeholder="Repository path..."
      class="repo-input"
    />
    {#if isFocused}
      <button on:click={switchRepo} class="switch-btn">Switch</button>
    {/if}
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
    font-size: 11px;
    font-family: 'Courier', monospace;
    outline: none;
    transition: all 0.2s ease;
  }

  .repo-input:focus {
    border-color: var(--border-hover);
    background: var(--bg-hover);
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

  .switch-btn:active {
    transform: translateY(1px);
  }

  .suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 80px;
    margin-top: 6px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    max-height: 300px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: var(--shadow-large);
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
    color: var(--text-primary);
  }
</style>
