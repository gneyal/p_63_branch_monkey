<script>
  import { onMount } from 'svelte';
  import { commitTree, isLoading, showToast, showModal, repoInfo, workingTreeStatus } from '../stores/store.js';
  import { theme, toggleTheme } from '../stores/theme.js';
  import { fetchCommitTree, fetchRepoInfo, fetchWorkingTreeStatus } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Modal from './Modal.svelte';
  import CommitTree from './CommitTree.svelte';
  import BuildingsView from './BuildingsView.svelte';
  import RepoSelector from './RepoSelector.svelte';
  import RecentRepos from './RecentRepos.svelte';
  import GlobalActions from './GlobalActions.svelte';
  import BranchesList from './BranchesList.svelte';
  import RemoteStatus from './RemoteStatus.svelte';
  import PromptsLibrary from './PromptsLibrary.svelte';
  import ContextLibrary from './ContextLibrary.svelte';

  let error = null;
  let showBranchesList = false;
  let showRemoteStatus = false;
  let showPromptsLibrary = false;
  let showContextLibrary = false;
  let currentView = 'buildings'; // 'flow' or 'buildings'
  let commitTreeComponent;
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
    // Frame 4: Jumping back
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
    await loadWorkingTreeStatus();
    // Refresh working tree status every 5 seconds (don't reset commit tree)
    const interval = setInterval(() => {
      loadWorkingTreeStatus();
    }, 5000);
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

  async function loadWorkingTreeStatus() {
    try {
      const status = await fetchWorkingTreeStatus();
      workingTreeStatus.set(status);
    } catch (err) {
      console.error('Failed to load working tree status:', err);
    }
  }

  // Derive pagination state from the store
  $: currentOffset = $commitTree?.commits?.length || 0;
  $: hasMore = $commitTree?.has_more || false;
  $: totalCommits = $commitTree?.total || 0;

  async function loadData(append = false) {
    // Prevent concurrent loads
    if ($isLoading) {
      console.log('Already loading, skipping');
      return;
    }

    try {
      isLoading.set(true);
      const existingCommits = $commitTree?.commits || [];
      const offset = append ? existingCommits.length : 0;
      console.log('Loading commits with offset:', offset, 'append:', append);
      const treeData = await fetchCommitTree(50, offset);
      console.log('Loaded commit tree data:', treeData);

      if (append && existingCommits.length > 0) {
        // Append new commits to existing ones
        const newCommits = treeData.commits || [];
        console.log('Appending', newCommits.length, 'commits to existing', existingCommits.length);
        commitTree.set({
          ...treeData,
          commits: [...existingCommits, ...newCommits]
        });
      } else {
        // Replace commits (initial load or refresh)
        commitTree.set(treeData);
      }

      console.log('Pagination state:', {
        loaded: $commitTree?.commits?.length,
        hasMore: treeData.has_more,
        total: treeData.total
      });
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
    if (!hasMore) {
      console.log('No more commits to load');
      return;
    }
    if ($isLoading) {
      console.log('Already loading, skipping loadMore');
      return;
    }
    console.log('loadMore called, currentOffset:', currentOffset);
    await loadData(true);
  }

  function handleNodeClick(node) {
    showToast(`Selected commit: ${node.sha.substring(0, 7)}`, 'info');
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
    showRemoteStatus = true;
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

  function handleShowPrompts() {
    showPromptsLibrary = true;
  }

  function handleShowContext() {
    showContextLibrary = true;
  }
</script>

<main class="app-main">
  <header class="app-header">
    <div class="header-left">
      <div class="title-container">
        <h1
          class="app-title"
          on:mouseenter={startMonkeyAnimation}
          on:mouseleave={stopMonkeyAnimation}
        >
          branch/monkey
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
      <div class="view-toggle">
        <button
          class="view-btn"
          class:active={currentView === 'flow'}
          on:click={() => currentView = 'flow'}
          title="Flow view"
        >
          Flow
        </button>
        <button
          class="view-btn"
          class:active={currentView === 'buildings'}
          on:click={() => currentView = 'buildings'}
          title="Buildings view"
        >
          Buildings
        </button>
      </div>
    </div>
  </header>

  {#if error}
    <div class="error-banner">
      <span>{error}</span>
      <button on:click={loadData} class="retry-btn">Retry</button>
    </div>
  {/if}

  <div class="app-content">
    {#if currentView === 'flow'}
      <CommitTree
        bind:this={commitTreeComponent}
        onNodeClick={handleNodeClick}
        {hasMore}
        {totalCommits}
        loadedCount={currentOffset}
        onLoadMore={loadMore}
      />
    {:else}
      <BuildingsView commits={$commitTree?.commits || []} onNodeClick={handleNodeClick} />
    {/if}
  </div>

  <footer class="app-footer">
    <div class="footer-left">
      <GlobalActions
        onGoToTop={handleGoToTop}
        onGoToBottom={handleGoToBottom}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
        onShowPrompts={handleShowPrompts}
        onShowContext={handleShowContext}
      />
    </div>

    <div class="footer-center">
      <div class="commit-info" class:has-more={hasMore}>
        <span class="commit-count">{currentOffset} / {totalCommits} saves</span>
        {#if hasMore}
          <button class="load-more-compact" on:click={loadMore} title="Show older saves">
            Show More
          </button>
        {/if}
      </div>
    </div>

    <div class="footer-right">
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
  </footer>

  {#if showBranchesList}
    <BranchesList
      onClose={() => showBranchesList = false}
      onBranchClick={handleBranchClick}
    />
  {/if}

  {#if showRemoteStatus}
    <RemoteStatus
      onClose={() => showRemoteStatus = false}
    />
  {/if}

  {#if showPromptsLibrary}
    <PromptsLibrary
      onClose={() => showPromptsLibrary = false}
    />
  {/if}

  {#if showContextLibrary}
    <ContextLibrary
      onClose={() => showContextLibrary = false}
    />
  {/if}

  <Toast />
  <Modal />
</main>

<style>
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
    justify-content: flex-end;
    align-items: center;
  }

  .commit-info {
    display: flex;
    gap: 0;
    align-items: center;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    cursor: default;
  }

  .commit-info.has-more {
    cursor: pointer;
  }

  .commit-info.has-more:hover {
    border-color: var(--border-hover);
  }

  .commit-count {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .view-toggle {
    display: flex;
    gap: 0;
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    overflow: hidden;
  }

  .view-btn {
    padding: 6px 12px;
    background: var(--bg-primary);
    border: none;
    border-right: 1px solid var(--border-primary);
    color: var(--text-secondary);
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-btn:last-child {
    border-right: none;
  }

  .view-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .view-btn.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .load-more-compact {
    padding: 0;
    margin-left: 8px;
    background: transparent;
    border: none;
    color: var(--accent-primary);
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease, color 0.2s ease;
  }

  .commit-info:hover .load-more-compact {
    opacity: 1;
  }

  .load-more-compact:hover {
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
</style>
