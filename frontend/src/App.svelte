<script>
  import { onMount } from 'svelte';
  import { commitTree, isLoading, showToast, showModal, repoInfo } from './lib/stores/store.js';
  import { theme, toggleTheme } from './lib/stores/theme.js';
  import { fetchCommitTree, fetchRepoInfo, createBranch } from './lib/services/api.js';
  import Toast from './lib/components/Toast.svelte';
  import Modal from './lib/components/Modal.svelte';
  import CommitTree from './lib/components/CommitTree.svelte';
  import RepoSelector from './lib/components/RepoSelector.svelte';
  import RecentRepos from './lib/components/RecentRepos.svelte';
  import GlobalActions from './lib/components/GlobalActions.svelte';
  import LandingPage from './lib/components/LandingPage.svelte';
  import BranchesList from './lib/components/BranchesList.svelte';

  let error = null;
  let showLanding = localStorage.getItem('showLanding') !== 'false';
  let showBranchesList = false;
  let commitTreeComponent;
  let currentOffset = 0;
  let hasMore = false;
  let totalCommits = 0;
  let showMonkey = false;
  let monkeyFrame = 0;

  const monkeyFrames = [
    // Frame 1: Monkey on left branch
    `        ___
       {. .}
        >o<
       /|||\\
      // \\\\\\\\
=========
     ||
     ||`,
    // Frame 2: Monkey jumping
    `
      {. .}
       >o<
      /|||\\
     // \\\\\\\\

=========
     ||
     ||`,
    // Frame 3: Monkey on right branch
    `
       {. .}
        >o<
       /|||\\
      // \\\\\\\\
         =========
              ||
              ||`,
    // Frame 4: Monkey jumping back
    `
      {. .}
       >o<
      /|||\\
     // \\\\\\\\

=========
     ||
     ||`,
  ];

  let animationInterval;

  function startMonkeyAnimation() {
    showMonkey = true;
    monkeyFrame = 0;
    animationInterval = setInterval(() => {
      monkeyFrame = (monkeyFrame + 1) % monkeyFrames.length;
    }, 600);
  }

  function stopMonkeyAnimation() {
    showMonkey = false;
    if (animationInterval) {
      clearInterval(animationInterval);
    }
  }

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

  async function loadData(append = false) {
    try {
      isLoading.set(true);
      const offset = append ? currentOffset : 0;
      const treeData = await fetchCommitTree(50, offset);
      console.log('Loaded commit tree data:', treeData);

      if (append) {
        // Append new commits to existing ones
        commitTree.update(current => ({
          ...treeData,
          commits: [...(current?.commits || []), ...(treeData.commits || [])]
        }));
      } else {
        // Replace commits (initial load or refresh)
        commitTree.set(treeData);
      }

      currentOffset = treeData.offset + treeData.commits.length;
      hasMore = treeData.has_more;
      totalCommits = treeData.total;
      console.log('Pagination state:', { currentOffset, hasMore, totalCommits, loaded: treeData.commits.length });
      error = null;
    } catch (err) {
      console.error('Failed to load data:', err);
      error = err.message;
      showToast(`Failed to load data: ${err.message}`, 'error');
    } finally {
      isLoading.set(false);
    }
  }

  async function loadMore() {
    if (!hasMore || $isLoading) return;
    await loadData(true);
  }

  function handleNodeClick(node) {
    showToast(`Selected commit: ${node.sha.substring(0, 7)}`, 'info');
  }

  function handleGetStarted() {
    showLanding = false;
    localStorage.setItem('showLanding', 'false');
  }

  function handleGoToTop() {
    if (commitTreeComponent && commitTreeComponent.goToTop) {
      commitTreeComponent.goToTop();
    }
  }

  function handleGoToBottom() {
    if (commitTreeComponent && commitTreeComponent.goToBottom) {
      commitTreeComponent.goToBottom();
    }
  }

  function handleShowRemote() {
    // To be implemented
  }

  function handleNameBranches() {
    showBranchesList = true;
  }

  function handleBranchClick(branch) {
    if (commitTreeComponent?.goToCommit) {
      const success = commitTreeComponent.goToCommit(branch.sha);
      if (success) {
        showToast(`Jumped to branch: ${branch.name}`, 'success');
      } else {
        showToast(`Could not find commit ${branch.sha}`, 'error');
      }
    }
  }
</script>

