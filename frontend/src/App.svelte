<script>
  import { onMount } from 'svelte';
  import { commitTree, isLoading, showToast, repoInfo } from './lib/stores/store.js';
  import { fetchCommitTree, fetchRepoInfo } from './lib/services/api.js';
  import Toast from './lib/components/Toast.svelte';
  import Modal from './lib/components/Modal.svelte';
  import CommitTree from './lib/components/CommitTree.svelte';
  import RepoSelector from './lib/components/RepoSelector.svelte';

  let error = null;

  onMount(async () => {
    await loadRepoInfo();
    await loadData();
    // Refresh data every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  });

  async function loadRepoInfo() {
    try {
      const info = await fetchRepoInfo();
      repoInfo.set(info);
    } catch (err) {
      console.error('Failed to load repo info:', err);
    }
  }

  async function loadData() {
    try {
      isLoading.set(true);
      const treeData = await fetchCommitTree();
      console.log('Loaded commit tree data:', treeData);
      commitTree.set(treeData);
      error = null;
    } catch (err) {
      console.error('Failed to load data:', err);
      error = err.message;
      showToast(`Failed to load data: ${err.message}`, 'error');
    } finally {
      isLoading.set(false);
    }
  }

  function handleNodeClick(node) {
    showToast(`Selected commit: ${node.sha.substring(0, 7)}`, 'info');
  }
</script>

<main class="app">
  <header class="app-header">
    <h1 class="app-title">Branch Monkey</h1>
    <div class="repo-selector-container">
      <RepoSelector />
    </div>
  </header>

  {#if error}
    <div class="error-banner">
      <span>⚠️ {error}</span>
      <button on:click={loadData} class="retry-btn">Retry</button>
    </div>
  {/if}

  <div class="app-content">
    <div class="panel tree-panel">
      <CommitTree onNodeClick={handleNodeClick} />
    </div>
  </div>

  <Toast />
  <Modal />
</main>

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: #121212;
    color: #e0e0e0;
  }

  :global(*) {
    box-sizing: border-box;
  }

  .app {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    padding: 0;
    gap: 0;
    overflow: hidden;
  }

  .app-header {
    text-align: center;
    padding: 12px 20px;
    background: #1a1a1a;
    border-bottom: 1px solid #333;
  }

  .app-title {
    margin: 0 0 12px 0;
    font-size: 24px;
    font-weight: 700;
    color: #fff;
  }

  .repo-selector-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 20px;
  }

  .error-banner {
    background: #5c2828;
    color: #ff6b6b;
    padding: 12px 16px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #752e2e;
  }

  .retry-btn {
    background: #752e2e;
    color: #ff6b6b;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: background 0.2s;
  }

  .retry-btn:hover {
    background: #8a3434;
  }

  .app-content {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 0;
    width: 100%;
    overflow: hidden;
  }

  .panel {
    flex: 1;
    min-height: 0;
    width: 100%;
  }

  @media (max-width: 768px) {
    .app-title {
      font-size: 28px;
    }

    .app-subtitle {
      font-size: 14px;
    }

    .app-header {
      padding: 16px;
    }
  }
</style>
