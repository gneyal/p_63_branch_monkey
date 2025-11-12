<script>
  import { repoInfo, showToast } from '../stores/store.js';
  import { searchRepoPaths, setRepoPath, fetchRepoInfo } from '../services/api.js';

  let inputValue = '';
  let suggestions = [];
  let showSuggestions = false;
  let searchTimeout = null;

  // Update input when repoInfo changes
  $: if ($repoInfo.path) {
    inputValue = $repoInfo.path;
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
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
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
    padding: 8px 20px;
    background: #7c3aed;
    border: none;
    color: white;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .switch-btn:hover {
    background: #6d28d9;
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
    margin-top: 8px;
    font-size: 12px;
    color: #808080;
    font-family: 'Monaco', 'Courier New', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
