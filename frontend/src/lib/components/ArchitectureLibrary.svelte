<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import {
    SvelteFlow,
    Controls,
    Background,
    BackgroundVariant,
    MiniMap
  } from '@xyflow/svelte';
  import '@xyflow/svelte/dist/style.css';
  import {
    fetchContextPrompt,
    fetchContextHistory,
    fetchContextEntry,
    saveContextSummary,
    deleteContextEntry
  } from '../services/api.js';
  import { showToast } from '../stores/store.js';
  import ChipNode from './ChipNode.svelte';

  import { createEventDispatcher } from 'svelte';

  export let onClose = () => {};
  export let inline = true;

  const dispatch = createEventDispatcher();

  let history = [];
  let loading = true;
  let loadingHistory = false;
  let selectedEntry = null;
  let parsedArchitecture = null;
  let parseError = null;
  let activeSection = 'overview';
  let showPromptModal = false;
  let showSaveModal = false;
  let currentPrompt = '';
  let saveContent = '';
  let saving = false;
  let viewMode = 'flow'; // 'list', 'flow', or 'raw'

  // Multi-select state
  let selectedNodes = [];
  let showPromptBuilder = false;
  let promptInstruction = '';
  let generatedPrompt = '';

  // Prompt builder options
  let promptOptions = {
    noOtherFiles: true,
    keepItSimple: false,
    explainChanges: false,
    addTests: false,
    preserveStyle: true,
    noNewDeps: false
  };

  // Draggable modal state
  let modalPosition = { x: 0, y: 0 };
  let isDragging = false;
  let dragOffset = { x: 0, y: 0 };
  let showConstraintsPopup = false;

  function handleDragStart(e) {
    if (e.target.closest('button') || e.target.closest('textarea') || e.target.closest('input')) return;
    isDragging = true;
    const rect = e.currentTarget.closest('.prompt-builder').getBoundingClientRect();
    dragOffset = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
    document.addEventListener('mousemove', handleDragMove);
    document.addEventListener('mouseup', handleDragEnd);
  }

  function handleDragMove(e) {
    if (!isDragging) return;
    modalPosition = {
      x: e.clientX - dragOffset.x - window.innerWidth / 2 + 450,
      y: e.clientY - dragOffset.y - window.innerHeight / 2 + 250
    };
  }

  function handleDragEnd() {
    isDragging = false;
    document.removeEventListener('mousemove', handleDragMove);
    document.removeEventListener('mouseup', handleDragEnd);
  }

  // Handle node click for selection
  // Click to add to selection, click again to remove (no modifier key needed)
  function handleNodeClick(eventDetail) {
    const clickedNode = eventDetail.node;

    // Toggle: if already selected, remove; otherwise add
    const index = selectedNodes.findIndex(n => n.id === clickedNode.id);
    if (index >= 0) {
      selectedNodes = selectedNodes.filter(n => n.id !== clickedNode.id);
    } else {
      selectedNodes = [...selectedNodes, clickedNode];
    }

    // Update nodes store to reflect selection state
    const selectedIds = new Set(selectedNodes.map(n => n.id));
    nodes.update(n => n.map(node => ({
      ...node,
      selected: selectedIds.has(node.id)
    })));

    dispatch('selectionchange', { nodes: selectedNodes });
  }

  // Handle pane click to deselect all
  function handlePaneClick() {
    selectedNodes = [];
    // Clear selection state on all nodes
    nodes.update(n => n.map(node => ({ ...node, selected: false })));
    dispatch('selectionchange', { nodes: selectedNodes });
  }

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    chip: ChipNode
  };

  const SECTIONS = [
    { id: 'overview', label: 'Overview', icon: 'info' },
    { id: 'tech_stack', label: 'Tech Stack', icon: 'stack' },
    { id: 'endpoints', label: 'Endpoints', icon: 'api' },
    { id: 'entities', label: 'Entities', icon: 'data' },
    { id: 'tables', label: 'Database', icon: 'db' },
    { id: 'ui_components', label: 'UI/UX', icon: 'ui' },
    { id: 'notes', label: 'Notes', icon: 'notes' },
  ];

  onMount(async () => {
    await loadHistory();
    loading = false;
  });

  async function loadHistory() {
    try {
      loadingHistory = true;
      const data = await fetchContextHistory('architecture');
      history = data.history || [];
      // Auto-select the last (oldest) entry in history
      if (history.length > 0 && !selectedEntry) {
        const lastEntry = history[history.length - 1];
        handleEntryClick(lastEntry);
      }
    } catch (err) {
      showToast(`Failed to load history: ${err.message}`, 'error');
      history = [];
    } finally {
      loadingHistory = false;
    }
  }

  async function handleEntryClick(entry) {
    try {
      const data = await fetchContextEntry(entry.id);
      selectedEntry = data.entry;
      parseArchitecture(selectedEntry.content);
    } catch (err) {
      showToast(`Failed to load entry: ${err.message}`, 'error');
    }
  }

  function parseArchitecture(content) {
    try {
      // Try to parse as JSON
      const parsed = JSON.parse(content);
      parsedArchitecture = parsed;
      parseError = null;
      activeSection = 'overview';
      // Generate flow data from the architecture
      generateFlowData(parsed);
    } catch (err) {
      // Not valid JSON - treat as plain text
      parsedArchitecture = null;
      parseError = 'Content is not structured JSON. Displaying as plain text.';
      nodes.set([]);
      edges.set([]);
    }
  }

  function generateFlowData(arch) {
    const newNodes = [];
    const newEdges = [];

    // Layout configuration - layered architecture
    const nodeWidth = 180;
    const nodeHeight = 100;
    const horizontalGap = 40;
    const verticalGap = 80;
    const layerGap = 120;

    // Track node IDs by layer for connections
    const layers = {
      pages: [],      // Layer 0 - Pages/Views
      components: [], // Layer 1 - UI Components
      endpoints: [],  // Layer 2 - API Endpoints
      entities: [],   // Layer 3 - Data Entities
      tables: []      // Layer 4 - Database Tables
    };

    // Helper to calculate X position for centering items in a row
    function getRowStartX(itemCount) {
      const totalWidth = itemCount * nodeWidth + (itemCount - 1) * horizontalGap;
      return Math.max(50, (1200 - totalWidth) / 2);
    }

    let currentY = 50;

    // Layer 0: Pages (extracted from UI components with type 'page' or routes)
    const pages = arch.ui_components?.filter(c => c.type === 'page' || c.routes?.length > 0) || [];
    if (pages.length > 0) {
      const startX = getRowStartX(pages.length);
      pages.forEach((page, i) => {
        const id = `page-${i}`;
        layers.pages.push(id);
        newNodes.push({
          id,
          type: 'chip',
          position: { x: startX + i * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'page',
            name: page.name,
            description: page.description,
            path: page.routes?.[0] || page.file_path
          }
        });
      });
      currentY += nodeHeight + layerGap;
    }

    // Layer 1: Components (UI components that are not pages)
    const components = arch.ui_components?.filter(c => c.type !== 'page' && !c.routes?.length) || [];
    if (components.length > 0) {
      const startX = getRowStartX(Math.min(components.length, 6));
      components.slice(0, 6).forEach((comp, i) => {
        const id = `comp-${i}`;
        layers.components.push(id);
        newNodes.push({
          id,
          type: 'chip',
          position: { x: startX + i * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'component',
            name: comp.name,
            description: comp.description,
            meta: comp.type || (comp.props?.length ? `${comp.props.length} props` : null)
          }
        });
      });
      if (components.length > 6) {
        newNodes.push({
          id: 'comp-more',
          type: 'chip',
          position: { x: startX + 6 * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'component',
            name: `+${components.length - 6} more`,
            meta: 'components'
          }
        });
      }
      currentY += nodeHeight + layerGap;
    }

    // Layer 2: API Endpoints
    if (arch.endpoints?.length > 0) {
      const startX = getRowStartX(Math.min(arch.endpoints.length, 5));
      arch.endpoints.slice(0, 5).forEach((ep, i) => {
        const id = `endpoint-${i}`;
        layers.endpoints.push(id);
        newNodes.push({
          id,
          type: 'chip',
          position: { x: startX + i * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'endpoint',
            name: ep.path?.split('/').pop() || ep.path,
            path: ep.path,
            method: ep.method,
            description: ep.description
          }
        });
      });
      if (arch.endpoints.length > 5) {
        newNodes.push({
          id: 'endpoint-more',
          type: 'chip',
          position: { x: startX + 5 * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'endpoint',
            name: `+${arch.endpoints.length - 5} more`,
            meta: 'endpoints'
          }
        });
      }
      currentY += nodeHeight + layerGap;
    }

    // Layer 3: Entities
    if (arch.entities?.length > 0) {
      const startX = getRowStartX(Math.min(arch.entities.length, 5));
      arch.entities.slice(0, 5).forEach((entity, i) => {
        const id = `entity-${i}`;
        layers.entities.push(id);
        newNodes.push({
          id,
          type: 'chip',
          position: { x: startX + i * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'entity',
            name: entity.name,
            description: entity.description,
            meta: entity.fields?.length ? `${entity.fields.length} fields` : null
          }
        });
      });
      if (arch.entities.length > 5) {
        newNodes.push({
          id: 'entity-more',
          type: 'chip',
          position: { x: startX + 5 * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'entity',
            name: `+${arch.entities.length - 5} more`,
            meta: 'entities'
          }
        });
      }
      currentY += nodeHeight + layerGap;
    }

    // Layer 4: Database Tables
    if (arch.tables?.length > 0) {
      const startX = getRowStartX(Math.min(arch.tables.length, 5));
      arch.tables.slice(0, 5).forEach((table, i) => {
        const id = `table-${i}`;
        layers.tables.push(id);
        newNodes.push({
          id,
          type: 'chip',
          position: { x: startX + i * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'table',
            name: table.name,
            description: table.description,
            meta: table.columns?.length ? `${table.columns.length} columns` : null
          }
        });
      });
      if (arch.tables.length > 5) {
        newNodes.push({
          id: 'table-more',
          type: 'chip',
          position: { x: startX + 5 * (nodeWidth + horizontalGap), y: currentY },
          data: {
            layerType: 'table',
            name: `+${arch.tables.length - 5} more`,
            meta: 'tables'
          }
        });
      }
    }

    // Create edges between layers (connecting related items) - vim colors
    // Pages -> Components (fan out)
    if (layers.pages.length > 0 && layers.components.length > 0) {
      layers.pages.forEach(pageId => {
        layers.components.forEach(compId => {
          newEdges.push({
            id: `${pageId}-${compId}`,
            source: pageId,
            target: compId,
            type: 'smoothstep',
            style: 'stroke: #c678dd; stroke-width: 1.5px; opacity: 0.4;'  // vim magenta
          });
        });
      });
    }

    // Components -> Endpoints (fan out)
    const sourceLayer1 = layers.components.length > 0 ? layers.components : layers.pages;
    if (sourceLayer1.length > 0 && layers.endpoints.length > 0) {
      sourceLayer1.forEach(srcId => {
        layers.endpoints.forEach(epId => {
          newEdges.push({
            id: `${srcId}-${epId}`,
            source: srcId,
            target: epId,
            type: 'smoothstep',
            style: 'stroke: #61afef; stroke-width: 1.5px; opacity: 0.4;'  // vim blue
          });
        });
      });
    }

    // Endpoints -> Entities
    if (layers.endpoints.length > 0 && layers.entities.length > 0) {
      layers.endpoints.forEach(epId => {
        layers.entities.forEach(entityId => {
          newEdges.push({
            id: `${epId}-${entityId}`,
            source: epId,
            target: entityId,
            type: 'smoothstep',
            style: 'stroke: #98c379; stroke-width: 1.5px; opacity: 0.4;'  // vim green
          });
        });
      });
    }

    // Entities -> Tables (try to match by name, otherwise fan out)
    if (layers.entities.length > 0 && layers.tables.length > 0) {
      layers.entities.forEach((entityId, i) => {
        // Connect each entity to corresponding table or all tables
        const tableId = layers.tables[i] || layers.tables[0];
        newEdges.push({
          id: `${entityId}-${tableId}`,
          source: entityId,
          target: tableId,
          type: 'smoothstep',
          animated: true,
          style: 'stroke: #e5c07b; stroke-width: 2px;'  // vim yellow
        });
      });
    }

    // Ensure all nodes are selectable
    const selectableNodes = newNodes.map(n => ({ ...n, selectable: true }));
    nodes.set(selectableNodes);
    edges.set(newEdges);
  }

  async function handleGeneratePrompt() {
    try {
      const data = await fetchContextPrompt('architecture');
      currentPrompt = data.prompt;
      showPromptModal = true;
    } catch (err) {
      showToast(`Failed to get prompt: ${err.message}`, 'error');
    }
  }

  function handleCopyPrompt() {
    navigator.clipboard.writeText(currentPrompt);
    showToast('Prompt copied to clipboard! Paste it in your AI tool.', 'success');
  }

  function handleOpenSaveModal() {
    saveContent = '';
    showSaveModal = true;
  }

  async function handleSave() {
    if (!saveContent.trim()) {
      showToast('Please enter the architecture JSON', 'error');
      return;
    }

    // Validate JSON
    try {
      JSON.parse(saveContent);
    } catch (err) {
      showToast(`Invalid JSON: ${err.message}`, 'error');
      return;
    }

    try {
      saving = true;
      await saveContextSummary('architecture', saveContent);
      showToast('Architecture saved successfully!', 'success');
      showSaveModal = false;
      saveContent = '';
      await loadHistory();
    } catch (err) {
      showToast(`Failed to save: ${err.message}`, 'error');
    } finally {
      saving = false;
    }
  }

  async function handleDelete(entryId) {
    if (!confirm('Are you sure you want to delete this architecture?')) {
      return;
    }

    try {
      await deleteContextEntry(entryId);
      showToast('Architecture deleted', 'success');
      if (selectedEntry?.id === entryId) {
        selectedEntry = null;
        parsedArchitecture = null;
      }
      await loadHistory();
    } catch (err) {
      showToast(`Failed to delete: ${err.message}`, 'error');
    }
  }

  function handleCopyContent() {
    if (selectedEntry?.content) {
      navigator.clipboard.writeText(selectedEntry.content);
      showToast('Content copied to clipboard', 'success');
    }
  }

  function formatDate(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function getMethodColor(method) {
    const colors = {
      GET: '#61affe',
      POST: '#49cc90',
      PUT: '#fca130',
      PATCH: '#50e3c2',
      DELETE: '#f93e3e',
    };
    return colors[method] || '#999';
  }

  function getCategoryIcon(category) {
    const icons = {
      language: 'L',
      framework: 'F',
      database: 'D',
      tool: 'T',
      service: 'S',
    };
    return icons[category] || '?';
  }


  // Expose methods for parent
  export function getSelectedNodes() {
    return selectedNodes;
  }

  export function openPromptBuilder() {
    if (selectedNodes.length > 0) {
      handleOpenPromptBuilder();
    }
  }

  function clearSelection() {
    selectedNodes = [];
    // Update the nodes store to clear selection
    nodes.update(n => n.map(node => ({ ...node, selected: false })));
  }

  function handleOpenPromptBuilder() {
    promptInstruction = '';
    modalPosition = { x: 0, y: 0 };
    showPromptBuilder = true;
    generateContextPrompt();
  }

  function generateContextPrompt() {
    const context = selectedNodes.map(node => {
      const d = node.data || {};
      let info = `- ${d.layerType?.toUpperCase() || 'NODE'}: ${d.name || node.id}`;
      if (d.path) info += `\n  Path: ${d.path}`;
      if (d.method) info += `\n  Method: ${d.method}`;
      if (d.description) info += `\n  Description: ${d.description}`;
      return info;
    }).join('\n\n');

    const fileHints = selectedNodes
      .filter(n => n.data?.path)
      .map(n => n.data.path);

    let parts = [];

    // Context section
    parts.push(`## Context\n\nWork with these specific parts of the codebase:\n\n${context}`);

    if (fileHints.length > 0) {
      parts.push(`## Files to focus on\n\n${fileHints.map(f => `- ${f}`).join('\n')}`);
    }

    // Task section
    if (promptInstruction.trim()) {
      parts.push(`## Task\n\n${promptInstruction.trim()}`);
    }

    // Build constraints from checkboxes
    const constraints = [];
    if (promptOptions.noOtherFiles) {
      constraints.push('Do NOT modify files outside the scope defined above');
    }
    if (promptOptions.keepItSimple) {
      constraints.push('Keep the solution simple and minimal - no over-engineering');
    }
    if (promptOptions.explainChanges) {
      constraints.push('Explain each change you make and why');
    }
    if (promptOptions.addTests) {
      constraints.push('Add or update tests for the changes');
    }
    if (promptOptions.preserveStyle) {
      constraints.push('Preserve the existing code style and patterns');
    }
    if (promptOptions.noNewDeps) {
      constraints.push('Do not add new dependencies unless absolutely necessary');
    }

    if (constraints.length > 0) {
      parts.push(`## Constraints\n\n${constraints.map(c => `- ${c}`).join('\n')}`);
    }

    generatedPrompt = parts.join('\n\n');
  }

  function handleCopyContextPrompt() {
    navigator.clipboard.writeText(generatedPrompt);
    showToast('Prompt copied to clipboard!', 'success');
  }
</script>

<div class="architecture-inline">

    {#if loading}
      <div class="loading">
        <div class="spinner"></div>
        <p>Loading...</p>
      </div>
    {:else}
      <div class="panel-body">
        <div class="tab-header">
          <div class="tab-info">
            <p class="tab-description">System design, tech stack, API endpoints, entities, and UI components</p>
          </div>
          <div class="tab-actions">
            <button class="action-btn primary" on:click={handleGeneratePrompt}>
              Generate Prompt
            </button>
            <button class="action-btn" on:click={handleOpenSaveModal}>
              Save Architecture
            </button>
          </div>
        </div>

        <div class="content-layout">
          <!-- History Panel -->
          <div class="history-panel">
            <div class="history-header">History ({history.length})</div>
            {#if loadingHistory}
              <div class="loading-small">
                <div class="spinner-small"></div>
              </div>
            {:else if history.length === 0}
              <div class="empty-history">
                <p>No architecture docs yet</p>
                <p class="hint">Click "Generate Prompt" to create one</p>
              </div>
            {:else}
              <div class="history-list">
                {#each history as entry}
                  <div
                    class="history-item"
                    class:selected={selectedEntry?.id === entry.id}
                    role="button"
                    tabindex="0"
                    on:click={() => handleEntryClick(entry)}
                    on:keydown={(e) => e.key === 'Enter' && handleEntryClick(entry)}
                  >
                    <div class="history-date">{formatDate(entry.created_at)}</div>
                    <div class="history-preview">{entry.preview}</div>
                    <button
                      class="delete-btn"
                      on:click|stopPropagation={() => handleDelete(entry.id)}
                      title="Delete"
                    >
                      X
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>

          <!-- Content Panel -->
          <div class="content-panel">
            {#if selectedEntry}
              {#if parsedArchitecture}
                <!-- View Mode Toggle -->
                <div class="view-mode-toggle">
                  <button
                    class="view-mode-btn"
                    class:active={viewMode === 'list'}
                    on:click={() => viewMode = 'list'}
                  >
                    List
                  </button>
                  <button
                    class="view-mode-btn"
                    class:active={viewMode === 'flow'}
                    on:click={() => viewMode = 'flow'}
                  >
                    Flow
                  </button>
                  <button
                    class="view-mode-btn"
                    class:active={viewMode === 'raw'}
                    on:click={() => viewMode = 'raw'}
                  >
                    Raw
                  </button>
                </div>

                {#if viewMode === 'flow'}
                  <!-- SvelteFlow Chip View -->
                  <div class="svelteflow-view">
                    {#if $nodes.length > 0}
                      <SvelteFlow
                        nodes={$nodes}
                        edges={$edges}
                        {nodeTypes}
                        fitView
                        minZoom={0.3}
                        maxZoom={1.5}
                        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
                        panOnDrag={true}
                        elementsSelectable={true}
                        nodesConnectable={false}
                        onnodeclick={handleNodeClick}
                        onpaneclick={handlePaneClick}
                      >
                        <Background variant={BackgroundVariant.Dots} gap={20} />
                        <Controls />
                        <MiniMap />
                      </SvelteFlow>
                    {:else}
                      <div class="empty-flow">
                        <p>No architecture data to visualize</p>
                        <p class="hint">Architecture needs UI components, endpoints, entities, or tables</p>
                      </div>
                    {/if}

                    <!-- Selection actions bar -->
                    {#if selectedNodes.length > 0}
                      <div class="selection-bar">
                        <span class="selection-count">{selectedNodes.length} selected</span>
                        <button class="selection-action" on:click={handleOpenPromptBuilder}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                          Write Prompt
                        </button>
                        <button class="selection-action secondary" on:click={clearSelection}>
                          Clear
                        </button>
                      </div>
                    {/if}

                    <!-- Tech Stack Footer -->
                    {#if parsedArchitecture.tech_stack?.length > 0}
                      <div class="tech-bar">
                        <span class="tech-bar-label">Stack:</span>
                        {#each parsedArchitecture.tech_stack as tech}
                          <span class="tech-tag" class:lang={tech.category === 'language'} class:framework={tech.category === 'framework'} class:database={tech.category === 'database'}>
                            {tech.name}
                          </span>
                        {/each}
                      </div>
                    {/if}
                  </div>
                {:else if viewMode === 'raw'}
                  <!-- Raw JSON View -->
                  <div class="raw-view">
                    <div class="raw-header">
                      <button class="copy-btn" on:click={handleCopyContent}>Copy JSON</button>
                    </div>
                    <pre class="raw-content">{JSON.stringify(parsedArchitecture, null, 2)}</pre>
                  </div>
                {:else}
                  <!-- Structured View -->
                  <div class="structured-view">
                    <div class="section-tabs">
                      {#each SECTIONS as section}
                        <button
                          class="section-tab"
                          class:active={activeSection === section.id}
                          on:click={() => activeSection = section.id}
                        >
                          {section.label}
                          {#if section.id !== 'overview' && section.id !== 'notes'}
                            <span class="count">
                              {parsedArchitecture[section.id]?.length || 0}
                            </span>
                          {/if}
                        </button>
                      {/each}
                    </div>

                    <div class="section-content">
                    {#if activeSection === 'overview'}
                      <div class="overview-section">
                        <h2>{parsedArchitecture.project_name || 'Unnamed Project'}</h2>
                        {#if parsedArchitecture.version}
                          <span class="version">v{parsedArchitecture.version}</span>
                        {/if}
                        <p class="description">{parsedArchitecture.description || 'No description'}</p>
                        <div class="overview-stats">
                          <div class="stat">
                            <span class="stat-value">{parsedArchitecture.tech_stack?.length || 0}</span>
                            <span class="stat-label">Technologies</span>
                          </div>
                          <div class="stat">
                            <span class="stat-value">{parsedArchitecture.endpoints?.length || 0}</span>
                            <span class="stat-label">Endpoints</span>
                          </div>
                          <div class="stat">
                            <span class="stat-value">{parsedArchitecture.entities?.length || 0}</span>
                            <span class="stat-label">Entities</span>
                          </div>
                          <div class="stat">
                            <span class="stat-value">{parsedArchitecture.tables?.length || 0}</span>
                            <span class="stat-label">Tables</span>
                          </div>
                          <div class="stat">
                            <span class="stat-value">{parsedArchitecture.ui_components?.length || 0}</span>
                            <span class="stat-label">Components</span>
                          </div>
                        </div>
                      </div>

                    {:else if activeSection === 'tech_stack'}
                      <div class="tech-stack-section">
                        {#if parsedArchitecture.tech_stack?.length > 0}
                          <div class="tech-grid">
                            {#each parsedArchitecture.tech_stack as tech}
                              <div class="tech-card">
                                <div class="tech-icon">{getCategoryIcon(tech.category)}</div>
                                <div class="tech-info">
                                  <div class="tech-name">
                                    {tech.name}
                                    {#if tech.version}
                                      <span class="tech-version">{tech.version}</span>
                                    {/if}
                                  </div>
                                  <div class="tech-category">{tech.category}</div>
                                  {#if tech.purpose}
                                    <div class="tech-purpose">{tech.purpose}</div>
                                  {/if}
                                </div>
                              </div>
                            {/each}
                          </div>
                        {:else}
                          <div class="empty-section">No tech stack defined</div>
                        {/if}
                      </div>

                    {:else if activeSection === 'endpoints'}
                      <div class="endpoints-section">
                        {#if parsedArchitecture.endpoints?.length > 0}
                          <div class="endpoints-list">
                            {#each parsedArchitecture.endpoints as endpoint}
                              <div class="endpoint-card">
                                <div class="endpoint-header">
                                  <span class="method" style="background: {getMethodColor(endpoint.method)}">{endpoint.method}</span>
                                  <span class="path">{endpoint.path}</span>
                                  {#if endpoint.auth_required}
                                    <span class="auth-badge">AUTH</span>
                                  {/if}
                                </div>
                                <div class="endpoint-description">{endpoint.description}</div>
                                {#if endpoint.params?.length > 0}
                                  <div class="endpoint-params">
                                    <div class="params-label">Parameters:</div>
                                    {#each endpoint.params as param}
                                      <div class="param">
                                        <span class="param-name">{param.name}</span>
                                        <span class="param-type">{param.type}</span>
                                        <span class="param-location">{param.location}</span>
                                        {#if !param.required}
                                          <span class="param-optional">optional</span>
                                        {/if}
                                      </div>
                                    {/each}
                                  </div>
                                {/if}
                                {#if endpoint.response_type}
                                  <div class="endpoint-response">
                                    <span class="response-label">Returns:</span>
                                    <span class="response-type">{endpoint.response_type}</span>
                                  </div>
                                {/if}
                                {#if endpoint.tags?.length > 0}
                                  <div class="endpoint-tags">
                                    {#each endpoint.tags as tag}
                                      <span class="tag">{tag}</span>
                                    {/each}
                                  </div>
                                {/if}
                              </div>
                            {/each}
                          </div>
                        {:else}
                          <div class="empty-section">No endpoints defined</div>
                        {/if}
                      </div>

                    {:else if activeSection === 'entities'}
                      <div class="entities-section">
                        {#if parsedArchitecture.entities?.length > 0}
                          <div class="entities-list">
                            {#each parsedArchitecture.entities as entity}
                              <div class="entity-card">
                                <div class="entity-header">
                                  <span class="entity-name">{entity.name}</span>
                                  {#if entity.file_path}
                                    <span class="entity-path">{entity.file_path}</span>
                                  {/if}
                                </div>
                                <div class="entity-description">{entity.description}</div>
                                {#if entity.fields?.length > 0}
                                  <table class="fields-table">
                                    <thead>
                                      <tr>
                                        <th>Field</th>
                                        <th>Type</th>
                                        <th>Description</th>
                                        <th>Constraints</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {#each entity.fields as field}
                                        <tr>
                                          <td class="field-name">
                                            {field.name}
                                            {#if !field.required}
                                              <span class="optional">?</span>
                                            {/if}
                                          </td>
                                          <td class="field-type">{field.type}</td>
                                          <td class="field-desc">{field.description || '-'}</td>
                                          <td class="field-constraints">
                                            {field.constraints?.join(', ') || '-'}
                                          </td>
                                        </tr>
                                      {/each}
                                    </tbody>
                                  </table>
                                {/if}
                                {#if entity.relationships?.length > 0}
                                  <div class="entity-relationships">
                                    <span class="rel-label">Relationships:</span>
                                    {#each entity.relationships as rel}
                                      <span class="relationship">{rel}</span>
                                    {/each}
                                  </div>
                                {/if}
                              </div>
                            {/each}
                          </div>
                        {:else}
                          <div class="empty-section">No entities defined</div>
                        {/if}
                      </div>

                    {:else if activeSection === 'tables'}
                      <div class="tables-section">
                        {#if parsedArchitecture.tables?.length > 0}
                          <div class="tables-list">
                            {#each parsedArchitecture.tables as table}
                              <div class="table-card">
                                <div class="table-header">
                                  <span class="table-name">{table.name}</span>
                                </div>
                                <div class="table-description">{table.description}</div>
                                {#if table.columns?.length > 0}
                                  <table class="columns-table">
                                    <thead>
                                      <tr>
                                        <th>Column</th>
                                        <th>Type</th>
                                        <th>Nullable</th>
                                        <th>Key</th>
                                        <th>Default</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {#each table.columns as col}
                                        <tr>
                                          <td class="col-name">
                                            {col.name}
                                            {#if col.primary_key}
                                              <span class="pk">PK</span>
                                            {/if}
                                          </td>
                                          <td class="col-type">{col.type}</td>
                                          <td class="col-nullable">{col.nullable ? 'YES' : 'NO'}</td>
                                          <td class="col-fk">
                                            {#if col.foreign_key}
                                              <span class="fk">FK: {col.foreign_key}</span>
                                            {:else}
                                              -
                                            {/if}
                                          </td>
                                          <td class="col-default">{col.default || '-'}</td>
                                        </tr>
                                      {/each}
                                    </tbody>
                                  </table>
                                {/if}
                                {#if table.indexes?.length > 0}
                                  <div class="table-indexes">
                                    <span class="idx-label">Indexes:</span>
                                    {#each table.indexes as idx}
                                      <span class="index">
                                        {idx.name} ({idx.columns.join(', ')})
                                        {#if idx.unique}
                                          <span class="unique">UNIQUE</span>
                                        {/if}
                                      </span>
                                    {/each}
                                  </div>
                                {/if}
                              </div>
                            {/each}
                          </div>
                        {:else}
                          <div class="empty-section">No database tables defined</div>
                        {/if}
                      </div>

                    {:else if activeSection === 'ui_components'}
                      <div class="ui-section">
                        {#if parsedArchitecture.ui_components?.length > 0}
                          <div class="ui-list">
                            {#each parsedArchitecture.ui_components as comp}
                              <div class="ui-card">
                                <div class="ui-header">
                                  <span class="ui-name">{comp.name}</span>
                                  <span class="ui-type">{comp.type}</span>
                                </div>
                                <div class="ui-description">{comp.description}</div>
                                {#if comp.file_path}
                                  <div class="ui-path">{comp.file_path}</div>
                                {/if}
                                {#if comp.routes?.length > 0}
                                  <div class="ui-routes">
                                    <span class="routes-label">Routes:</span>
                                    {#each comp.routes as route}
                                      <span class="route">{route}</span>
                                    {/each}
                                  </div>
                                {/if}
                                {#if comp.props?.length > 0}
                                  <div class="ui-props">
                                    <span class="props-label">Props:</span>
                                    {#each comp.props as prop}
                                      <span class="prop">{prop}</span>
                                    {/each}
                                  </div>
                                {/if}
                                {#if comp.children?.length > 0}
                                  <div class="ui-children">
                                    <span class="children-label">Children:</span>
                                    {#each comp.children as child}
                                      <span class="child">{child}</span>
                                    {/each}
                                  </div>
                                {/if}
                              </div>
                            {/each}
                          </div>
                        {:else}
                          <div class="empty-section">No UI components defined</div>
                        {/if}
                      </div>

                    {:else if activeSection === 'notes'}
                      <div class="notes-section">
                        {#if parsedArchitecture.notes?.length > 0}
                          <ul class="notes-list">
                            {#each parsedArchitecture.notes as note}
                              <li>{note}</li>
                            {/each}
                          </ul>
                        {:else}
                          <div class="empty-section">No notes</div>
                        {/if}
                      </div>
                    {/if}
                    </div>
                  </div>
                {/if}
              {:else}
                <!-- Plain Text View (legacy) -->
                <div class="plain-view">
                  <div class="content-header">
                    <span class="content-date">{formatDate(selectedEntry.created_at)}</span>
                    <button class="copy-btn" on:click={handleCopyContent}>Copy</button>
                  </div>
                  {#if parseError}
                    <div class="parse-warning">{parseError}</div>
                  {/if}
                  <div class="content-body">
                    <pre>{selectedEntry.content}</pre>
                  </div>
                </div>
              {/if}
            {:else}
              <div class="empty-content">
                <p>Select an architecture document to view</p>
                <p class="hint">Or generate a new one using the prompt</p>
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}

</div>

<!-- Prompt Modal -->
{#if showPromptModal}
  <div class="modal-backdrop" on:click={() => showPromptModal = false}>
    <div class="modal large" on:click|stopPropagation>
      <div class="modal-header">
        <h4>AI Prompt for Architecture</h4>
        <button class="close-btn" on:click={() => showPromptModal = false}>X</button>
      </div>
      <div class="modal-body">
        <p class="modal-instructions">
          Copy this prompt and paste it into your AI tool (Claude, ChatGPT, etc.).
          The AI will analyze your codebase and generate a structured JSON architecture document.
        </p>
        <pre class="prompt-content">{currentPrompt}</pre>
      </div>
      <div class="modal-footer">
        <button class="action-btn primary" on:click={handleCopyPrompt}>
          Copy Prompt
        </button>
        <button class="action-btn" on:click={() => showPromptModal = false}>
          Close
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Prompt Builder Modal (no backdrop - floating window) -->
{#if showPromptBuilder}
  <div
    class="modal prompt-builder floating"
    class:dragging={isDragging}
    style="transform: translate({modalPosition.x}px, {modalPosition.y}px)"
  >
    <div class="modal-header draggable" on:mousedown={handleDragStart}>
      <h4>Write Prompt with Context</h4>
      <button class="close-btn" on:click={() => showPromptBuilder = false}>X</button>
    </div>
    <div class="modal-body">
      <!-- Context chips -->
      <div class="context-summary compact">
        <div class="context-chips">
          {#each selectedNodes as node}
            <div class="context-chip" class:page={node.data?.layerType === 'page'} class:component={node.data?.layerType === 'component'} class:endpoint={node.data?.layerType === 'endpoint'} class:entity={node.data?.layerType === 'entity'} class:table={node.data?.layerType === 'table'}>
              <span class="chip-type">{node.data?.layerType || 'node'}</span>
              <span class="chip-name">{node.data?.name || node.id}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- Task input row with constraints button -->
      <div class="task-row">
        <textarea
          class="prompt-textarea task-input"
          bind:value={promptInstruction}
          on:input={generateContextPrompt}
          placeholder="What do you want to do with these components?"
          rows="2"
        ></textarea>
        <div class="constraints-wrapper">
          <button
            class="constraints-btn"
            class:has-constraints={Object.values(promptOptions).some(v => v)}
            on:click={() => showConstraintsPopup = !showConstraintsPopup}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
            </svg>
          </button>
          {#if showConstraintsPopup}
            <div class="constraints-popup">
              <div class="constraints-popup-header">Constraints</div>
              <label class="option-item">
                <input type="checkbox" bind:checked={promptOptions.noOtherFiles} on:change={generateContextPrompt} />
                <span>Only modify listed files</span>
              </label>
              <label class="option-item">
                <input type="checkbox" bind:checked={promptOptions.preserveStyle} on:change={generateContextPrompt} />
                <span>Preserve code style</span>
              </label>
              <label class="option-item">
                <input type="checkbox" bind:checked={promptOptions.keepItSimple} on:change={generateContextPrompt} />
                <span>Keep it simple</span>
              </label>
              <label class="option-item">
                <input type="checkbox" bind:checked={promptOptions.noNewDeps} on:change={generateContextPrompt} />
                <span>No new dependencies</span>
              </label>
              <label class="option-item">
                <input type="checkbox" bind:checked={promptOptions.addTests} on:change={generateContextPrompt} />
                <span>Add/update tests</span>
              </label>
              <label class="option-item">
                <input type="checkbox" bind:checked={promptOptions.explainChanges} on:change={generateContextPrompt} />
                <span>Explain changes</span>
              </label>
            </div>
          {/if}
        </div>
      </div>

      <!-- Generated prompt preview -->
      <div class="prompt-preview-section">
        <div class="preview-label">Generated prompt</div>
        <pre class="prompt-preview">{generatedPrompt || 'Enter a task to generate prompt...'}</pre>
      </div>
    </div>
    <div class="modal-footer">
      <button class="action-btn" on:click={() => showPromptBuilder = false}>
        Cancel
      </button>
      <button class="action-btn primary" on:click={handleCopyContextPrompt} disabled={!generatedPrompt}>
        Copy Prompt
      </button>
    </div>
  </div>
{/if}

<!-- Save Modal -->
{#if showSaveModal}
  <div class="modal-backdrop" on:click={() => showSaveModal = false}>
    <div class="modal large" on:click|stopPropagation>
      <div class="modal-header">
        <h4>Save Architecture</h4>
        <button class="close-btn" on:click={() => showSaveModal = false}>X</button>
      </div>
      <div class="modal-body">
        <p class="modal-instructions">
          Paste the AI-generated JSON architecture below:
        </p>
        <textarea
          class="save-textarea"
          bind:value={saveContent}
          placeholder="Paste the JSON architecture here..."
          rows="20"
        ></textarea>
      </div>
      <div class="modal-footer">
        <button
          class="action-btn primary"
          on:click={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Architecture'}
        </button>
        <button class="action-btn" on:click={() => showSaveModal = false}>
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .architecture-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .architecture-panel {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 95%;
    max-width: 1400px;
    height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
  }

  .panel-header {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 16px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 2px;
  }

  .close-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .panel-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .tab-header {
    padding: 12px 20px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
  }

  .tab-description {
    margin: 0;
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .tab-actions {
    display: flex;
    gap: 8px;
  }

  .action-btn {
    padding: 8px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 1px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .action-btn.primary {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: var(--bg-primary);
  }

  .action-btn.primary:hover {
    opacity: 0.9;
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .content-layout {
    flex: 1;
    display: grid;
    grid-template-columns: 220px 1fr;
    overflow: hidden;
  }

  .history-panel {
    border-right: 1px solid var(--border-primary);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .history-header {
    padding: 10px 16px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-secondary);
    flex-shrink: 0;
  }

  .history-list {
    flex: 1;
    overflow-y: auto;
  }

  .history-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px 16px;
    border: none;
    border-bottom: 1px solid var(--border-secondary);
    background: transparent;
    cursor: pointer;
    text-align: left;
    width: 100%;
    position: relative;
    transition: all 0.15s;
  }

  .history-item:hover {
    background: var(--bg-hover);
  }

  .history-item.selected {
    background: var(--bg-secondary);
    border-left: 3px solid var(--accent-primary);
    padding-left: 13px;
  }

  .history-date {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .history-preview {
    font-size: 10px;
    color: var(--text-tertiary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 24px;
  }

  .history-item .delete-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    padding: 4px 8px;
    font-size: 10px;
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    opacity: 0;
    transition: all 0.15s;
  }

  .history-item:hover .delete-btn {
    opacity: 1;
  }

  .history-item .delete-btn:hover {
    color: #ff6b6b;
  }

  .content-panel {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* Structured View */
  .structured-view {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }

  .section-tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid var(--border-primary);
    background: var(--bg-secondary);
    flex-shrink: 0;
    overflow-x: auto;
  }

  .section-tab {
    padding: 10px 16px;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    transition: all 0.15s;
  }

  .section-tab:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
  }

  .section-tab.active {
    color: var(--text-primary);
    border-bottom-color: var(--accent-primary);
  }

  .section-tab .count {
    background: var(--bg-primary);
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 9px;
  }

  .section-tab.active .count {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .section-content {
    flex: 1;
    overflow: auto;
    padding: 20px;
  }

  /* Overview Section */
  .overview-section h2 {
    margin: 0 0 8px;
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .version {
    display: inline-block;
    padding: 2px 8px;
    background: var(--bg-secondary);
    border-radius: 2px;
    font-size: 11px;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }

  .overview-section .description {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 24px;
  }

  .overview-stats {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 24px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .stat-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-top: 4px;
  }

  /* Tech Stack Section */
  .tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px;
  }

  .tech-card {
    display: flex;
    gap: 12px;
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
  }

  .tech-icon {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-primary);
    color: var(--bg-primary);
    font-weight: 600;
    border-radius: 2px;
    flex-shrink: 0;
  }

  .tech-info {
    flex: 1;
    min-width: 0;
  }

  .tech-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .tech-version {
    font-size: 11px;
    color: var(--text-tertiary);
    margin-left: 6px;
  }

  .tech-category {
    font-size: 10px;
    text-transform: uppercase;
    color: var(--text-tertiary);
    letter-spacing: 0.5px;
  }

  .tech-purpose {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 4px;
  }

  /* Endpoints Section */
  .endpoints-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .endpoint-card {
    padding: 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
  }

  .endpoint-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .method {
    padding: 4px 8px;
    font-size: 10px;
    font-weight: 700;
    color: white;
    border-radius: 2px;
  }

  .path {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: var(--text-primary);
  }

  .auth-badge {
    padding: 2px 6px;
    font-size: 9px;
    font-weight: 600;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    color: var(--text-tertiary);
    border-radius: 2px;
  }

  .endpoint-description {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }

  .endpoint-params {
    margin-bottom: 12px;
  }

  .params-label, .response-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-tertiary);
    margin-bottom: 6px;
  }

  .param {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
    font-size: 11px;
  }

  .param-name {
    font-family: 'Courier New', monospace;
    color: var(--text-primary);
  }

  .param-type {
    color: var(--accent-primary);
  }

  .param-location {
    padding: 1px 6px;
    background: var(--bg-primary);
    border-radius: 2px;
    color: var(--text-tertiary);
    font-size: 10px;
  }

  .param-optional {
    color: var(--text-tertiary);
    font-style: italic;
  }

  .endpoint-response {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .response-type {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: var(--accent-primary);
  }

  .endpoint-tags {
    display: flex;
    gap: 6px;
  }

  .tag {
    padding: 2px 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    font-size: 10px;
    color: var(--text-secondary);
  }

  /* Entities & Tables Section */
  .entities-list, .tables-list, .ui-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .entity-card, .table-card, .ui-card {
    padding: 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
  }

  .entity-header, .table-header, .ui-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .entity-name, .table-name, .ui-name {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .entity-path, .ui-path {
    font-family: 'Courier New', monospace;
    font-size: 11px;
    color: var(--text-tertiary);
  }

  .entity-description, .table-description, .ui-description {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 16px;
  }

  .fields-table, .columns-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    margin-bottom: 12px;
  }

  .fields-table th, .columns-table th {
    text-align: left;
    padding: 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .fields-table td, .columns-table td {
    padding: 8px;
    border: 1px solid var(--border-primary);
    color: var(--text-primary);
  }

  .field-name, .col-name {
    font-family: 'Courier New', monospace;
  }

  .field-type, .col-type {
    color: var(--accent-primary);
  }

  .optional {
    color: var(--text-tertiary);
  }

  .pk, .fk, .unique {
    padding: 1px 4px;
    font-size: 9px;
    font-weight: 600;
    border-radius: 2px;
    margin-left: 4px;
  }

  .pk {
    background: #fca130;
    color: white;
  }

  .fk {
    background: #61affe;
    color: white;
  }

  .unique {
    background: #49cc90;
    color: white;
  }

  .entity-relationships, .table-indexes {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .rel-label, .idx-label, .routes-label, .props-label, .children-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-tertiary);
  }

  .relationship, .index, .route, .prop, .child {
    padding: 4px 8px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    font-size: 11px;
    color: var(--text-secondary);
  }

  /* UI Section */
  .ui-type {
    padding: 2px 8px;
    background: var(--accent-primary);
    color: var(--bg-primary);
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    border-radius: 2px;
  }

  .ui-routes, .ui-props, .ui-children {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 8px;
  }

  /* Notes Section */
  .notes-list {
    margin: 0;
    padding: 0 0 0 20px;
  }

  .notes-list li {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.8;
    margin-bottom: 8px;
  }

  /* Plain Text View */
  .plain-view {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .content-header {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--bg-secondary);
    flex-shrink: 0;
  }

  .content-date {
    font-size: 11px;
    color: var(--text-secondary);
  }

  .copy-btn {
    padding: 4px 12px;
    background: transparent;
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-radius: 1px;
    cursor: pointer;
  }

  .copy-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .parse-warning {
    padding: 8px 16px;
    background: #fef3cd;
    color: #856404;
    font-size: 11px;
  }

  :global([data-theme="dark"]) .parse-warning {
    background: #3d3200;
    color: #ffc107;
  }

  .content-body {
    flex: 1;
    overflow: auto;
    padding: 16px;
  }

  .content-body pre {
    margin: 0;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .empty-section {
    padding: 40px;
    text-align: center;
    color: var(--text-tertiary);
    font-size: 13px;
  }

  .empty-history,
  .empty-content,
  .loading,
  .loading-small {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 32px;
    color: var(--text-tertiary);
    gap: 8px;
  }

  .empty-history p,
  .empty-content p {
    margin: 0;
    font-size: 12px;
  }

  .hint {
    font-size: 11px !important;
    opacity: 0.7;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 2px solid var(--border-secondary);
    border-top-color: var(--text-secondary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .spinner-small {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border-secondary);
    border-top-color: var(--text-secondary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Modal Styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }

  .modal {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    box-shadow: var(--shadow-large);
  }

  .modal.large {
    max-width: 1000px;
    max-height: 90vh;
  }

  .modal-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-primary);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h4 {
    margin: 0;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .modal-body {
    flex: 1;
    padding: 20px;
    overflow: auto;
  }

  .modal-instructions {
    margin: 0 0 16px;
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .prompt-content {
    background: var(--bg-secondary);
    padding: 16px;
    border-radius: 2px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 500px;
    overflow: auto;
  }

  .save-textarea {
    width: 100%;
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 2px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    resize: vertical;
  }

  .save-textarea:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .modal-footer {
    padding: 16px 20px;
    border-top: 1px solid var(--border-primary);
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  @media (max-width: 768px) {
    .content-layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
    }

    .history-panel {
      border-right: none;
      border-bottom: 1px solid var(--border-primary);
      max-height: 150px;
    }

    .section-tabs {
      flex-wrap: nowrap;
    }

    .overview-stats {
      gap: 12px;
    }

    .stat {
      padding: 12px 16px;
    }

    .tech-grid {
      grid-template-columns: 1fr;
    }
  }

  /* View Mode Toggle */
  .view-mode-toggle {
    display: flex;
    gap: 16px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-primary);
  }

  .view-mode-btn {
    padding: 6px 0;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-tertiary);
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-mode-btn:hover {
    color: var(--text-secondary);
  }

  .view-mode-btn.active {
    color: var(--text-primary);
    border-bottom-color: var(--text-primary);
  }

  /* Flow View */
  .flow-view {
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
    min-height: 500px;
  }

  .flow-view :global(.svelte-flow) {
    flex: 1;
    background: var(--bg-secondary) !important;
  }

  .flow-view :global(.svelte-flow__controls) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
  }

  .flow-view :global(.svelte-flow__controls button) {
    background: var(--bg-primary) !important;
    border-bottom: 1px solid var(--border-secondary) !important;
    color: var(--text-secondary) !important;
  }

  .flow-view :global(.svelte-flow__controls button:hover) {
    background: var(--bg-hover) !important;
  }

  .flow-view :global(.svelte-flow__minimap) {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-primary) !important;
    box-shadow: var(--shadow-medium) !important;
  }

  .flow-legend {
    display: flex;
    gap: 16px;
    padding: 12px 16px;
    background: var(--bg-primary);
    border-top: 1px solid var(--border-secondary);
    flex-shrink: 0;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-secondary);
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 3px;
  }

  .empty-flow {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary);
    gap: 8px;
    padding: 40px;
    text-align: center;
  }

  .empty-flow p {
    margin: 0;
  }

  .empty-flow .hint {
    font-size: 12px;
    opacity: 0.7;
  }

  /* Chip Flow View */
  .chip-flow-view {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: auto;
    padding: 24px;
    background: var(--bg-secondary);
  }

  .chip-flow-container {
    display: flex;
    align-items: flex-start;
    gap: 0;
    overflow-x: auto;
    padding-bottom: 16px;
  }

  .arch-chip {
    min-width: 220px;
    max-width: 280px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
    box-shadow: var(--shadow-small);
  }

  .chip-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-secondary);
  }

  .chip-icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    border-radius: 4px;
    flex-shrink: 0;
  }

  .ui-chip .chip-icon {
    background: #00bcd4;
    color: white;
  }

  .api-chip .chip-icon {
    background: #2196f3;
    color: white;
  }

  .entity-chip .chip-icon {
    background: #4caf50;
    color: white;
  }

  .db-chip .chip-icon {
    background: #ff9800;
    color: white;
  }

  .chip-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
    flex: 1;
  }

  .chip-count {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    background: var(--bg-primary);
    border-radius: 10px;
    color: var(--text-secondary);
  }

  .chip-items {
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: 400px;
    overflow-y: auto;
  }

  .chip-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    background: var(--bg-secondary);
    border-radius: 4px;
    font-size: 11px;
    transition: background 0.15s;
  }

  .chip-item:hover {
    background: var(--bg-hover);
  }

  .item-name {
    color: var(--text-primary);
    font-weight: 500;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .item-badge {
    font-size: 9px;
    padding: 2px 6px;
    background: var(--accent-primary);
    color: var(--bg-primary);
    border-radius: 2px;
    text-transform: uppercase;
    font-weight: 600;
  }

  .item-method {
    font-size: 8px;
    padding: 2px 5px;
    color: white;
    border-radius: 2px;
    font-weight: 700;
    flex-shrink: 0;
  }

  .item-path {
    font-family: 'Courier New', monospace;
    font-size: 10px;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .item-meta {
    font-size: 9px;
    color: var(--text-tertiary);
    flex-shrink: 0;
  }

  /* Chip Connector */
  .chip-connector {
    display: flex;
    align-items: center;
    padding: 0 4px;
    flex-shrink: 0;
  }

  .connector-line {
    width: 24px;
    height: 2px;
    background: var(--border-primary);
  }

  .connector-arrow {
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
    border-left: 8px solid var(--border-primary);
  }

  /* SvelteFlow Chip View */
  .svelteflow-view {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
    position: relative;
  }

  .svelteflow-view :global(.svelte-flow) {
    flex: 1;
    background: var(--bg-secondary);
  }

  .svelteflow-view :global(.svelte-flow__background) {
    background: var(--bg-secondary);
  }

  .svelteflow-view :global(.svelte-flow__background pattern circle) {
    fill: var(--border-secondary);
  }

  .svelteflow-view :global(.svelte-flow__controls) {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    box-shadow: var(--shadow-small);
  }

  .svelteflow-view :global(.svelte-flow__controls button) {
    background: var(--bg-primary);
    border: none;
    border-bottom: 1px solid var(--border-secondary);
    color: var(--text-secondary);
  }

  .svelteflow-view :global(.svelte-flow__controls button:hover) {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .svelteflow-view :global(.svelte-flow__controls button:last-child) {
    border-bottom: none;
  }

  .svelteflow-view :global(.svelte-flow__minimap) {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
  }

  .svelteflow-view :global(.svelte-flow__edge-path) {
    stroke: var(--border-primary);
    stroke-width: 2px;
  }

  .svelteflow-view :global(.svelte-flow__edge.animated path) {
    stroke-dasharray: 5;
    animation: dash 0.5s linear infinite;
  }

  @keyframes dash {
    to {
      stroke-dashoffset: -10;
    }
  }

  .empty-flow {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-tertiary);
    padding: 48px;
  }

  .empty-flow p {
    margin: 4px 0;
    font-size: 13px;
  }

  .empty-flow .hint {
    font-size: 11px;
    opacity: 0.7;
  }

  /* Tech Stack Bar */
  .tech-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    padding: 16px 0 0;
    border-top: 1px solid var(--border-secondary);
    margin-top: 16px;
  }

  .tech-bar-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .tech-tag {
    font-size: 10px;
    padding: 4px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 12px;
    color: var(--text-secondary);
  }

  .tech-tag.lang {
    border-color: #c678dd;
    color: #c678dd;  /* vim magenta */
  }

  .tech-tag.framework {
    border-color: #61afef;
    color: #61afef;  /* vim blue */
  }

  .tech-tag.database {
    border-color: #e5c07b;
    color: #e5c07b;  /* vim yellow */
  }

  /* Raw View */
  .raw-view {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .raw-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    display: flex;
    justify-content: flex-end;
    background: var(--bg-secondary);
    flex-shrink: 0;
  }

  .raw-content {
    flex: 1;
    margin: 0;
    padding: 16px;
    overflow: auto;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-primary);
    background: var(--bg-primary);
    white-space: pre;
    tab-size: 2;
  }

  /* Inline Mode */
  .architecture-inline {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-primary);
  }

  .architecture-inline .panel-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .architecture-inline .content-layout {
    flex: 1;
    overflow: hidden;
  }

  .architecture-inline .tab-header {
    border-bottom: 1px solid var(--border-primary);
  }

  /* Selection Bar */
  .selection-bar {
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    padding: 10px 16px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
    z-index: 1000;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }

  .selection-count {
    font-size: 12px;
    color: var(--text-secondary);
    padding-right: 12px;
    border-right: 1px solid var(--border-secondary);
  }

  .selection-action {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: var(--accent-primary);
    border: none;
    border-radius: 2px;
    color: var(--bg-primary);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .selection-action:hover {
    opacity: 0.85;
  }

  .selection-action.secondary {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
  }

  .selection-action.secondary:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .selection-action svg {
    flex-shrink: 0;
  }

  /* Make selection more visible */
  .svelteflow-view :global(.svelte-flow__node.selected) {
    box-shadow: 0 0 0 3px #61afef !important;
    outline: 2px solid #61afef !important;
    outline-offset: 2px !important;
  }

  .svelteflow-view :global(.svelte-flow__selection) {
    background: rgba(97, 175, 239, 0.2) !important;
    border: 2px dashed #61afef !important;
  }

  .svelteflow-view :global(.svelte-flow__nodesselection-rect) {
    background: rgba(97, 175, 239, 0.1) !important;
    border: 2px solid #61afef !important;
  }

  /* Prompt Builder Modal */
  .modal.prompt-builder {
    max-width: 500px;
    width: 500px;
    transition: box-shadow 0.15s ease;
  }

  .modal.prompt-builder .modal-body {
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .modal.prompt-builder.floating {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    height: 100vh;
    max-height: 100vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }

  .modal.prompt-builder.dragging {
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
    user-select: none;
  }

  .modal-header.draggable {
    cursor: grab;
  }

  .modal-header.draggable:active {
    cursor: grabbing;
  }

  .context-summary.compact {
    padding: 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
  }

  .task-row {
    display: flex;
    gap: 8px;
    align-items: flex-start;
  }

  .task-input {
    flex: 1;
    min-height: 50px;
    resize: vertical;
  }

  .constraints-wrapper {
    position: relative;
  }

  .constraints-btn {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .constraints-btn:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .constraints-btn.has-constraints {
    border-color: var(--accent-primary);
    color: var(--accent-primary);
  }

  .constraints-popup {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 4px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    padding: 12px;
    min-width: 200px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    z-index: 10;
  }

  .constraints-popup-header {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .constraints-popup .option-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px 0;
  }

  .prompt-preview-section {
    display: flex;
    flex-direction: column;
    background: var(--bg-secondary);
    border-radius: 4px;
    overflow: hidden;
    flex: 1;
    min-height: 100px;
  }

  .prompt-preview-section .prompt-preview {
    flex: 1;
    overflow: auto;
  }

  .context-summary {
    background: var(--bg-secondary);
    border-radius: 4px;
    padding: 12px;
  }

  .context-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 10px;
  }

  .context-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .context-chip {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    font-size: 11px;
  }

  .context-chip.page { border-color: #56b6c2; }
  .context-chip.component { border-color: #c678dd; }
  .context-chip.endpoint { border-color: #61afef; }
  .context-chip.entity { border-color: #98c379; }
  .context-chip.table { border-color: #e5c07b; }

  .chip-type {
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-tertiary);
  }

  .chip-name {
    color: var(--text-primary);
    font-weight: 500;
  }

  .instruction-section {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .instruction-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .instruction-input {
    flex: 1;
    min-height: 120px;
    padding: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    font-size: 13px;
    color: var(--text-primary);
    resize: none;
    font-family: inherit;
  }

  .instruction-input:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .instruction-input::placeholder {
    color: var(--text-tertiary);
  }

  .preview-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    padding: 10px 12px;
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-primary);
  }

  .prompt-preview {
    flex: 1;
    margin: 0;
    padding: 12px;
    font-family: 'SF Mono', Monaco, 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.5;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
    overflow: auto;
  }

  /* Prompt sections */
  .prompt-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .section-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .label-hint {
    font-weight: 400;
    color: var(--text-tertiary);
    font-size: 11px;
  }

  .prompt-textarea {
    padding: 10px 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    font-size: 13px;
    color: var(--text-primary);
    resize: none;
    font-family: inherit;
    line-height: 1.4;
  }

  .prompt-textarea:focus {
    outline: none;
    border-color: var(--accent-primary);
  }

  .prompt-textarea::placeholder {
    color: var(--text-tertiary);
  }

  .task-section {
    flex: 1;
  }

  .task-textarea {
    flex: 1;
    min-height: 100px;
  }

  /* Options grid */
  .prompt-options {
    background: var(--bg-secondary);
    border-radius: 4px;
    padding: 12px;
  }

  .options-label {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 10px;
  }

  .options-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .option-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px 0;
  }

  .option-item:hover {
    color: var(--text-primary);
  }

  .option-item input[type="checkbox"] {
    width: 14px;
    height: 14px;
    accent-color: var(--accent-primary);
    cursor: pointer;
  }

  .option-item span {
    user-select: none;
  }

  @media (max-width: 768px) {
    .prompt-builder-layout {
      grid-template-columns: 1fr;
    }

    .prompt-builder-right {
      min-height: 200px;
    }
  }
</style>
