<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { commitTree, isLoading, showToast, showModal, repoInfo, workingTreeStatus } from '../stores/store.js';
  import ThemePicker from './ThemePicker.svelte';
  import { fetchCommitTree, fetchRepoInfo, fetchWorkingTreeStatus, fetchRemoteStatus } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Modal from './Modal.svelte';
  import CommitTree from './CommitTree.svelte';
  import BuildingsView from './BuildingsView.svelte';
  import Topbar from './Topbar.svelte';
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
  let remoteStatus = null;
  let groupBy = 'day'; // 'day' or 'week' for buildings view
  let commitTreeComponent;

  onMount(async () => {
    await loadRepoInfo();
    await loadData();
    await loadWorkingTreeStatus();
    await loadRemoteStatus();
    // Refresh working tree status and remote status periodically
    const interval = setInterval(() => {
      loadWorkingTreeStatus();
      loadRemoteStatus();
    }, 10000);
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

  async function loadRemoteStatus() {
    try {
      remoteStatus = await fetchRemoteStatus();
    } catch (err) {
      console.error('Failed to load remote status:', err);
      remoteStatus = null;
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
  <Topbar activeView="commits" />

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
        remoteSha={remoteStatus?.remote_sha}
      />
    {:else}
      <BuildingsView commits={$commitTree?.commits || []} onNodeClick={handleNodeClick} {groupBy} remoteSha={remoteStatus?.remote_sha} />
    {/if}
  </div>

  <footer class="app-footer">
    <div class="footer-left">
      <GlobalActions
        activeView="commits"
        onGoToTop={handleGoToTop}
        onGoToBottom={handleGoToBottom}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
        onShowPrompts={handleShowPrompts}
        onShowContext={handleShowContext}
      />
    </div>

    <div class="footer-center">
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
      <div class="commit-info" class:has-more={hasMore}>
        <span class="commit-count">{currentOffset} / {totalCommits} saves</span>
        {#if hasMore}
          <button class="load-more-compact" on:click={loadMore} title="Show older saves">
            Show More
          </button>
        {/if}
      </div>
      {#if remoteStatus}
        <button class="remote-sync-indicator" on:click={() => showRemoteStatus = true} title="Remote sync status">
          {#if !remoteStatus.has_remote}
            <span class="sync-icon no-remote">○</span>
            <span class="sync-label">No remote</span>
          {:else if remoteStatus.ahead === 0 && remoteStatus.behind === 0}
            <span class="sync-icon synced">✓</span>
            <span class="sync-label">Synced</span>
          {:else}
            {#if remoteStatus.ahead > 0}
              <span class="sync-ahead">↑{remoteStatus.ahead}</span>
            {/if}
            {#if remoteStatus.behind > 0}
              <span class="sync-behind">↓{remoteStatus.behind}</span>
            {/if}
          {/if}
        </button>
      {/if}
    </div>

    <div class="footer-right">
      <ThemePicker compact={true} />
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
    align-items: center;
    gap: 16px;
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

  /* Remote Sync Indicator */
  .remote-sync-indicator {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 10px;
    font-weight: 500;
  }

  .remote-sync-indicator:hover {
    border-color: var(--border-hover);
    background: var(--bg-hover);
  }

  .sync-icon {
    font-size: 12px;
  }

  .sync-icon.synced {
    color: #10b981;
  }

  .sync-icon.no-remote {
    color: var(--text-tertiary);
  }

  .sync-label {
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .sync-ahead {
    color: #10b981;
    font-weight: 600;
  }

  .sync-behind {
    color: #f59e0b;
    font-weight: 600;
  }
</style>
