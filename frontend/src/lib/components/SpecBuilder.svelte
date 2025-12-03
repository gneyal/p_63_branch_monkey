<script>
  import { onMount, tick } from 'svelte';
  import Topbar from './Topbar.svelte';

  // Conversation state
  let messages = [];
  let currentInput = '';
  let isTyping = false;
  let chatContainer;

  // Spec being built
  let spec = {
    title: '',
    summary: '',
    type: null, // 'feature', 'bugfix', 'refactor', 'infrastructure'
    scope: null, // 'frontend', 'backend', 'fullstack', 'database', 'api'
    size: null, // 'small', 'medium', 'large'
    hasAuth: false,
    hasDatabase: false,
    hasApi: false,
    hasUi: false,
    users: [],
    requirements: [],
    outOfScope: [],
    techNotes: [],
    risks: [],
  };

  // Question flow state
  let currentQuestion = 'start';
  let questionHistory = [];

  // Saved specs
  let savedSpecs = [];
  let showSavedSpecs = false;

  // Question definitions with smart branching
  const questions = {
    start: {
      text: "What do you want to build?",
      type: 'text',
      placeholder: "Describe your idea in a sentence or two...",
      next: analyzeInitialInput,
    },
    confirmType: {
      text: "Got it. This sounds like a {type}. Is that right?",
      type: 'choice',
      options: [
        { label: 'Yes', value: true },
        { label: 'No, let me clarify', value: false },
      ],
      next: (answer) => answer ? 'scopeQuestion' : 'clarifyType',
    },
    clarifyType: {
      text: "What kind of change is this?",
      type: 'choice',
      options: [
        { label: 'New feature', value: 'feature' },
        { label: 'Bug fix', value: 'bugfix' },
        { label: 'Refactor/cleanup', value: 'refactor' },
        { label: 'Infrastructure/tooling', value: 'infrastructure' },
      ],
      next: (answer) => {
        spec.type = answer;
        return 'scopeQuestion';
      },
    },
    scopeQuestion: {
      text: "What parts of the system does this touch?",
      type: 'multi',
      options: [
        { label: 'User interface', value: 'ui' },
        { label: 'API/Backend logic', value: 'api' },
        { label: 'Database', value: 'database' },
        { label: 'External services', value: 'external' },
      ],
      next: (answers) => {
        spec.hasUi = answers.includes('ui');
        spec.hasApi = answers.includes('api');
        spec.hasDatabase = answers.includes('database');

        // Determine scope
        if (answers.includes('ui') && (answers.includes('api') || answers.includes('database'))) {
          spec.scope = 'fullstack';
        } else if (answers.includes('ui')) {
          spec.scope = 'frontend';
        } else if (answers.includes('database') && !answers.includes('api')) {
          spec.scope = 'database';
        } else if (answers.includes('api')) {
          spec.scope = 'backend';
        }

        return 'sizeQuestion';
      },
    },
    sizeQuestion: {
      text: "How big of a change is this?",
      type: 'choice',
      options: [
        { label: 'Small (< 1 day)', value: 'small', desc: 'Quick fix or minor tweak' },
        { label: 'Medium (few days)', value: 'medium', desc: 'Solid chunk of work' },
        { label: 'Large (1+ week)', value: 'large', desc: 'Major feature or overhaul' },
      ],
      next: (answer) => {
        spec.size = answer;
        return spec.hasUi ? 'usersQuestion' : 'requirementsQuestion';
      },
    },
    usersQuestion: {
      text: "Who will use this?",
      type: 'multi',
      options: [
        { label: 'All users', value: 'all' },
        { label: 'Admin users', value: 'admin' },
        { label: 'New users', value: 'new' },
        { label: 'Power users', value: 'power' },
        { label: 'Internal team', value: 'internal' },
      ],
      next: (answers) => {
        spec.users = answers;
        return 'authQuestion';
      },
    },
    authQuestion: {
      text: "Does this need special permissions or authentication?",
      type: 'choice',
      options: [
        { label: 'No, available to everyone', value: 'none' },
        { label: 'Yes, logged-in users only', value: 'auth' },
        { label: 'Yes, specific roles/permissions', value: 'roles' },
      ],
      next: (answer) => {
        spec.hasAuth = answer !== 'none';
        if (answer === 'roles') {
          return 'rolesQuestion';
        }
        return 'requirementsQuestion';
      },
    },
    rolesQuestion: {
      text: "Which roles should have access?",
      type: 'text',
      placeholder: "e.g., admin, editor, viewer...",
      next: (answer) => {
        spec.techNotes.push(`Access: ${answer}`);
        return 'requirementsQuestion';
      },
    },
    requirementsQuestion: {
      text: "What are the must-have requirements? (one per line)",
      type: 'textarea',
      placeholder: "- Must do X\n- Should handle Y\n- Needs to show Z",
      next: (answer) => {
        spec.requirements = answer.split('\n').filter(r => r.trim()).map(r => r.replace(/^[-•]\s*/, ''));
        return spec.hasDatabase ? 'dataQuestion' : (spec.hasApi ? 'apiQuestion' : 'edgeCasesQuestion');
      },
    },
    dataQuestion: {
      text: "What data changes are needed?",
      type: 'choice',
      options: [
        { label: 'New tables/collections', value: 'new' },
        { label: 'Modify existing schema', value: 'modify' },
        { label: 'Just reading data', value: 'read' },
        { label: 'Not sure yet', value: 'unsure' },
      ],
      next: (answer) => {
        if (answer === 'new' || answer === 'modify') {
          spec.techNotes.push(`Database: ${answer === 'new' ? 'New schema needed' : 'Schema migration needed'}`);
          return 'dataDetailsQuestion';
        }
        return spec.hasApi ? 'apiQuestion' : 'edgeCasesQuestion';
      },
    },
    dataDetailsQuestion: {
      text: "Briefly describe the data model:",
      type: 'text',
      placeholder: "e.g., User has many Posts, Post has tags...",
      next: (answer) => {
        spec.techNotes.push(`Data model: ${answer}`);
        return spec.hasApi ? 'apiQuestion' : 'edgeCasesQuestion';
      },
    },
    apiQuestion: {
      text: "What API changes are needed?",
      type: 'choice',
      options: [
        { label: 'New endpoints', value: 'new' },
        { label: 'Modify existing endpoints', value: 'modify' },
        { label: 'No API changes', value: 'none' },
      ],
      next: (answer) => {
        if (answer !== 'none') {
          spec.techNotes.push(`API: ${answer === 'new' ? 'New endpoints needed' : 'Endpoint modifications needed'}`);
        }
        return 'edgeCasesQuestion';
      },
    },
    edgeCasesQuestion: {
      text: "Any edge cases or error scenarios to handle?",
      type: 'text',
      placeholder: "e.g., What if user has no data? Network fails?",
      optional: true,
      next: (answer) => {
        if (answer.trim()) {
          spec.risks.push(answer);
        }
        return 'outOfScopeQuestion';
      },
    },
    outOfScopeQuestion: {
      text: "Anything explicitly OUT of scope?",
      type: 'text',
      placeholder: "e.g., Mobile support, internationalization...",
      optional: true,
      next: (answer) => {
        if (answer.trim()) {
          spec.outOfScope = answer.split(',').map(s => s.trim()).filter(s => s);
        }
        return 'anythingElseQuestion';
      },
    },
    anythingElseQuestion: {
      text: "Anything else important to note?",
      type: 'text',
      placeholder: "Dependencies, deadlines, concerns...",
      optional: true,
      next: (answer) => {
        if (answer.trim()) {
          spec.techNotes.push(answer);
        }
        return 'complete';
      },
    },
    complete: {
      text: "Your spec is ready! You can copy it or save it for later.",
      type: 'complete',
    },
  };

  // Analyze initial input to detect type and extract info
  function analyzeInitialInput(input) {
    const lower = input.toLowerCase();
    spec.summary = input;

    // Extract title (first sentence or up to 50 chars)
    spec.title = input.split(/[.!?]/)[0].slice(0, 60);
    if (spec.title.length < input.length) spec.title += '...';

    // Detect type
    if (lower.includes('fix') || lower.includes('bug') || lower.includes('broken') || lower.includes('error') || lower.includes('issue')) {
      spec.type = 'bugfix';
    } else if (lower.includes('refactor') || lower.includes('clean') || lower.includes('improve') || lower.includes('optimize')) {
      spec.type = 'refactor';
    } else if (lower.includes('deploy') || lower.includes('ci') || lower.includes('infrastructure') || lower.includes('pipeline')) {
      spec.type = 'infrastructure';
    } else {
      spec.type = 'feature';
    }

    // Detect scope hints
    if (lower.includes('button') || lower.includes('page') || lower.includes('ui') || lower.includes('component') || lower.includes('style') || lower.includes('css')) {
      spec.hasUi = true;
    }
    if (lower.includes('api') || lower.includes('endpoint') || lower.includes('server') || lower.includes('backend')) {
      spec.hasApi = true;
    }
    if (lower.includes('database') || lower.includes('table') || lower.includes('schema') || lower.includes('query') || lower.includes('sql')) {
      spec.hasDatabase = true;
    }
    if (lower.includes('auth') || lower.includes('login') || lower.includes('permission') || lower.includes('role') || lower.includes('access')) {
      spec.hasAuth = true;
    }

    const typeLabels = {
      feature: 'new feature',
      bugfix: 'bug fix',
      refactor: 'refactoring task',
      infrastructure: 'infrastructure change',
    };

    return 'confirmType';
  }

  // Add a message to the chat
  function addMessage(role, content, options = null) {
    messages = [...messages, { role, content, options, timestamp: Date.now() }];
    scrollToBottom();
  }

  // Scroll chat to bottom
  async function scrollToBottom() {
    await tick();
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  // Get current question object with dynamic text
  function getCurrentQuestion() {
    const q = questions[currentQuestion];
    if (!q) return null;

    // Replace placeholders in text
    let text = q.text;
    const typeLabels = {
      feature: 'new feature',
      bugfix: 'bug fix',
      refactor: 'refactoring task',
      infrastructure: 'infrastructure change',
    };
    text = text.replace('{type}', typeLabels[spec.type] || spec.type);

    return { ...q, text };
  }

  // Handle user input
  async function handleSubmit() {
    if (!currentInput.trim() && !questions[currentQuestion]?.optional) return;

    const input = currentInput.trim();
    currentInput = '';

    // Add user message
    addMessage('user', input || '(skipped)');

    // Get next question
    const q = questions[currentQuestion];
    if (q && q.next) {
      questionHistory.push(currentQuestion);

      // Simulate thinking
      isTyping = true;
      await new Promise(r => setTimeout(r, 300 + Math.random() * 400));
      isTyping = false;

      const nextQ = q.next(input);
      currentQuestion = nextQ;

      // Add bot message for next question
      const nextQuestion = getCurrentQuestion();
      if (nextQuestion) {
        addMessage('bot', nextQuestion.text, nextQuestion);
      }
    }
  }

  // Handle choice selection
  async function handleChoice(value) {
    const q = questions[currentQuestion];
    const option = q.options.find(o => o.value === value);

    addMessage('user', option?.label || value);

    if (q && q.next) {
      questionHistory.push(currentQuestion);

      isTyping = true;
      await new Promise(r => setTimeout(r, 300 + Math.random() * 400));
      isTyping = false;

      const nextQ = q.next(value);
      currentQuestion = nextQ;

      const nextQuestion = getCurrentQuestion();
      if (nextQuestion) {
        addMessage('bot', nextQuestion.text, nextQuestion);
      }
    }
  }

  // Handle multi-select
  let multiSelectValues = [];

  function toggleMultiSelect(value) {
    if (multiSelectValues.includes(value)) {
      multiSelectValues = multiSelectValues.filter(v => v !== value);
    } else {
      multiSelectValues = [...multiSelectValues, value];
    }
  }

  async function submitMultiSelect() {
    const q = questions[currentQuestion];
    const labels = multiSelectValues.map(v => q.options.find(o => o.value === v)?.label).join(', ');

    addMessage('user', labels || '(none selected)');

    if (q && q.next) {
      questionHistory.push(currentQuestion);

      isTyping = true;
      await new Promise(r => setTimeout(r, 300 + Math.random() * 400));
      isTyping = false;

      const nextQ = q.next(multiSelectValues);
      currentQuestion = nextQ;
      multiSelectValues = [];

      const nextQuestion = getCurrentQuestion();
      if (nextQuestion) {
        addMessage('bot', nextQuestion.text, nextQuestion);
      }
    }
  }

  // Go back to previous question
  function goBack() {
    if (questionHistory.length > 0) {
      currentQuestion = questionHistory.pop();
      messages = messages.slice(0, -2); // Remove last bot + user message
    }
  }

  // Start new spec
  function startNew() {
    spec = {
      title: '',
      summary: '',
      type: null,
      scope: null,
      size: null,
      hasAuth: false,
      hasDatabase: false,
      hasApi: false,
      hasUi: false,
      users: [],
      requirements: [],
      outOfScope: [],
      techNotes: [],
      risks: [],
    };
    messages = [];
    questionHistory = [];
    currentQuestion = 'start';
    multiSelectValues = [];

    // Start with initial question
    const q = getCurrentQuestion();
    addMessage('bot', q.text, q);
  }

  // Generate markdown spec
  function generateMarkdown() {
    let md = `# ${spec.title || 'Untitled Spec'}\n\n`;

    if (spec.summary) {
      md += `## Summary\n${spec.summary}\n\n`;
    }

    // Metadata
    const meta = [];
    if (spec.type) meta.push(`**Type:** ${spec.type}`);
    if (spec.scope) meta.push(`**Scope:** ${spec.scope}`);
    if (spec.size) meta.push(`**Size:** ${spec.size}`);
    if (spec.hasAuth) meta.push(`**Auth required:** Yes`);
    if (meta.length) {
      md += meta.join(' | ') + '\n\n';
    }

    if (spec.users.length) {
      md += `## Target Users\n${spec.users.map(u => `- ${u}`).join('\n')}\n\n`;
    }

    if (spec.requirements.length) {
      md += `## Requirements\n${spec.requirements.map(r => `- ${r}`).join('\n')}\n\n`;
    }

    if (spec.outOfScope.length) {
      md += `## Out of Scope\n${spec.outOfScope.map(r => `- ${r}`).join('\n')}\n\n`;
    }

    if (spec.techNotes.length) {
      md += `## Technical Notes\n${spec.techNotes.map(r => `- ${r}`).join('\n')}\n\n`;
    }

    if (spec.risks.length) {
      md += `## Risks & Edge Cases\n${spec.risks.map(r => `- ${r}`).join('\n')}\n\n`;
    }

    return md;
  }

  // Copy spec to clipboard
  function copySpec() {
    navigator.clipboard.writeText(generateMarkdown());
    copiedSpec = true;
    setTimeout(() => copiedSpec = false, 2000);
  }

  let copiedSpec = false;

  // Save spec
  function saveSpec() {
    const saved = {
      id: crypto.randomUUID(),
      ...spec,
      savedAt: new Date().toISOString(),
    };
    savedSpecs = [saved, ...savedSpecs];
    localStorage.setItem('branchMonkeySpecs', JSON.stringify(savedSpecs));
  }

  // Load saved specs
  function loadSavedSpecs() {
    const stored = localStorage.getItem('branchMonkeySpecs');
    if (stored) {
      savedSpecs = JSON.parse(stored);
    }
  }

  // Load a saved spec
  function loadSpec(saved) {
    spec = { ...saved };
    currentQuestion = 'complete';
    messages = [{ role: 'bot', content: 'Loaded saved spec. You can edit or copy it.', timestamp: Date.now() }];
    showSavedSpecs = false;
  }

  // Delete a saved spec
  function deleteSpec(id) {
    savedSpecs = savedSpecs.filter(s => s.id !== id);
    localStorage.setItem('branchMonkeySpecs', JSON.stringify(savedSpecs));
  }

  onMount(() => {
    loadSavedSpecs();
    startNew();
  });
</script>

<div class="spec-builder-page">
  <Topbar activeView="spec" />

  <div class="spec-builder-content">
    <!-- Chat Interface -->
    <div class="chat-panel">
      <div class="chat-header">
        <h2>Spec Builder</h2>
        <div class="chat-actions">
          <button class="action-btn" on:click={() => showSavedSpecs = !showSavedSpecs}>
            {showSavedSpecs ? 'Hide Saved' : 'Saved Specs'} ({savedSpecs.length})
          </button>
          <button class="action-btn" on:click={startNew}>New Spec</button>
        </div>
      </div>

      {#if showSavedSpecs && savedSpecs.length > 0}
        <div class="saved-specs-panel">
          {#each savedSpecs as saved}
            <div class="saved-spec-item">
              <div class="saved-spec-info" on:click={() => loadSpec(saved)}>
                <span class="saved-spec-title">{saved.title || 'Untitled'}</span>
                <span class="saved-spec-date">{new Date(saved.savedAt).toLocaleDateString()}</span>
              </div>
              <button class="delete-btn" on:click|stopPropagation={() => deleteSpec(saved.id)}>×</button>
            </div>
          {/each}
        </div>
      {/if}

      <div class="chat-messages" bind:this={chatContainer}>
        {#each messages as message}
          <div class="message {message.role}">
            <div class="message-content">
              {message.content}
            </div>
          </div>
        {/each}

        {#if isTyping}
          <div class="message bot">
            <div class="message-content typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Input Area -->
      <div class="chat-input-area">
        {#if currentQuestion !== 'complete'}
          {@const q = getCurrentQuestion()}

          {#if q?.type === 'text'}
            <div class="input-row">
              {#if questionHistory.length > 0}
                <button class="back-btn" on:click={goBack}>←</button>
              {/if}
              <input
                type="text"
                bind:value={currentInput}
                placeholder={q.placeholder || 'Type your answer...'}
                on:keydown={(e) => e.key === 'Enter' && handleSubmit()}
              />
              <button class="send-btn" on:click={handleSubmit} disabled={!currentInput.trim() && !q.optional}>
                {q.optional && !currentInput.trim() ? 'Skip' : 'Send'}
              </button>
            </div>
          {:else if q?.type === 'textarea'}
            <div class="textarea-input">
              {#if questionHistory.length > 0}
                <button class="back-btn" on:click={goBack}>←</button>
              {/if}
              <textarea
                bind:value={currentInput}
                placeholder={q.placeholder}
                rows="4"
              ></textarea>
              <button class="send-btn" on:click={handleSubmit} disabled={!currentInput.trim() && !q.optional}>
                {q.optional && !currentInput.trim() ? 'Skip' : 'Continue'}
              </button>
            </div>
          {:else if q?.type === 'choice'}
            <div class="choice-input">
              {#if questionHistory.length > 0}
                <button class="back-btn standalone" on:click={goBack}>← Back</button>
              {/if}
              <div class="choice-buttons">
                {#each q.options as option}
                  <button class="choice-btn" on:click={() => handleChoice(option.value)}>
                    <span class="choice-label">{option.label}</span>
                    {#if option.desc}<span class="choice-desc">{option.desc}</span>{/if}
                  </button>
                {/each}
              </div>
            </div>
          {:else if q?.type === 'multi'}
            <div class="multi-input">
              {#if questionHistory.length > 0}
                <button class="back-btn standalone" on:click={goBack}>← Back</button>
              {/if}
              <div class="multi-buttons">
                {#each q.options as option}
                  <button
                    class="multi-btn"
                    class:selected={multiSelectValues.includes(option.value)}
                    on:click={() => toggleMultiSelect(option.value)}
                  >
                    {option.label}
                  </button>
                {/each}
              </div>
              <button class="send-btn" on:click={submitMultiSelect}>Continue</button>
            </div>
          {/if}
        {:else}
          <div class="complete-actions">
            <button class="action-btn primary" on:click={copySpec}>
              {copiedSpec ? 'Copied!' : 'Copy Spec'}
            </button>
            <button class="action-btn" on:click={saveSpec}>Save</button>
            <button class="action-btn" on:click={startNew}>Start New</button>
          </div>
        {/if}
      </div>
    </div>

    <!-- Spec Preview -->
    <div class="spec-preview">
      <div class="preview-header">
        <h3>Spec Preview</h3>
        {#if currentQuestion === 'complete'}
          <span class="complete-badge">Complete</span>
        {:else}
          <span class="progress-badge">In progress...</span>
        {/if}
      </div>

      <div class="preview-content">
        {#if spec.title}
          <h2 class="spec-title">{spec.title}</h2>
        {:else}
          <h2 class="spec-title placeholder">Your spec title...</h2>
        {/if}

        {#if spec.summary}
          <p class="spec-summary">{spec.summary}</p>
        {/if}

        <div class="spec-tags">
          {#if spec.type}
            <span class="tag type-{spec.type}">{spec.type}</span>
          {/if}
          {#if spec.scope}
            <span class="tag">{spec.scope}</span>
          {/if}
          {#if spec.size}
            <span class="tag">{spec.size}</span>
          {/if}
          {#if spec.hasAuth}
            <span class="tag auth">auth required</span>
          {/if}
        </div>

        {#if spec.users.length > 0}
          <div class="spec-section">
            <h4>Target Users</h4>
            <ul>
              {#each spec.users as user}
                <li>{user}</li>
              {/each}
            </ul>
          </div>
        {/if}

        {#if spec.requirements.length > 0}
          <div class="spec-section">
            <h4>Requirements</h4>
            <ul>
              {#each spec.requirements as req}
                <li>{req}</li>
              {/each}
            </ul>
          </div>
        {/if}

        {#if spec.outOfScope.length > 0}
          <div class="spec-section">
            <h4>Out of Scope</h4>
            <ul>
              {#each spec.outOfScope as item}
                <li>{item}</li>
              {/each}
            </ul>
          </div>
        {/if}

        {#if spec.techNotes.length > 0}
          <div class="spec-section">
            <h4>Technical Notes</h4>
            <ul>
              {#each spec.techNotes as note}
                <li>{note}</li>
              {/each}
            </ul>
          </div>
        {/if}

        {#if spec.risks.length > 0}
          <div class="spec-section">
            <h4>Risks & Edge Cases</h4>
            <ul>
              {#each spec.risks as risk}
                <li>{risk}</li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .spec-builder-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--bg-primary);
  }

  .spec-builder-content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* Chat Panel */
  .chat-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--border-primary);
    max-width: 600px;
  }

  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .chat-header h2 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .chat-actions {
    display: flex;
    gap: 8px;
  }

  .action-btn {
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .action-btn.primary {
    background: var(--text-tertiary);
    color: var(--bg-primary);
    border-color: var(--text-tertiary);
  }

  .action-btn.primary:hover {
    background: var(--text-secondary);
  }

  /* Saved Specs Panel */
  .saved-specs-panel {
    border-bottom: 1px solid var(--border-secondary);
    max-height: 200px;
    overflow-y: auto;
    background: var(--bg-secondary);
  }

  .saved-spec-item {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    border-bottom: 1px solid var(--border-secondary);
    cursor: pointer;
    transition: background 0.2s;
  }

  .saved-spec-item:hover {
    background: var(--bg-hover);
  }

  .saved-spec-info {
    flex: 1;
  }

  .saved-spec-title {
    display: block;
    font-size: 13px;
    color: var(--text-primary);
  }

  .saved-spec-date {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .delete-btn {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 18px;
    cursor: pointer;
    padding: 4px;
    opacity: 0;
    transition: all 0.2s;
  }

  .saved-spec-item:hover .delete-btn {
    opacity: 1;
  }

  .delete-btn:hover {
    color: var(--text-primary);
  }

  /* Chat Messages */
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .message {
    max-width: 85%;
    animation: messageIn 0.3s ease;
  }

  @keyframes messageIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .message.bot {
    align-self: flex-start;
  }

  .message.user {
    align-self: flex-end;
  }

  .message-content {
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 14px;
    line-height: 1.5;
  }

  .message.bot .message-content {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
  }

  .message.user .message-content {
    background: var(--text-tertiary);
    color: var(--bg-primary);
    border-bottom-right-radius: 4px;
  }

  .typing {
    display: flex;
    gap: 4px;
    padding: 16px 20px;
  }

  .typing span {
    width: 8px;
    height: 8px;
    background: var(--text-tertiary);
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
  }

  .typing span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes typing {
    0%, 80%, 100% {
      transform: scale(0.8);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }

  /* Input Area */
  .chat-input-area {
    padding: 16px 20px;
    border-top: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .input-row {
    display: flex;
    gap: 8px;
  }

  .input-row input {
    flex: 1;
    padding: 12px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 14px;
  }

  .input-row input:focus {
    outline: none;
    border-color: var(--border-hover);
  }

  .textarea-input {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .textarea-input textarea {
    padding: 12px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 14px;
    font-family: inherit;
    resize: none;
  }

  .textarea-input textarea:focus {
    outline: none;
    border-color: var(--border-hover);
  }

  .back-btn {
    padding: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .back-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .back-btn.standalone {
    align-self: flex-start;
    margin-bottom: 8px;
    padding: 8px 12px;
    font-size: 12px;
  }

  .send-btn {
    padding: 12px 20px;
    background: var(--text-tertiary);
    border: none;
    border-radius: 8px;
    color: var(--bg-primary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .send-btn:hover:not(:disabled) {
    background: var(--text-secondary);
  }

  .send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Choice Input */
  .choice-input {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .choice-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .choice-btn {
    flex: 1;
    min-width: 120px;
    padding: 12px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .choice-btn:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  .choice-label {
    font-weight: 500;
  }

  .choice-desc {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  /* Multi Input */
  .multi-input {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .multi-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .multi-btn {
    padding: 10px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 13px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .multi-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .multi-btn.selected {
    background: var(--text-tertiary);
    color: var(--bg-primary);
    border-color: var(--text-tertiary);
  }

  /* Complete Actions */
  .complete-actions {
    display: flex;
    gap: 8px;
    justify-content: center;
  }

  /* Spec Preview */
  .spec-preview {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--bg-secondary);
  }

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border-secondary);
  }

  .preview-header h3 {
    margin: 0;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .complete-badge {
    font-size: 10px;
    font-weight: 500;
    color: var(--bg-primary);
    background: var(--text-tertiary);
    padding: 4px 10px;
    border-radius: 10px;
  }

  .progress-badge {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .preview-content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }

  .spec-title {
    margin: 0 0 12px 0;
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .spec-title.placeholder {
    color: var(--text-tertiary);
    font-style: italic;
  }

  .spec-summary {
    margin: 0 0 16px 0;
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.6;
  }

  .spec-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 24px;
  }

  .tag {
    font-size: 10px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 4px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
  }

  .tag.type-feature {
    border-color: var(--branch-experiment);
    color: var(--branch-experiment);
  }

  .tag.type-bugfix {
    border-color: var(--branch-fix);
    color: var(--branch-fix);
  }

  .tag.type-refactor {
    border-color: var(--branch-main);
    color: var(--branch-main);
  }

  .tag.type-infrastructure {
    border-color: var(--branch-feature);
    color: var(--branch-feature);
  }

  .tag.auth {
    border-color: var(--accent-secondary);
    color: var(--accent-secondary);
  }

  .spec-section {
    margin-bottom: 20px;
  }

  .spec-section h4 {
    margin: 0 0 8px 0;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
  }

  .spec-section ul {
    margin: 0;
    padding-left: 20px;
  }

  .spec-section li {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 4px;
  }
</style>