{#if showLanding}
  <LandingPage onGetStarted={handleGetStarted} />
{:else}
<main class="app-main">
  <header class="app-header">
    <div class="header-left">
      <div class="title-container">
        <h1
          class="app-title"
          on:mouseenter={startMonkeyAnimation}
          on:mouseleave={stopMonkeyAnimation}
        >
          branch_monkey
        </h1>
        {#if showMonkey}
          <div class="ascii-monkey">
            <pre>{monkeyFrames[monkeyFrame]}</pre>
          </div>
        {/if}
      </div>
      <RecentRepos />
    </div>

    <div class="header-center">
      <RepoSelector />
    </div>

    <div class="header-right">
      <div class="commit-info">
        <span class="commit-count">{currentOffset} / {totalCommits} commits</span>
        {#if hasMore}
          <button class="load-more-compact" on:click={loadMore} title="Load more commits">
            Load More
          </button>
        {/if}
      </div>

      <GlobalActions
        onGoToTop={handleGoToTop}
        onGoToBottom={handleGoToBottom}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
      />

      <button class="theme-toggle" on:click={toggleTheme} title="Toggle theme">
        {#if $theme === 'light'}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
        {:else}
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        {/if}
      </button>
    </div>
  </header>

  {#if error}
    <div class="error-banner">
      <span>{error}</span>
      <button on:click={loadData} class="retry-btn">Retry</button>
    </div>
  {/if}

  <div class="app-content">
    <CommitTree
      bind:this={commitTreeComponent}
      onNodeClick={handleNodeClick}
      {hasMore}
      {totalCommits}
      loadedCount={currentOffset}
      onLoadMore={loadMore}
    />
  </div>

  {#if showBranchesList}
    <BranchesList
      onClose={() => showBranchesList = false}
      onBranchClick={handleBranchClick}
    />
  {/if}

  <Toast />
  <Modal />
</main>
{/if}

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :global(:root[data-theme="light"]) {
    --bg-primary: #fafaf8;
    --bg-secondary: #f0f0ed;
    --bg-hover: #e8e8e3;
    --text-primary: #1a1a1a;
    --text-secondary: #4a4a4a;
    --text-tertiary: #7a7a7a;
    --border-primary: #d0d0c8;
    --border-secondary: #e0e0d8;
    --border-hover: #a0a098;
    --accent-primary: #4a4a4a;
    --accent-secondary: #7a7a7a;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.1);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.15);

    /* Branch colors - light mode - muted */
    --branch-main: #4a7dc9;
    --branch-experiment: #3a9679;
    --branch-feature: #8e6cbd;
    --branch-fix: #c84a4a;
    --branch-default: #7a8290;
  }

  :global(:root[data-theme="dark"]) {
    --bg-primary: #1a1a1a;
    --bg-secondary: #121212;
    --bg-hover: #262626;
    --text-primary: #e5e5e5;
    --text-secondary: #a3a3a3;
    --text-tertiary: #737373;
    --border-primary: #404040;
    --border-secondary: #2d2d2d;
    --border-hover: #525252;
    --accent-primary: #e5e5e5;
    --accent-secondary: #a3a3a3;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.4);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.5);

    /* Branch colors - dark mode */
    --branch-main: #3b82f6;
    --branch-experiment: #10b981;
    --branch-feature: #8b5cf6;
    --branch-fix: #ef4444;
    --branch-default: #9ca3af;
  }

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  :global(*) {
    box-sizing: border-box;
  }

  .app-main {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .app-header {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: 24px;
    align-items: center;
    padding: 12px 24px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
    box-shadow: var(--shadow-small);
  }

  @media (max-width: 1200px) {
    .app-header {
      grid-template-columns: auto 1fr auto;
      gap: 16px;
      padding: 12px 16px;
    }

    .app-title {
      font-size: 10px;
    }
  }

  @media (max-width: 768px) {
    .app-header {
      grid-template-columns: 1fr;
      gap: 12px;
      padding: 12px 16px;
    }

    .header-left,
    .header-center,
    .header-right {
      justify-content: center;
    }

    .header-left {
      order: 1;
    }

    .header-center {
      order: 2;
    }

    .header-right {
      order: 3;
      flex-wrap: wrap;
    }
  }

  .header-left {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .title-container {
    position: relative;
  }

  .app-title {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 1.5px;
    white-space: nowrap;
    margin: 0;
    font-family: 'Courier New', 'Courier', 'Monaco', 'Menlo', monospace;
    cursor: pointer;
  }

  .ascii-monkey {
    position: absolute;
    top: calc(100% + 8px);
    left: 0;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    padding: 16px;
    box-shadow: var(--shadow-large);
    z-index: 1000;
    animation: monkeySlideIn 0.2s ease;
    min-width: 220px;
  }

  @keyframes monkeySlideIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .ascii-monkey pre {
    margin: 0;
    font-family: 'Courier New', 'Courier', 'Monaco', 'Menlo', monospace;
    font-size: 11px;
    line-height: 1.3;
    color: var(--text-primary);
    white-space: pre;
  }

  .header-center {
    display: flex;
    justify-content: center;
  }

  .header-right {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    align-items: center;
  }

  .commit-info {
    display: flex;
    gap: 8px;
    align-items: center;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
  }

  .commit-count {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .load-more-compact {
    padding: 5px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 1px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .load-more-compact:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .load-more-compact:active {
    transform: translateY(1px);
  }

  .theme-toggle {
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

  .theme-toggle:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .theme-toggle:active {
    transform: translateY(1px);
  }

  .error-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 32px;
    background: #fef2f2;
    color: #991b1b;
    border-bottom: 1px solid #fecaca;
    font-size: 13px;
  }

  :global([data-theme="dark"]) .error-banner {
    background: #3f1f1f;
    color: #fca5a5;
    border-bottom-color: #7f1d1d;
  }

  .retry-btn {
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    border-radius: 2px;
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .retry-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .app-content {
    flex: 1;
    min-height: 0;
    overflow: hidden;
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
