<script>
  import { Handle, Position } from '@xyflow/svelte';
  import { showToast, showModal } from '../stores/store.js';
  import { fetchNotes, addNote, deleteNote, createBranch, fetchPrompt, savePrompt, deletePrompt } from '../services/api.js';

  export let data;

  let showMenu = false;
  let showNotes = false;
  let showTooltip = false;
  let showFullMessage = false;
  let showPrompt = false;
  let notes = [];
  let newNoteText = '';
  let loadingNotes = false;
  let promptText = '';
  let promptTimestamp = null;
  let loadingPrompt = false;
  let hideMenuTimeout = null;

  function getBranchColor(branches) {
    if (!branches || branches.length === 0) return 'var(--branch-default)';
    const branch = branches[0];
    if (branch === 'main' || branch === 'master') return 'var(--branch-main)';
    if (branch.startsWith('experiment/')) return 'var(--branch-experiment)';
    if (branch.startsWith('feature/')) return 'var(--branch-feature)';
    if (branch.startsWith('fix/') || branch.startsWith('bugfix/')) return 'var(--branch-fix)';
    return 'var(--branch-default)';
  }

  function getBranchBackground(branches) {
    return 'var(--bg-primary)';
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
    showMenu = false;

    showModal({
      title: 'Create Branch',
      message: `Create a new branch at commit ${data.sha}`,
      showInput: true,
      inputPlaceholder: 'Branch name...',
      confirmText: 'Create',
      cancelText: 'Cancel',
      onConfirm: async (branchName) => {
        if (!branchName || !branchName.trim()) {
          showToast('Branch name cannot be empty', 'error');
          return;
        }

        try {
          await createBranch(branchName.trim(), data.fullSha);
          showToast(`Branch "${branchName}" created successfully`, 'success');
          // Reload page to show new branch
          window.location.reload();
        } catch (error) {
          showToast(error.message, 'error');
        }
      }
    });
  }

  async function toggleNotes() {
    showNotes = !showNotes;
    showMenu = false;

    if (showNotes && notes.length === 0) {
      // Load notes from API when opening panel
      await loadNotes();
    }
  }

  function toggleFullMessage() {
    showFullMessage = !showFullMessage;
    showMenu = false;
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

  async function togglePromptPanel() {
    showPrompt = !showPrompt;
    showMenu = false;

    if (showPrompt && !promptText && !loadingPrompt) {
      // Load prompt from API when opening panel
      await loadPromptData();
    }
  }

  async function loadPromptData() {
    try {
      loadingPrompt = true;
      const result = await fetchPrompt(data.fullSha);
      if (result.prompt) {
        promptText = result.prompt;
        promptTimestamp = result.timestamp;
      } else {
        promptText = '';
        promptTimestamp = null;
      }
    } catch (error) {
      showToast(`Failed to load prompt: ${error.message}`, 'error');
    } finally {
      loadingPrompt = false;
    }
  }

  async function savePromptHandler() {
    if (!promptText.trim()) {
      showToast('Prompt cannot be empty', 'error');
      return;
    }

    try {
      const result = await savePrompt(data.fullSha, promptText.trim());
      promptTimestamp = result.timestamp;
      showToast('Prompt saved', 'success');
    } catch (error) {
      showToast(`Failed to save prompt: ${error.message}`, 'error');
    }
  }

  async function deletePromptHandler() {
    try {
      await deletePrompt(data.fullSha);
      promptText = '';
      promptTimestamp = null;
      showToast('Prompt deleted', 'success');
    } catch (error) {
      showToast(`Failed to delete prompt: ${error.message}`, 'error');
    }
  }

  function copyPromptToClipboard() {
    if (!promptText) {
      showToast('No prompt to copy', 'error');
      return;
    }

    navigator.clipboard.writeText(promptText);
    showToast('Prompt copied to clipboard', 'success');
  }

  $: borderColor = getBranchColor(data.branches);
  $: backgroundColor = getBranchBackground(data.branches);
  $: isHead = data.is_head;

  function handleMouseEnter() {
    if (hideMenuTimeout) {
      clearTimeout(hideMenuTimeout);
      hideMenuTimeout = null;
    }
    showMenu = true;
    showTooltip = true;
  }

  function handleMouseLeave() {
    // Delay hiding to allow moving cursor to buttons
    hideMenuTimeout = setTimeout(() => {
      showMenu = false;
      showTooltip = false;
    }, 300);
  }

  function handleButtonsMouseEnter() {
    if (hideMenuTimeout) {
      clearTimeout(hideMenuTimeout);
      hideMenuTimeout = null;
    }
    showMenu = true;
  }

  function handleButtonsMouseLeave() {
    hideMenuTimeout = setTimeout(() => {
      showMenu = false;
      showTooltip = false;
    }, 200);
  }
</script>

<div
  class="commit-node"
  class:is-head={isHead}
  style="border-color: {borderColor}; background: {backgroundColor};"
  on:mouseenter={handleMouseEnter}
  on:mouseleave={handleMouseLeave}
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
    <div class="action-buttons" on:mouseenter={handleButtonsMouseEnter} on:mouseleave={handleButtonsMouseLeave}>
      <button
        class="action-btn"
        on:click|stopPropagation={toggleFullMessage}
        title="Show full message"
      >
        Details
      </button>
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
        on:click|stopPropagation={togglePromptPanel}
        title="Prompt"
      >
        Prompt
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

  {#if showFullMessage}
    <div class="full-message-panel z-50" on:click|stopPropagation>
      <div class="full-message-header">
        <h4>Full Message</h4>
        <button class="close-panel" on:click={toggleFullMessage}>✕</button>
      </div>
      <div class="full-message-content">
        <p class="full-message-text">{data.message}</p>
        <div class="commit-details">
          <div class="detail-row">
            <span class="detail-label">SHA:</span>
            <span class="detail-value">{data.sha}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Author:</span>
            <span class="detail-value">{data.author}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Date:</span>
            <span class="detail-value">{data.age}</span>
          </div>
        </div>
      </div>
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

  {#if showPrompt}
    <div class="prompt-panel" on:click|stopPropagation>
      <div class="prompt-header">
        <h4>Prompt</h4>
        <button class="close-prompt" on:click={togglePromptPanel}>✕</button>
      </div>

      <div class="prompt-content">
        {#if loadingPrompt}
          <p class="no-prompt">Loading prompt...</p>
        {:else if !promptText}
          <p class="no-prompt">No conversation saved for this commit yet.<br/>Continue chatting and it will be auto-captured!</p>
        {:else}
          <textarea
            value={promptText}
            readonly
            placeholder="No prompt saved yet..."
            class="prompt-textarea"
          ></textarea>

          {#if promptTimestamp}
            <div class="prompt-footer">
              <span class="prompt-timestamp">Auto-saved: {new Date(promptTimestamp).toLocaleString()}</span>
            </div>
          {/if}

          <div class="prompt-actions">
            <button class="copy-prompt" on:click={copyPromptToClipboard}>
              Copy to Clipboard
            </button>
            <button class="delete-prompt" on:click={deletePromptHandler}>
              Delete
            </button>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <Handle type="source" position={Position.Bottom} />
</div>

<style>
  .commit-node {
    position: relative;
    border-radius: 2px;
    padding: 16px 20px;
    border: 1px solid;
    border-color: var(--border-primary);
    background: var(--bg-primary);
    min-width: 220px;
    max-width: 300px;
    box-shadow: var(--shadow-small);
    transition: all 0.15s ease;
    cursor: pointer;
  }

  .commit-node:hover {
    box-shadow: var(--shadow-medium);
    border-color: var(--border-hover);
  }

  .commit-node.is-head {
    border-width: 2px;
    box-shadow: var(--shadow-medium);
  }

  .node-content {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: center;
  }

  .node-message {
    font-size: 13px;
    font-weight: 400;
    color: var(--text-primary);
    line-height: 1.4;
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
    font-size: 10px;
    padding: 3px 8px;
    border-radius: 1px;
    background: var(--bg-secondary);
    font-weight: 500;
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid;
  }

  .action-buttons {
    position: absolute;
    left: calc(100% + 12px);
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
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    font-size: 10px;
    font-weight: 500;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-small);
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    box-shadow: var(--shadow-medium);
    color: var(--text-primary);
  }

  .commit-tooltip {
    position: absolute;
    top: -80px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    padding: 12px 16px;
    min-width: 220px;
    box-shadow: var(--shadow-medium);
    z-index: 999;
    animation: tooltipFadeIn 0.15s ease;
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
    color: var(--text-tertiary);
    font-weight: 500;
    min-width: 50px;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.5px;
  }

  .tooltip-value {
    color: var(--text-primary);
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

  .full-message-panel {
    position: absolute;
    left: calc(100% + 12px);
    top: 0;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    width: 400px;
    max-width: 90vw;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-medium);
    z-index: 1000;
    animation: panelSlideIn 0.15s ease;
  }

  @keyframes panelSlideIn {
    from {
      opacity: 0;
      transform: translateX(-12px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .full-message-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .full-message-header h4 {
    margin: 0;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .close-panel {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }

  .close-panel:hover {
    color: var(--text-primary);
  }

  .full-message-content {
    padding: 16px;
  }

  .full-message-text {
    color: var(--text-primary);
    font-size: 13px;
    line-height: 1.5;
    margin: 0 0 16px 0;
    word-wrap: break-word;
    white-space: pre-wrap;
  }

  .commit-details {
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    border-radius: 1px;
    padding: 12px;
  }

  .detail-row {
    display: flex;
    gap: 12px;
    margin-bottom: 8px;
    font-size: 12px;
  }

  .detail-row:last-child {
    margin-bottom: 0;
  }

  .detail-label {
    color: var(--text-tertiary);
    font-weight: 500;
    min-width: 60px;
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.5px;
  }

  .detail-value {
    color: var(--text-primary);
    flex: 1;
    font-family: 'Courier', monospace;
  }

  .prompt-panel {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 1px;
    width: 420px;
    max-width: 90vw;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
    z-index: 1000;
    animation: promptSlideIn 0.2s ease;
  }

  @keyframes promptSlideIn {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-8px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .prompt-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .prompt-header h4 {
    margin: 0;
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .close-prompt {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;
  }

  .close-prompt:hover {
    color: var(--text-primary);
  }

  .prompt-content {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .no-prompt {
    color: var(--text-tertiary);
    font-size: 12px;
    text-align: center;
    padding: 20px;
    margin: 0;
  }

  .prompt-textarea {
    width: 100%;
    min-height: 200px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    color: var(--text-primary);
    padding: 12px;
    border-radius: 1px;
    font-size: 13px;
    font-family: 'Courier', monospace;
    line-height: 1.5;
    resize: vertical;
    outline: none;
    transition: border-color 0.15s;
  }

  .prompt-textarea[readonly] {
    background: var(--bg-secondary);
    cursor: default;
    opacity: 0.95;
  }

  .prompt-textarea:focus {
    border-color: var(--border-hover);
  }

  .prompt-textarea::placeholder {
    color: var(--text-tertiary);
  }

  .prompt-footer {
    display: flex;
    justify-content: flex-end;
  }

  .prompt-timestamp {
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .prompt-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }

  .copy-prompt {
    background: var(--accent-primary);
    border: 1px solid var(--accent-primary);
    color: var(--bg-primary);
    padding: 8px 16px;
    border-radius: 1px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .copy-prompt:hover {
    opacity: 0.9;
    box-shadow: var(--shadow-small);
  }

  .delete-prompt {
    background: transparent;
    border: 1px solid var(--border-secondary);
    color: var(--text-secondary);
    padding: 8px 16px;
    border-radius: 1px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .delete-prompt:hover {
    border-color: #ff6b6b;
    color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
  }
</style>
