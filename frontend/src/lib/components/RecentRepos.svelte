<script>
  import { repoInfo, showToast } from '../stores/store.js';
  import { setRepoPath, fetchRepoInfo } from '../services/api.js';

  let showMenu = false;
  let activeTab = 'recent'; // 'recent' or 'favorites'
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

    // Remove if already exists
    recentRepos = recentRepos.filter(r => r !== path);

    // Add to front
    recentRepos.unshift(path);

    // Keep only last 20
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

  async function selectRepo(path) {
    try {
      await setRepoPath(path);
      const info = await fetchRepoInfo();
      repoInfo.set(info);
      saveRecentRepo(path);
      showMenu = false;
      showToast('Repository changed', 'success');
      window.location.reload();
    } catch (error) {
      showToast(error.message, 'error');
    }
  }

  $: isFavorite = $repoInfo.path && favorites.includes($repoInfo.path);

  // Load on mount
  loadData();

  // Save current repo when it changes
  $: if ($repoInfo.path) {
    saveRecentRepo($repoInfo.path);
  }
</script>

<div class="recent-repos">
  <button
    class="menu-trigger"
    class:active={showMenu}
    on:click={() => showMenu = !showMenu}
    title="Recent repositories"
  >
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  </button>

  {#if showMenu}
    <div class="menu-dropdown">
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
  .recent-repos {
    position: relative;
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .menu-trigger, .favorite-toggle {
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
  }

  .menu-trigger:hover, .favorite-toggle:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .menu-trigger:active, .favorite-toggle:active {
    transform: translateY(1px);
  }

  .menu-trigger.active {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .favorite-toggle {
    font-size: 16px;
    line-height: 1;
  }

  .favorite-toggle.is-favorite {
    color: var(--accent-primary);
    border-color: var(--accent-primary);
  }

  .menu-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    width: 320px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    box-shadow: var(--shadow-large);
    z-index: 1000;
    overflow: hidden;
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
    max-height: 400px;
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
