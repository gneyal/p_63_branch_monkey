<script>
  import { commitTree, workingTreeStatus } from '../stores/store.js';
  import { writable } from 'svelte/store';
  import { onMount } from 'svelte';
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    MiniMap
  } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import CommitNode from './CommitNode.svelte';
  import WorkingTreeNode from './WorkingTreeNode.svelte';
  import FlowController from './FlowController.svelte';

  export let onNodeClick = null;
  export let hasMore = false;
  export let totalCommits = 0;
  export let loadedCount = 0;
  export let onLoadMore = null;
  export let remoteSha = null;

  // Calculate which commits are ahead of remote
  $: aheadShas = calculateAheadShas($commitTree?.commits, remoteSha);

  function calculateAheadShas(commits, remoteSha) {
    if (!remoteSha || !commits || commits.length === 0) return new Set();

    // Check if remote commit exists in the loaded commits
    const remoteIndex = commits.findIndex(c => c.sha === remoteSha);
    if (remoteIndex === -1) return new Set(); // Remote not in loaded commits

    // Only commits BEFORE the remote are ahead
    const ahead = new Set();
    for (let i = 0; i < remoteIndex; i++) {
      ahead.add(commits[i].sha);
    }
    return ahead;
  }

  let selectedCommit = null;
  let currentCommitIndex = 0;
  let svelteFlowComponent = null;
  let commandQueue = [];

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    commit: CommitNode,
    workingTree: WorkingTreeNode
  };

  // Center viewport on a specific commit by index
  function centerOnCommit(index) {
    if ($nodes.length === 0 || index < 0 || index >= $nodes.length) return;

    const node = $nodes[index];
    currentCommitIndex = index;

    // Send command to FlowController to fit to this node
    commandQueue = [...commandQueue, {
      type: 'fitToNode',
      nodeId: node.id
    }];
  }

  // Export function to go to top
  export function goToTop() {
    centerOnCommit(0);
  }

  // Export function to go to bottom
  export function goToBottom() {
    if ($nodes.length === 0) return;
    centerOnCommit($nodes.length - 1);
  }

  // Export function to get current commit
  export function getCurrentCommit() {
    if ($nodes.length === 0 || currentCommitIndex < 0 || currentCommitIndex >= $commitTree.commits.length) {
      return null;
    }
    return $commitTree.commits[currentCommitIndex];
  }

  // Export function to navigate to a commit by SHA
  export function goToCommit(sha) {
    if (!$commitTree?.commits) return false;

    const index = $commitTree.commits.findIndex(c => c.sha.startsWith(sha) || sha.startsWith(c.sha));
    if (index === -1) return false;

    centerOnCommit(index);
    return true;
  }

  // Handle keyboard navigation
  function handleKeydown(event) {
    if (!$nodes.length) return;

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      // Move up (to newer commits)
      const nextIndex = Math.max(0, currentCommitIndex - 1);
      centerOnCommit(nextIndex);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      // Move down (to older commits)
      const prevIndex = Math.min($nodes.length - 1, currentCommitIndex + 1);
      centerOnCommit(prevIndex);
    }
  }

  // Set up keyboard listener
  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    return () => {
      window.removeEventListener('keydown', handleKeydown);
    };
  });

  // Transform commits to nodes and edges for Svelte Flow
  $: if ($commitTree && $commitTree.commits && $commitTree.commits.length > 0) {
    const commits = $commitTree.commits;
    const newNodes = [];
    const newEdges = [];

    // Create a map for quick lookup
    const commitMap = new Map(commits.map(c => [c.sha, c]));

    // Check if we should show working tree node (uncommitted changes)
    const showWorkingTreeNode = $workingTreeStatus && !$workingTreeStatus.clean;

    // Assign lanes to commits (vertical lines for each branch)
    const commitLanes = new Map(); // sha -> lane number
    const branchLanes = new Map(); // branch name -> lane number

    // Main branch always gets lane 0 (center)
    branchLanes.set('main', 0);
    branchLanes.set('master', 0);
    let nextLane = 1;

    // Process commits to assign lanes
    // Commits come newest to oldest, so we need to track lanes as we go
    commits.forEach((commit, index) => {
      let lane = null;

      // If this commit has a branch label (it's a branch tip)
      if (commit.branches && commit.branches.length > 0) {
        const branchName = commit.branches[0];

        // Check if this branch already has a lane assigned
        if (branchLanes.has(branchName)) {
          lane = branchLanes.get(branchName);
        } else {
          // New branch - assign it to the right of main
          lane = nextLane++;
          branchLanes.set(branchName, lane);
        }
      } else {
        // No branch label - inherit lane from children (commits that point to this as parent)
        // Look ahead to find which commit has this as a parent
        for (let i = 0; i < index; i++) {
          const child = commits[i];
          if (child.parents && child.parents.includes(commit.sha)) {
            if (commitLanes.has(child.sha)) {
              lane = commitLanes.get(child.sha);
              break;
            }
          }
        }

        // If still no lane, default to main lane
        if (lane === null) {
          lane = 0;
        }
      }

      commitLanes.set(commit.sha, lane);
    });

    // Layout settings - equal spacing for 45-degree diagonal edges
    const spacing = 300;
    const laneSpacing = spacing;
    const commitSpacing = spacing;

    // Calculate centering offset
    const maxLane = Math.max(...commitLanes.values());
    const totalWidth = maxLane * laneSpacing;
    const startX = -totalWidth / 2;

    // Add working tree node if there are uncommitted changes
    if (showWorkingTreeNode) {
      // Find HEAD commit (first commit)
      const headCommit = commits[0];
      const headLane = commitLanes.get(headCommit.sha) || 0;
      const xOffset = startX + (headLane * laneSpacing);

      newNodes.push({
        id: 'working-tree',
        type: 'workingTree',
        position: { x: xOffset, y: -commitSpacing },
        data: {
          status: $workingTreeStatus
        }
      });

      // Create edge from working tree to HEAD
      newEdges.push({
        id: `working-tree-${headCommit.sha}`,
        source: headCommit.sha,
        target: 'working-tree',
        type: 'straight',
        animated: true,
        markerEnd: {
          type: 'arrowclosed',
          width: 20,
          height: 20
        },
        style: 'stroke: var(--border-hover); stroke-width: 2px; stroke-dasharray: 5 5;'
      });
    }

    // Create nodes with proper lane positioning
    commits.forEach((commit, index) => {
      const lane = commitLanes.get(commit.sha) || 0;
      const xOffset = startX + (lane * laneSpacing);

      newNodes.push({
        id: commit.sha,
        type: 'commit',
        position: { x: xOffset, y: index * commitSpacing },
        zIndex: 1,
        data: {
          sha: commit.sha.substring(0, 7),
          fullSha: commit.fullSha,
          message: commit.message,
          author: commit.author,
          age: commit.age,
          branches: commit.branches,
          is_head: commit.is_head,
          isAhead: aheadShas.has(commit.sha),
          isRemote: commit.sha === remoteSha
        }
      });

      // Create edges from parent to this commit
      if (commit.parents && commit.parents.length > 0) {
        commit.parents.forEach(parentSha => {
          if (commitMap.has(parentSha)) {
            newEdges.push({
              id: `${parentSha}-${commit.sha}`,
              source: parentSha,
              target: commit.sha,
              type: 'straight',
              animated: false,
              markerEnd: {
                type: 'arrowclosed',
                width: 20,
                height: 20
              },
              style: 'stroke: var(--border-hover); stroke-width: 2px;'
            });
          }
        });
      }
    });

    nodes.set(newNodes);
    edges.set(newEdges);
  } else {
    nodes.set([]);
    edges.set([]);
  }

  function handleNodeClickInternal(event) {
    const nodeId = event.detail.node.id;
    const commit = $commitTree?.commits?.find(c => c.sha === nodeId);
    if (commit) {
      selectedCommit = commit;
      if (onNodeClick) {
        onNodeClick(commit);
      }
    }
  }
