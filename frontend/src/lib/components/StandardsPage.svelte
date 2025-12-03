<script>
  import { onMount } from 'svelte';
  import Topbar from './Topbar.svelte';
  import ThemePicker from './ThemePicker.svelte';

  let standards = [];
  let editingStandard = null;
  let showAddModal = false;
  let newStandard = { title: '', content: '' };
  let copiedId = null;

  const STORAGE_KEY = 'branch_monkey_standards';

  const defaultStandards = [
    {
      id: 'design',
      title: 'Design Standards',
      content: `## Design Standards

### UI Components
- Use consistent spacing (8px grid)
- Follow the existing color palette
- Maintain accessibility (WCAG 2.1 AA)

### Typography
- Headings: Inter font, semi-bold
- Body: System font stack
- Code: Monospace (Courier New)

### Responsive
- Mobile-first approach
- Breakpoints: 768px, 1024px, 1200px`
    },
    {
      id: 'backend',
      title: 'Backend Standards',
      content: `## Backend Standards

### API Design
- RESTful conventions
- Use proper HTTP status codes
- Version APIs when breaking changes

### Error Handling
- Return consistent error format
- Log errors with context
- Never expose internal errors to clients

### Security
- Validate all inputs
- Use parameterized queries
- Implement rate limiting`
    },
    {
      id: 'api',
      title: 'API Standards',
      content: `## API Standards

### Request/Response
- Use JSON for request/response bodies
- Include Content-Type headers
- Paginate list endpoints

### Naming
- Use kebab-case for URLs
- Use camelCase for JSON fields
- Use plural nouns for resources

### Documentation
- Document all endpoints
- Include example requests/responses
- Note rate limits and authentication`
    },
    {
      id: 'code',
      title: 'Code Standards',
      content: `## Code Standards

### General
- Write self-documenting code
- Keep functions small and focused
- DRY but don't over-abstract

### Naming
- Use descriptive variable names
- Prefix booleans with is/has/should
- Use consistent casing per language

### Comments
- Comment the "why", not the "what"
- Keep comments up to date
- Use TODO/FIXME sparingly`
    }
  ];

  onMount(() => {
    loadStandards();
  });

  function loadStandards() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        standards = JSON.parse(saved);
      } else {
        standards = defaultStandards;
        saveStandards();
      }
    } catch (e) {
      console.error('Failed to load standards:', e);
      standards = defaultStandards;
    }
  }

  function saveStandards() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(standards));
    } catch (e) {
      console.error('Failed to save standards:', e);
    }
  }

  function copyStandard(standard) {
    navigator.clipboard.writeText(standard.content).then(() => {
      copiedId = standard.id;
      setTimeout(() => copiedId = null, 2000);
    });
  }

  function startEdit(standard) {
    editingStandard = { ...standard };
  }

  function saveEdit() {
    if (!editingStandard) return;
    const idx = standards.findIndex(s => s.id === editingStandard.id);
    if (idx !== -1) {
      standards[idx] = editingStandard;
      standards = standards;
      saveStandards();
    }
    editingStandard = null;
  }

  function cancelEdit() {
    editingStandard = null;
  }

  function openAddModal() {
    newStandard = { title: '', content: '' };
    showAddModal = true;
  }

  function addStandard() {
    if (!newStandard.title.trim()) return;
    const standard = {
      id: Date.now().toString(),
      title: newStandard.title.trim(),
      content: newStandard.content.trim()
    };
    standards = [...standards, standard];
    saveStandards();
    showAddModal = false;
  }

  function deleteStandard(id) {
    standards = standards.filter(s => s.id !== id);
    saveStandards();
  }

  function resetToDefaults() {
    if (confirm('Reset all standards to defaults? This will delete your custom standards.')) {
      standards = defaultStandards;
      saveStandards();
    }
  }
</script>

