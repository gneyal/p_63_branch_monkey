<script>
  import { onMount } from 'svelte';
  import { commitTree, isLoading, showToast, repoInfo } from './lib/stores/store.js';
  import { fetchCommitTree, fetchRepoInfo } from './lib/services/api.js';
  import Toast from './lib/components/Toast.svelte';
  import Modal from './lib/components/Modal.svelte';
  import CommitTree from './lib/components/CommitTree.svelte';
  import RepoSelector from './lib/components/RepoSelector.svelte';
  import LandingPage from './lib/components/LandingPage.svelte';

  let error = null;
  let showLanding = localStorage.getItem('showLanding') !== 'false';

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

  function handleGetStarted() {
    showLanding = false;
    localStorage.setItem('showLanding', 'false');
  }
</script>

{#if showLanding}
  <LandingPage onGetStarted={handleGetStarted} />
{:else}
<main class="h-screen w-screen flex flex-col overflow-hidden">
  <header class="flex items-center gap-3 px-4 py-2 bg-zinc-900 border-b border-zinc-800">
    <h1 class="text-base font-semibold text-white whitespace-nowrap">Branch Monkey</h1>
    <div class="flex-1 max-w-3xl">
      <RepoSelector />
    </div>
  </header>

  {#if error}
    <div class="flex justify-between items-center px-4 py-3 bg-red-900/40 text-red-400 border border-red-900/60">
      <span>⚠️ {error}</span>
      <button on:click={loadData} class="px-3 py-1.5 bg-red-900/50 text-red-400 rounded hover:bg-red-900/70 text-xs font-medium transition">Retry</button>
    </div>
  {/if}

  <div class="flex-1 min-h-0 w-full overflow-hidden">
    <CommitTree onNodeClick={handleNodeClick} />
  </div>

  <Toast />
  <Modal />
</main>
{/if}

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
    padding: 8px 16px;
    background: #1a1a1a;
    border-bottom: 1px solid #333;
  }

  .app-title {
    margin: 0 0 8px 0;
    font-size: 18px;
    font-weight: 600;
    color: #fff;
  }

  .repo-selector-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 16px;
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
