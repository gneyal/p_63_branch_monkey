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
  import ArchitectureNode from './ArchitectureNode.svelte';

  export let onClose = () => {};

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
  let viewMode = 'list'; // 'list' or 'flow'

  const nodes = writable([]);
  const edges = writable([]);

  const nodeTypes = {
    architecture: ArchitectureNode
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

    // Layout configuration
    const columnWidth = 350;
    const rowHeight = 120;
    const startY = 50;

    // Column positions for each type
    const columns = {
      ui: 0,        // Left column - UI components
      endpoint: 1,  // Second column - API endpoints
      entity: 2,    // Third column - Entities
      table: 3,     // Fourth column - Database tables
    };

    // Track y position for each column
    const columnYPositions = { ui: startY, endpoint: startY, entity: startY, table: startY };

    // Create UI component nodes
    if (arch.ui_components?.length > 0) {
      arch.ui_components.forEach((comp, i) => {
        const id = comp.id || `ui_${comp.name?.toLowerCase().replace(/\s+/g, '_') || i}`;
        newNodes.push({
          id,
          type: 'architecture',
          position: { x: columns.ui * columnWidth, y: columnYPositions.ui },
          data: {
            nodeType: 'ui',
            name: comp.name,
            description: comp.description,
            type: comp.type,
            file_path: comp.file_path,
            props: comp.props,
            connects_to: comp.connects_to || []
          }
        });
        columnYPositions.ui += rowHeight;

        // Create edges for UI connections
        if (comp.connects_to) {
          comp.connects_to.forEach(targetId => {
            newEdges.push({
              id: `${id}-${targetId}`,
              source: id,
              target: targetId,
              type: 'smoothstep',
              animated: false,
              style: 'stroke: #00bcd4; stroke-width: 2px;'
            });
          });
        }
      });
    }

    // Create endpoint nodes
    if (arch.endpoints?.length > 0) {
      arch.endpoints.forEach((ep, i) => {
        const id = ep.id || `ep_${ep.method?.toLowerCase()}_${ep.path?.replace(/\//g, '_') || i}`;
        newNodes.push({
          id,
          type: 'architecture',
          position: { x: columns.endpoint * columnWidth, y: columnYPositions.endpoint },
          data: {
            nodeType: 'endpoint',
            name: ep.path,
            description: ep.description,
            method: ep.method,
            path: ep.path,
            params: ep.params,
            connects_to: ep.connects_to || []
          }
        });
        columnYPositions.endpoint += rowHeight;

        // Create edges for endpoint connections
        if (ep.connects_to) {
          ep.connects_to.forEach(targetId => {
            newEdges.push({
              id: `${id}-${targetId}`,
              source: id,
              target: targetId,
              type: 'smoothstep',
              animated: false,
              style: 'stroke: #2196f3; stroke-width: 2px;'
            });
          });
        }
      });
    }

    // Create entity nodes
    if (arch.entities?.length > 0) {
      arch.entities.forEach((entity, i) => {
        const id = entity.id || `entity_${entity.name?.toLowerCase().replace(/\s+/g, '_') || i}`;
        newNodes.push({
          id,
          type: 'architecture',
          position: { x: columns.entity * columnWidth, y: columnYPositions.entity },
          data: {
            nodeType: 'entity',
            name: entity.name,
            description: entity.description,
            fields: entity.fields,
            relationships: entity.relationships,
            connects_to: entity.connects_to || []
          }
        });
        columnYPositions.entity += rowHeight;

        // Create edges for entity connections
        if (entity.connects_to) {
          entity.connects_to.forEach(targetId => {
            newEdges.push({
              id: `${id}-${targetId}`,
              source: id,
              target: targetId,
              type: 'smoothstep',
              animated: false,
              style: 'stroke: #4caf50; stroke-width: 2px;'
            });
          });
        }
      });
    }

    // Create table nodes
    if (arch.tables?.length > 0) {
      arch.tables.forEach((table, i) => {
        const id = table.id || `table_${table.name?.toLowerCase().replace(/\s+/g, '_') || i}`;
        newNodes.push({
          id,
          type: 'architecture',
          position: { x: columns.table * columnWidth, y: columnYPositions.table },
          data: {
            nodeType: 'table',
            name: table.name,
            description: table.description,
            columns: table.columns,
            indexes: table.indexes,
            connects_to: table.connects_to || []
          }
        });
        columnYPositions.table += rowHeight;

        // Create edges for table connections
        if (table.connects_to) {
          table.connects_to.forEach(targetId => {
            newEdges.push({
              id: `${id}-${targetId}`,
              source: id,
              target: targetId,
              type: 'smoothstep',
              animated: false,
              style: 'stroke: #ff9800; stroke-width: 2px;'
            });
          });
        }
      });
    }

    nodes.set(newNodes);
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
      showToast('Invalid JSON format. Please check your input.', 'error');
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
</script>

<div class="architecture-backdrop" on:click={onClose}>
  <div class="architecture-panel" on:click|stopPropagation>
    <div class="panel-header">
      <h3>Architecture</h3>
      <button class="close-btn" on:click={onClose}>X</button>
    </div>

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
                    List View
                  </button>
                  <button
                    class="view-mode-btn"
                    class:active={viewMode === 'flow'}
                    on:click={() => viewMode = 'flow'}
                  >
                    Flow View
                  </button>
                </div>

                {#if viewMode === 'flow'}
                  <!-- Flow View -->
                  <div class="flow-view">
                    {#if $nodes.length > 0}
                      <SvelteFlow
                        nodes={$nodes}
                        edges={$edges}
                        {nodeTypes}
                        fitView
                        nodesDraggable={true}
                        nodesConnectable={false}
                        elementsSelectable={true}
                        panOnDrag={true}
                        zoomOnScroll={true}
                        zoomOnPinch={true}
                        zoomOnDoubleClick={true}
                        minZoom={0.2}
                        maxZoom={2}
                        defaultZoom={0.8}
                      >
                        <Controls showZoom={true} showFitView={true} showInteractive={false} />
                        <Background variant={BackgroundVariant.Dots} />
                        <MiniMap />
                      </SvelteFlow>
                      <div class="flow-legend">
                        <span class="legend-item"><span class="legend-color" style="background: #00bcd4;"></span> UI Components</span>
                        <span class="legend-item"><span class="legend-color" style="background: #2196f3;"></span> Endpoints</span>
                        <span class="legend-item"><span class="legend-color" style="background: #4caf50;"></span> Entities</span>
                        <span class="legend-item"><span class="legend-color" style="background: #ff9800;"></span> Tables</span>
                      </div>
                    {:else}
                      <div class="empty-flow">
                        <p>No flow data available.</p>
                        <p class="hint">Generate new architecture with the updated prompt to include flow connections.</p>
                      </div>
                    {/if}
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
    gap: 4px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-primary);
  }

  .view-mode-btn {
    padding: 8px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-secondary);
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.15s;
  }

  .view-mode-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .view-mode-btn.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    color: white;
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
</style>