<main class="standards-page">
  <Topbar activeView="standards" />

  <div class="page-content">
    <div class="standards-container">
      <div class="standards-header">
        <div class="header-left">
          <h2>Standards</h2>
          <p class="standards-description">
            Define your team's coding standards. Copy them to share with AI assistants.
          </p>
        </div>
        <div class="header-right">
          <button class="add-btn" on:click={openAddModal}>+ Add Standard</button>
          <button class="reset-btn" on:click={resetToDefaults}>Reset</button>
        </div>
      </div>

      <div class="standards-grid">
        {#each standards as standard (standard.id)}
          <div class="standard-card">
            <div class="standard-header">
              <h3>{standard.title}</h3>
              <div class="standard-actions">
                <button
                  class="action-btn copy-btn"
                  class:copied={copiedId === standard.id}
                  on:click={() => copyStandard(standard)}
                  title="Copy to clipboard"
                >
                  {copiedId === standard.id ? 'Copied!' : 'Copy'}
                </button>
                <button
                  class="action-btn edit-btn"
                  on:click={() => startEdit(standard)}
                  title="Edit"
                >
                  Edit
                </button>
                <button
                  class="action-btn delete-btn"
                  on:click={() => deleteStandard(standard.id)}
                  title="Delete"
                >
                  x
                </button>
              </div>
            </div>
            <div class="standard-content">
              <pre>{standard.content}</pre>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <footer class="app-footer">
    <div class="footer-left"></div>
    <div class="footer-center"></div>
    <div class="footer-right">
      <ThemePicker compact={true} />
    </div>
  </footer>
</main>

<!-- Edit Modal -->
{#if editingStandard}
  <div class="modal-overlay" on:click={cancelEdit}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Edit Standard</h3>
        <button class="modal-close" on:click={cancelEdit}>x</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Title</label>
          <input type="text" bind:value={editingStandard.title} />
        </div>
        <div class="form-group">
          <label>Content</label>
          <textarea bind:value={editingStandard.content} rows="15"></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={cancelEdit}>Cancel</button>
        <button class="btn-primary" on:click={saveEdit}>Save</button>
      </div>
    </div>
  </div>
{/if}

<!-- Add Modal -->
{#if showAddModal}
  <div class="modal-overlay" on:click={() => showAddModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Add Standard</h3>
        <button class="modal-close" on:click={() => showAddModal = false}>x</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Title</label>
          <input type="text" bind:value={newStandard.title} placeholder="e.g., Testing Standards" />
        </div>
        <div class="form-group">
          <label>Content</label>
          <textarea bind:value={newStandard.content} rows="15" placeholder="Write your standards here..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" on:click={() => showAddModal = false}>Cancel</button>
        <button class="btn-primary" on:click={addStandard}>Add</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .standards-page {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .page-content {
    flex: 1;
    min-height: 0;
    overflow: auto;
    padding: 24px;
  }

  .standards-container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .standards-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    gap: 24px;
  }

  .header-left h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .standards-description {
    margin: 0;
    font-size: 14px;
    color: var(--text-secondary);
  }

  .header-right {
    display: flex;
    gap: 8px;
  }

  .add-btn {
    padding: 8px 16px;
    background: var(--accent-primary);
    border: none;
    border-radius: 4px;
    color: var(--bg-primary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .add-btn:hover {
    opacity: 0.9;
  }

  .reset-btn {
    padding: 8px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .reset-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .standards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }

  .standard-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    overflow: hidden;
  }

  .standard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-primary);
    background: var(--bg-secondary);
  }

  .standard-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .standard-actions {
    display: flex;
    gap: 6px;
  }

  .action-btn {
    padding: 4px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 3px;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .copy-btn {
    color: var(--accent-primary);
    border-color: var(--accent-primary);
  }

  .copy-btn:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .copy-btn.copied {
    background: #22c55e;
    border-color: #22c55e;
    color: white;
  }

  .edit-btn {
    color: var(--text-secondary);
  }

  .edit-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .delete-btn {
    color: var(--text-tertiary);
    padding: 4px 8px;
  }

  .delete-btn:hover {
    background: #ef4444;
    border-color: #ef4444;
    color: white;
  }

  .standard-content {
    padding: 16px;
    max-height: 300px;
    overflow-y: auto;
  }

  .standard-content pre {
    margin: 0;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
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

  .footer-left,
  .footer-center,
  .footer-right {
    display: flex;
  }

  .footer-right {
    justify-content: flex-end;
  }

  /* Modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    width: 90%;
    max-width: 600px;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-primary);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 20px;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  .modal-close:hover {
    color: var(--text-primary);
  }

  .modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
  }

  .form-group {
    margin-bottom: 16px;
  }

  .form-group label {
    display: block;
    margin-bottom: 6px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-primary);
    font-size: 14px;
    font-family: inherit;
  }

  .form-group textarea {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    resize: vertical;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding: 16px 20px;
    border-top: 1px solid var(--border-primary);
  }

  .btn-primary {
    padding: 8px 20px;
    background: var(--accent-primary);
    border: none;
    border-radius: 4px;
    color: var(--bg-primary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
  }

  .btn-primary:hover {
    opacity: 0.9;
  }

  .btn-secondary {
    padding: 8px 20px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
  }

  .btn-secondary:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  @media (max-width: 768px) {
    .standards-header {
      flex-direction: column;
    }

    .standards-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
