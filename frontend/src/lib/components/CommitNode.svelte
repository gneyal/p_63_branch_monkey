<script>
  import { Handle, Position } from '@xyflow/svelte';
  import { showToast } from '../stores/store.js';
  import { fetchNotes, addNote, deleteNote } from '../services/api.js';

  export let data;

  let showMenu = false;
  let showNotes = false;
  let showTooltip = false;
  let notes = [];
  let newNoteText = '';
  let loadingNotes = false;

  function getBranchColor(branches) {
    if (!branches || branches.length === 0) return '#808080';
    const branch = branches[0];
    if (branch === 'main' || branch === 'master') return '#ffd700';
    if (branch.startsWith('experiment/')) return '#4caf50';
    return '#2196f3';
  }

  function getBranchBackground(branches) {
    if (!branches || branches.length === 0) return '#2d2d2d';
    const branch = branches[0];
    if (branch === 'main' || branch === 'master') return '#3d3520';
    if (branch.startsWith('experiment/')) return '#1e3a2e';
    return '#1e2a3d';
  }

  function copySHA() {
    navigator.clipboard.writeText(data.fullSha || data.sha);
    showToast('SHA copied to clipboard', 'success');
    showMenu = false;
  }

  function jumpToCommit() {
    showToast('Jump to commit functionality coming soon', 'info');
    showMenu = false;
  }

  function branchFromHere() {
    showToast('Branch from here functionality coming soon', 'info');
    showMenu = false;
  }

  async function toggleNotes() {
    showNotes = !showNotes;
    showMenu = false;

    if (showNotes && notes.length === 0) {
      // Load notes from API when opening panel
      await loadNotes();
    }
  }

  async function loadNotes() {
    try {
      loadingNotes = true;
      notes = await fetchNotes(data.fullSha);
    } catch (error) {
      showToast(`Failed to load notes: ${error.message}`, 'error');
    } finally {
      loadingNotes = false;
    }
  }

  async function addNoteHandler() {
    if (!newNoteText.trim()) return;

    try {
      const result = await addNote(data.fullSha, newNoteText.trim());
      notes = result.notes;
      newNoteText = '';
      showToast('Note added', 'success');
    } catch (error) {
      showToast(`Failed to add note: ${error.message}`, 'error');
    }
  }

  async function deleteNoteHandler(id) {
    try {
      notes = await deleteNote(data.fullSha, id);
      showToast('Note deleted', 'success');
    } catch (error) {
      showToast(`Failed to delete note: ${error.message}`, 'error');
    }
  }

  $: borderColor = getBranchColor(data.branches);
  $: backgroundColor = getBranchBackground(data.branches);
  $: isHead = data.is_head;
</script>

<div
  class="commit-node"
  class:is-head={isHead}
  style="border-color: {borderColor}; background: {backgroundColor};"
  on:mouseenter={() => { showMenu = true; showTooltip = true; }}
  on:mouseleave={() => { showMenu = false; showTooltip = false; }}