</script>

<div class="commit-tree">
  <div class="tree-main">
    {#if $commitTree && $commitTree.commits}
      <div class="tree-content" class:with-details={selectedCommit}>
        {#if $nodes.length > 0}
          <SvelteFlow
            bind:this={svelteFlowComponent}
            nodes={$nodes}
            edges={$edges}
            {nodeTypes}
            fitView
            nodesDraggable={false}
            nodesConnectable={false}
            elementsSelectable={true}
            panOnDrag={true}
            zoomOnScroll={true}
            zoomOnPinch={true}
            zoomOnDoubleClick={true}
            minZoom={0.3}
            maxZoom={3}
            defaultZoom={1}
            on:nodeclick={handleNodeClickInternal}
          >
            <Controls showZoom={true} showFitView={true} showInteractive={false} />
            <Background variant={BackgroundVariant.Dots} />
            <MiniMap />
            <FlowController {commandQueue} />
          </SvelteFlow>
        {:else}
          <div style="color: yellow; padding: 10px;">
            Loading nodes...
          </div>
        {/if}
      </div>

    {:else}
      <div class="tree-loading">
        <div class="spinner"></div>
        <p>Loading commit tree...</p>
      </div>
    {/if}

    {#if selectedCommit}
      <div class="details-panel">
        <div class="details-header">
          <h3>Commit Details</h3>
          <button class="close-btn" on:click={() => selectedCommit = null}>✕</button>
        </div>
        <div class="details-content">
          <div class="detail-section">
            <label>SHA</label>
            <div class="detail-value monospace">{selectedCommit.sha}</div>
          </div>

          <div class="detail-section">
            <label>Message</label>
            <div class="detail-value">{selectedCommit.message}</div>
          </div>

          <div class="detail-section">
            <label>Author</label>
            <div class="detail-value">{selectedCommit.author}</div>
          </div>

          <div class="detail-section">
            <label>Date</label>
            <div class="detail-value">{selectedCommit.age}</div>
          </div>

          {#if selectedCommit.branches && selectedCommit.branches.length > 0}
            <div class="detail-section">
              <label>Branches</label>
              <div class="detail-value">
                <div class="branches-list">
                  {#each selectedCommit.branches as branch}
                    <span class="branch-badge">{branch}</span>
                  {/each}
                </div>
              </div>
            </div>
          {/if}

          {#if selectedCommit.parents && selectedCommit.parents.length > 0}
            <div class="detail-section">
              <label>Parents</label>
              <div class="detail-value">
                {#each selectedCommit.parents as parent}
                  <div class="parent-sha monospace">{parent}</div>
                {/each}
              </div>
            </div>
          {/if}

          {#if selectedCommit.is_head}
            <div class="detail-section">
              <div class="head-badge">🔸 HEAD</div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .commit-tree {
    background: var(--bg-secondary);
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .tree-main {
    flex: 1;
    min-height: 0;
    display: flex;
    gap: 16px;
    overflow: hidden;
  }

  .tree-content {
    flex: 1;
    min-height: 0;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
    margin: 0 32px;
  }

  .tree-content.with-details {
    flex: 1;
    max-width: calc(100% - 370px);
  }

  @media (max-width: 1024px) {
    .tree-main {
      flex-direction: column;
    }

    .tree-content.with-details {
      max-width: 100%;
      flex: 1;
    }

    .details-panel {
      flex: 0 0 300px;
      max-height: 40vh;
    }
  }

  .tree-loading {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary);
    gap: 16px;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 2px solid var(--border-secondary);
    border-top-color: var(--text-secondary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Override Svelte Flow styles */
  :global(.svelte-flow) {
    background: var(--bg-secondary) !important;
  }

  :global(.svelte-flow__controls) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
  }

  :global(.svelte-flow__controls button) {
    background: var(--bg-primary) !important;
    border-bottom: 1px solid var(--border-secondary) !important;
    color: var(--text-secondary) !important;
  }

  :global(.svelte-flow__controls button:hover) {
    background: var(--bg-hover) !important;
  }

  :global(.svelte-flow__minimap) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
    transform: scale(0.6);
    transform-origin: bottom right;
    transition: transform 0.2s ease;
    opacity: 0.7;
  }

  :global(.svelte-flow__minimap:hover) {
    transform: scale(1);
    opacity: 1;
  }

  :global(.svelte-flow__edge-path) {
    stroke: var(--border-hover) !important;
    stroke-width: 2px !important;
    stroke-linecap: square !important;
    stroke-linejoin: miter !important;
  }

  .details-panel {
    flex: 0 0 350px;
    background: #2d2d2d;
    border-radius: 8px;
    border: 1px solid #444;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: slideIn 0.3s ease;
  }

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .details-header {
    padding: 16px;
    border-bottom: 1px solid #444;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .details-header h3 {
    margin: 0;
    font-size: 20px;
    color: #e0e0e0;
    font-weight: 600;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: #808080;
    font-size: 24px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .close-btn:hover {
    background: #3d3d3d;
    color: #e0e0e0;
  }

  .details-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .detail-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .detail-section label {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #808080;
    font-weight: 600;
  }

  .detail-value {
    color: #e0e0e0;
    font-size: 16px;
    line-height: 1.6;
    word-wrap: break-word;
  }

  .monospace {
    font-family: 'Monaco', 'Courier New', monospace;
    background: #1e1e1e;
    padding: 8px;
    border-radius: 4px;
    font-size: 14px;
  }

  .branches-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .branch-badge {
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 6px;
    background: #4caf50;
    color: white;
    font-weight: 600;
  }

  .parent-sha {
    margin-top: 4px;
  }

  .head-badge {
    display: inline-block;
    padding: 8px 16px;
    background: rgba(255, 215, 0, 0.2);
    border: 2px solid #ffd700;
    border-radius: 8px;
    color: #ffd700;
    font-weight: 700;
    font-size: 15px;
  }

  .load-more-container {
    position: fixed;
    bottom: 32px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
  }

  .load-more-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 12px 24px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-primary);
    border-radius: 2px;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
    box-shadow: var(--shadow-medium);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .load-more-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    box-shadow: var(--shadow-large);
  }

  .load-more-info {
    font-size: 10px;
    color: var(--text-tertiary);
    text-transform: none;
    letter-spacing: normal;
  }
</style>