>
  <Handle type="target" position={Position.Top} />

  <div class="node-content">
    <div class="node-message">
      {data.message.length > 60 ? data.message.substring(0, 60) + '...' : data.message}
    </div>

    {#if data.branches && data.branches.length > 0}
      <div class="branches">
        {#each data.branches as branch}
          <span class="branch-tag" style="border-color: {getBranchColor([branch])}; color: {getBranchColor([branch])};">
            {branch}
          </span>
        {/each}
      </div>
    {/if}
  </div>

  {#if showTooltip}
    <div class="commit-tooltip">
      <div class="tooltip-row">
        <span class="tooltip-label">Author:</span>
        <span class="tooltip-value">{data.author}</span>
      </div>
      <div class="tooltip-row">
        <span class="tooltip-label">Date:</span>
        <span class="tooltip-value">{data.age}</span>
      </div>
    </div>
  {/if}

  {#if showMenu}
    <div class="action-buttons">
      <button
        class="action-btn"
        on:click|stopPropagation={jumpToCommit}
        title="Jump to commit"
      >
        Jump
      </button>
      <button
        class="action-btn"
        on:click|stopPropagation={branchFromHere}
        title="Branch from here"
      >
        Branch
      </button>
      <button
        class="action-btn"
        on:click|stopPropagation={toggleNotes}
        title="Notes"
      >
        Notes
      </button>
      <button
        class="action-btn"
        on:click|stopPropagation={copySHA}
        title="Copy SHA"
      >
        Copy
      </button>
    </div>
  {/if}

  {#if showNotes}
    <div class="notes-panel" on:click|stopPropagation>
      <div class="notes-header">
        <h4>Notes</h4>
        <button class="close-notes" on:click={toggleNotes}>✕</button>
      </div>

      <div class="notes-list">
        {#if loadingNotes}
          <p class="no-notes">Loading notes...</p>
        {:else if notes.length === 0}
          <p class="no-notes">No notes yet</p>
        {:else}
          {#each notes as note (note.id)}
            <div class="note-item">
              <div class="note-text">{note.text}</div>
              <div class="note-footer">
                <span class="note-timestamp">{new Date(note.timestamp).toLocaleString()}</span>
                <button class="delete-note" on:click={() => deleteNoteHandler(note.id)}>Delete</button>
              </div>
            </div>
          {/each}
        {/if}
      </div>

      <div class="add-note">
        <input
          type="text"
          bind:value={newNoteText}
          placeholder="Add a note..."
          on:keydown={(e) => e.key === 'Enter' && addNoteHandler()}
        />
        <button on:click={addNoteHandler}>Add</button>
      </div>
    </div>
  {/if}

  <Handle type="source" position={Position.Bottom} />
</div>

<style>
  .commit-node {
    position: relative;
    border-radius: 12px;
    padding: 16px 20px;
    border: 3px solid;
    min-width: 220px;
    max-width: 300px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4);
    transition: all 0.2s;
    cursor: pointer;
  }

  .commit-node:hover {
    transform: scale(1.08);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
  }

  .commit-node.is-head {
    border-width: 4px;
    box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.4);
  }

  .node-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: center;
  }

  .node-message {
    font-size: 15px;
    font-weight: 500;
    color: #e0e0e0;
    line-height: 1.5;
    text-align: center;
    padding: 4px 8px;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }

  .branches {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .branch-tag {
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.3);
    border: 2px solid;
    font-weight: 700;
    white-space: nowrap;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }

  .action-buttons {
    position: absolute;
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: 4px;
    animation: buttonsSlideIn 0.2s ease;
  }

  @keyframes buttonsSlideIn {
    from {
      opacity: 0;
      transform: translateY(-50%) translateX(-8px);
    }
    to {
      opacity: 1;
      transform: translateY(-50%) translateX(0);
    }
  }

  .action-btn {
    padding: 4px 8px;
    background: #2d2d2d;
    border: 2px solid #444;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    color: #e0e0e0;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    white-space: nowrap;
  }

  .action-btn:hover {
    background: #3d3d3d;
    border-color: #666;
    transform: scale(1.15);
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.6);
  }

  .commit-tooltip {
    position: absolute;
    top: -80px;
    left: 50%;
    transform: translateX(-50%);
    background: #1e1e1e;
    border: 2px solid #444;
    border-radius: 8px;
    padding: 10px 14px;
    min-width: 220px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
    z-index: 999;
    animation: tooltipFadeIn 0.2s ease;
    pointer-events: none;
  }

  @keyframes tooltipFadeIn {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-5px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .tooltip-row {
    display: flex;
    gap: 8px;
    margin-bottom: 6px;
    font-size: 12px;
    line-height: 1.4;
  }

  .tooltip-row:last-child {
    margin-bottom: 0;
  }

  .tooltip-label {
    color: #808080;
    font-weight: 600;
    min-width: 50px;
  }

  .tooltip-value {
    color: #e0e0e0;
    flex: 1;
  }

  .notes-panel {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 12px;
    background: #2d2d2d;
    border: 2px solid #444;
    border-radius: 8px;
    width: 320px;
    max-height: 400px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
    z-index: 1000;
    animation: notesSlideIn 0.2s ease;
  }

  @keyframes notesSlideIn {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .notes-header {
    padding: 12px 16px;
    border-bottom: 2px solid #444;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .notes-header h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #e0e0e0;
  }

  .close-notes {
    background: transparent;
    border: none;
    color: #808080;
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .close-notes:hover {
    background: #3d3d3d;
    color: #e0e0e0;
  }

  .notes-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    max-height: 250px;
  }

  .no-notes {
    color: #808080;
    font-size: 14px;
    text-align: center;
    padding: 20px;
    margin: 0;
  }

  .note-item {
    background: #1e1e1e;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 8px;
  }

  .note-item:last-child {
    margin-bottom: 0;
  }

  .note-text {
    color: #e0e0e0;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 8px;
    word-wrap: break-word;
  }

  .note-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .note-timestamp {
    font-size: 11px;
    color: #808080;
  }

  .delete-note {
    background: transparent;
    border: 1px solid #752e2e;
    color: #ff6b6b;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .delete-note:hover {
    background: #752e2e;
    border-color: #8a3434;
  }

  .add-note {
    padding: 12px;
    border-top: 2px solid #444;
    display: flex;
    gap: 8px;
  }

  .add-note input {
    flex: 1;
    background: #1e1e1e;
    border: 1px solid #444;
    color: #e0e0e0;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }

  .add-note input:focus {
    border-color: #2196f3;
  }

  .add-note input::placeholder {
    color: #808080;
  }

  .add-note button {
    background: #2196f3;
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .add-note button:hover {
    background: #1976d2;
  }
</style>
