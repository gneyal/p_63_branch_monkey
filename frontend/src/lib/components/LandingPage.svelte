<script>
  import { onMount, onDestroy } from 'svelte';
  import { push } from 'svelte-spa-router';

  let scrollY = 0;
  let heroRef;
  let perspective = 45; // degrees
  let rotateX = 12;
  let scale = 0.85;

  // Animation state
  let cursorX = 50;
  let cursorY = 80;
  let activeTab = 'commits';
  let hoveredCommit = -1;
  let selectedCommit = -1;
  let animationFrame = 0;
  let animationInterval;
  let activeProject = 0;
  let showProjectDropdown = false;

  const tabs = ['commits', 'tasks', 'prompts', 'architecture'];

  // Multiple projects with different data
  const projects = [
    {
      name: 'acme-webapp',
      commits: [
        { sha: 'a1b2c3d', msg: 'Add new feature component', branch: 'main', isHead: true },
        { sha: 'e4f5g6h', msg: 'Fix authentication bug', branch: null, isHead: false },
        { sha: 'i7j8k9l', msg: 'Update dependencies', branch: null, isHead: false },
        { sha: 'm0n1o2p', msg: 'Refactor API layer', branch: null, isHead: false }
      ],
      tasks: {
        todo: ['Write API documentation', 'Add unit tests'],
        inProgress: ['Add user settings page'],
        done: ['Implement dark mode']
      },
      prompts: { total: 1247, cost: '$12.47', inputTokens: '892K', outputTokens: '234K' }
    },
    {
      name: 'mobile-app',
      commits: [
        { sha: 'x9y8z7w', msg: 'Implement push notifications', branch: 'develop', isHead: true },
        { sha: 'v6u5t4s', msg: 'Add offline mode support', branch: null, isHead: false },
        { sha: 'r3q2p1o', msg: 'Fix iOS crash on startup', branch: null, isHead: false }
      ],
      tasks: {
        todo: ['Add biometric auth'],
        inProgress: ['Optimize image loading', 'Implement caching'],
        done: ['Setup CI/CD', 'Add analytics']
      },
      prompts: { total: 834, cost: '$8.21', inputTokens: '512K', outputTokens: '156K' }
    },
    {
      name: 'data-pipeline',
      commits: [
        { sha: 'k1l2m3n', msg: 'Add Kafka consumer', branch: 'main', isHead: true },
        { sha: 'o4p5q6r', msg: 'Optimize batch processing', branch: null, isHead: false }
      ],
      tasks: {
        todo: ['Add monitoring dashboard', 'Write docs'],
        inProgress: ['Setup alerting'],
        done: ['Deploy to staging', 'Add retry logic', 'Schema migration']
      },
      prompts: { total: 2156, cost: '$24.89', inputTokens: '1.4M', outputTokens: '389K' }
    }
  ];

  $: currentProject = projects[activeProject];

  // Animation sequence with project switching
  const animationSequence = [
    // Move to first commit and hover
    { duration: 800, action: () => { cursorX = 450; cursorY = 95; } },
    { duration: 400, action: () => { hoveredCommit = 0; } },
    { duration: 600, action: () => { selectedCommit = 0; } },
    { duration: 1000, action: () => {} },
    // Move to second commit
    { duration: 600, action: () => { cursorX = 400; cursorY = 155; hoveredCommit = 1; } },
    { duration: 400, action: () => { selectedCommit = 1; } },
    { duration: 800, action: () => {} },
    // Move to Tasks tab
    { duration: 700, action: () => { cursorX = 120; cursorY = 70; hoveredCommit = -1; selectedCommit = -1; } },
    { duration: 400, action: () => { activeTab = 'tasks'; } },
    { duration: 1200, action: () => {} },
    // Move to project selector
    { duration: 600, action: () => { cursorX = 500; cursorY = 20; } },
    { duration: 300, action: () => { showProjectDropdown = true; } },
    { duration: 600, action: () => { cursorX = 500; cursorY = 60; } },
    { duration: 300, action: () => { activeProject = 1; showProjectDropdown = false; } },
    { duration: 1000, action: () => {} },
    // Browse tasks in new project
    { duration: 500, action: () => { cursorX = 350; cursorY = 200; } },
    { duration: 800, action: () => {} },
    // Move to Prompts tab
    { duration: 600, action: () => { cursorX = 120; cursorY = 100; } },
    { duration: 400, action: () => { activeTab = 'prompts'; } },
    { duration: 1200, action: () => {} },
    // Switch to another project
    { duration: 600, action: () => { cursorX = 500; cursorY = 20; } },
    { duration: 300, action: () => { showProjectDropdown = true; } },
    { duration: 600, action: () => { cursorX = 500; cursorY = 80; } },
    { duration: 300, action: () => { activeProject = 2; showProjectDropdown = false; } },
    { duration: 1000, action: () => {} },
    // Move to Architecture tab
    { duration: 600, action: () => { cursorX = 120; cursorY = 130; } },
    { duration: 400, action: () => { activeTab = 'architecture'; } },
    { duration: 1200, action: () => {} },
    // Back to first project and Commits
    { duration: 600, action: () => { cursorX = 500; cursorY = 20; } },
    { duration: 300, action: () => { showProjectDropdown = true; } },
    { duration: 600, action: () => { cursorX = 500; cursorY = 40; } },
    { duration: 300, action: () => { activeProject = 0; showProjectDropdown = false; } },
    { duration: 500, action: () => {} },
    { duration: 600, action: () => { cursorX = 120; cursorY = 40; } },
    { duration: 400, action: () => { activeTab = 'commits'; } },
    { duration: 500, action: () => {} },
  ];

  function runAnimation() {
    if (animationFrame >= animationSequence.length) {
      animationFrame = 0;
    }

    const step = animationSequence[animationFrame];
    step.action();

    animationFrame++;

    animationInterval = setTimeout(runAnimation, step.duration);
  }

  function handleScroll() {
    scrollY = window.scrollY;

    // Calculate transformation based on scroll
    // Start at 3D (rotated), end at 2D (flat) over 400px of scroll
    const progress = Math.min(scrollY / 400, 1);

    perspective = 45 - (progress * 45); // 45 -> 0
    rotateX = 12 - (progress * 12); // 12 -> 0
    scale = 0.85 + (progress * 0.15); // 0.85 -> 1
  }

  onMount(() => {
    window.addEventListener('scroll', handleScroll);
    handleScroll();

    // Start animation after a short delay
    setTimeout(runAnimation, 1500);
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('scroll', handleScroll);
    }
    if (animationInterval) {
      clearTimeout(animationInterval);
    }
  });

  function onGetStarted() {
    push('/install');
  }

  function onViewDemo() {
    push('/commits');
  }

  const pillars = [
    {
      title: 'Visual Git',
      description: 'See your commit history as an interactive timeline'
    },
    {
      title: 'Prompt Economy',
      description: 'Track tokens, costs, and usage across AI providers'
    },
    {
      title: 'Tasks',
      description: 'Kanban boards that live with your repo'
    },
    {
      title: 'Architecture',
      description: 'Visualize your codebase structure'
    },
    {
      title: 'Tests',
      description: 'Monitor and run your test suites'
    }
  ];
</script>

<div class="landing-page">
  <header class="header">
    <div class="header-content">
      <div class="logo">branch<span class="logo-slash">/</span>monkey</div>
      <nav class="nav">
        <a href="#features">Features</a>
        <a href="#install">Install</a>
        <button class="nav-cta" on:click={onGetStarted}>Get Started</button>
      </nav>
    </div>
  </header>

  <section class="hero" bind:this={heroRef}>
    <div class="hero-content">
      <h1 class="headline">
        A framework for<br/>
        <span class="highlight">today</span>
      </h1>
      <p class="tagline">
        Move fast across projects. Work with any AI.<br/>
        Own your context. Own your memory.
      </p>
      <div class="hero-buttons">
        <button class="cta-button primary" on:click={onGetStarted}>
          Get Started
        </button>
      </div>
    </div>

    <div class="hero-image-container">
      <div
        class="hero-image-wrapper"
        style="transform: perspective(1200px) rotateX({rotateX}deg) scale({scale}); opacity: {0.7 + (1 - rotateX/12) * 0.3};"
      >
        <div class="app-screenshot">
          <div class="screenshot-header">
            <div class="window-controls">
              <span class="control red"></span>
              <span class="control yellow"></span>
              <span class="control green"></span>
            </div>
            <div class="window-title">Branch Monkey — {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</div>
            <div class="project-selector">
              <span class="project-name">{currentProject.name}</span>
              <span class="project-arrow">▾</span>
              {#if showProjectDropdown}
                <div class="project-dropdown">
                  {#each projects as project, i}
                    <div class="project-option" class:active={i === activeProject}>{project.name}</div>
                  {/each}
                </div>
              {/if}
            </div>
          </div>
          <div class="screenshot-content">
            <div class="screenshot-sidebar">
              <div class="sidebar-item" class:active={activeTab === 'commits'}>Commits</div>
              <div class="sidebar-item" class:active={activeTab === 'tasks'}>Tasks</div>
              <div class="sidebar-item" class:active={activeTab === 'prompts'}>Prompts</div>
              <div class="sidebar-item" class:active={activeTab === 'architecture'}>Architecture</div>
            </div>
            <div class="screenshot-main">
              {#if activeTab === 'commits'}
                <div class="commit-graph">
                  {#each currentProject.commits as commit, i}
                    <div class="commit-node" class:head={commit.isHead} class:hovered={hoveredCommit === i} class:selected={selectedCommit === i}>
                      <div class="node-dot"></div>
                      <div class="node-content">
                        <span class="node-sha">{commit.sha}</span>
                        <span class="node-msg">{commit.msg}</span>
                        {#if commit.branch}
                          <span class="node-branch">{commit.branch}</span>
                        {/if}
                      </div>
                    </div>
                    {#if i < currentProject.commits.length - 1}
                      <div class="commit-edge"></div>
                    {/if}
                  {/each}
                </div>
              {:else if activeTab === 'tasks'}
                <div class="tasks-view">
                  <div class="tasks-header">
                    <span class="tasks-title">{currentProject.name} Tasks</span>
                  </div>
                  <div class="tasks-columns">
                    <div class="task-column">
                      <div class="column-header">Todo</div>
                      {#each currentProject.tasks.todo as task}
                        <div class="task-card">{task}</div>
                      {/each}
                    </div>
                    <div class="task-column">
                      <div class="column-header">In Progress</div>
                      {#each currentProject.tasks.inProgress as task}
                        <div class="task-card active">{task}</div>
                      {/each}
                    </div>
                    <div class="task-column">
                      <div class="column-header">Done</div>
                      {#each currentProject.tasks.done as task}
                        <div class="task-card done">{task}</div>
                      {/each}
                    </div>
                  </div>
                </div>
              {:else if activeTab === 'prompts'}
                <div class="prompts-view">
                  <div class="prompts-header">
                    <span class="prompts-title">{currentProject.name}</span>
                    <span class="prompts-total">{currentProject.prompts.cost} total</span>
                  </div>
                  <div class="prompts-stats">
                    <div class="stat-card">
                      <span class="stat-value">{currentProject.prompts.total.toLocaleString()}</span>
                      <span class="stat-label">Total Prompts</span>
                    </div>
                    <div class="stat-card">
                      <span class="stat-value">{currentProject.prompts.inputTokens}</span>
                      <span class="stat-label">Input Tokens</span>
                    </div>
                    <div class="stat-card">
                      <span class="stat-value">{currentProject.prompts.outputTokens}</span>
                      <span class="stat-label">Output Tokens</span>
                    </div>
                  </div>
                  <div class="prompts-list">
                    <div class="prompt-item">
                      <span class="prompt-provider">Claude</span>
                      <span class="prompt-preview">Refactor the authentication...</span>
                      <span class="prompt-cost">$0.12</span>
                    </div>
                    <div class="prompt-item">
                      <span class="prompt-provider">GPT-4</span>
                      <span class="prompt-preview">Generate test cases for...</span>
                      <span class="prompt-cost">$0.08</span>
                    </div>
                  </div>
                </div>
              {:else if activeTab === 'architecture'}
                <div class="arch-view">
                  <div class="arch-header">Architecture Overview</div>
                  <div class="arch-diagram">
                    <div class="arch-layer">
                      <div class="arch-box frontend">Frontend</div>
                    </div>
                    <div class="arch-arrow">↓</div>
                    <div class="arch-layer">
                      <div class="arch-box api">API Layer</div>
                    </div>
                    <div class="arch-arrow">↓</div>
                    <div class="arch-layer">
                      <div class="arch-box db">Database</div>
                      <div class="arch-box cache">Cache</div>
                    </div>
                  </div>
                </div>
              {/if}
            </div>

            <!-- Animated cursor -->
            <div class="demo-cursor" style="left: {cursorX}px; top: {cursorY}px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M4 4L10.5 20.5L13 13L20.5 10.5L4 4Z" fill="var(--text-primary)" stroke="var(--bg-primary)" stroke-width="1.5"/>
              </svg>
            </div>
          </div>
        </div>
        <div class="screenshot-glow"></div>
      </div>
    </div>
  </section>

  <section class="pillars" id="features">
    <div class="pillars-grid">
      {#each pillars as pillar}
        <div class="pillar">
          <h3 class="pillar-title">{pillar.title}</h3>
          <p class="pillar-description">{pillar.description}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="install-section" id="install">
    <div class="install-content">
      <h2>Get started in seconds</h2>
      <button class="cta-button primary" on:click={onGetStarted}>
        Install
      </button>
    </div>
  </section>

  <footer class="footer">
    <div class="footer-content">
      <div class="footer-logo">branch/monkey</div>
      <div class="footer-links">
        <a href="https://github.com/gneyal/p_63_branch_monkey" target="_blank" rel="noopener">GitHub</a>
      </div>
    </div>
  </footer>
</div>

<style>
  .landing-page {
    min-height: 100vh;
    background: var(--bg-secondary);
    color: var(--text-primary);
    overflow-x: hidden;
  }

  /* Header */
  .header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: rgba(var(--bg-secondary-rgb, 29, 32, 33), 0.9);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border-secondary);
  }

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 16px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    font-size: 18px;
    font-weight: 700;
    font-family: 'Courier New', monospace;
    color: var(--text-primary);
  }

  .logo-slash {
    color: var(--accent-primary);
  }

  .nav {
    display: flex;
    align-items: center;
    gap: 32px;
  }

  .nav a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: color 0.2s;
  }

  .nav a:hover {
    color: var(--text-primary);
  }

  .nav-cta {
    background: var(--text-primary);
    color: var(--bg-primary);
    border: none;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .nav-cta:hover {
    opacity: 0.85;
  }

  /* Hero */
  .hero {
    padding: 160px 40px 100px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .hero-content {
    text-align: center;
    margin-bottom: 60px;
  }

  .headline {
    font-size: 56px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 24px 0;
    line-height: 1.15;
    letter-spacing: -1.5px;
  }

  .highlight {
    color: var(--text-tertiary);
  }

  .tagline {
    font-size: 18px;
    color: var(--text-secondary);
    margin: 0 0 40px 0;
    line-height: 1.7;
  }

  .hero-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
  }

  .cta-button {
    padding: 16px 40px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .cta-button.primary {
    background: var(--text-primary);
    color: var(--bg-primary);
  }

  .cta-button.primary:hover {
    opacity: 0.85;
    transform: translateY(-1px);
  }

  .cta-button.secondary {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-primary);
  }

  .cta-button.secondary:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
  }

  /* Hero Image */
  .hero-image-container {
    display: flex;
    justify-content: center;
    perspective: 1200px;
  }

  .hero-image-wrapper {
    position: relative;
    transition: transform 0.1s ease-out, opacity 0.1s ease-out;
    transform-origin: center top;
  }

  .app-screenshot {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    overflow: hidden;
    box-shadow:
      0 4px 6px rgba(0, 0, 0, 0.1),
      0 10px 40px rgba(0, 0, 0, 0.2);
    width: 900px;
    max-width: 90vw;
  }

  .screenshot-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
  }

  .window-controls {
    display: flex;
    gap: 8px;
  }

  .control {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }

  .control.red { background: #ff5f57; }
  .control.yellow { background: #febc2e; }
  .control.green { background: #28c840; }

  .window-title {
    flex: 1;
    text-align: center;
    font-size: 12px;
    color: var(--text-tertiary);
    font-weight: 500;
  }

  .project-selector {
    position: relative;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    font-size: 11px;
    color: var(--text-secondary);
    cursor: default;
  }

  .project-name {
    font-weight: 500;
    color: var(--text-primary);
  }

  .project-arrow {
    font-size: 10px;
    color: var(--text-tertiary);
  }

  .project-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 4px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    min-width: 140px;
    z-index: 10;
    overflow: hidden;
  }

  .project-option {
    padding: 8px 12px;
    font-size: 11px;
    color: var(--text-secondary);
    transition: all 0.15s;
  }

  .project-option.active {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .project-option:hover {
    background: var(--bg-hover);
  }

  .screenshot-content {
    display: flex;
    height: 400px;
  }

  .screenshot-sidebar {
    width: 180px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-primary);
    padding: 16px 0;
  }

  .sidebar-item {
    padding: 10px 20px;
    font-size: 13px;
    color: var(--text-secondary);
    cursor: default;
    transition: all 0.15s;
  }

  .sidebar-item.active {
    color: var(--text-primary);
    background: var(--bg-hover);
    border-left: 2px solid var(--text-tertiary);
    padding-left: 18px;
  }

  .screenshot-main {
    flex: 1;
    padding: 24px;
    overflow: hidden;
  }

  .commit-graph {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .commit-node {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    transition: all 0.2s;
  }

  .commit-node.head {
    border-color: var(--text-tertiary);
    box-shadow: 0 0 0 1px var(--text-tertiary);
  }

  .commit-node.hovered {
    background: var(--bg-hover);
  }

  .commit-node.selected {
    border-color: var(--text-secondary);
    box-shadow: 0 0 0 2px var(--text-secondary);
  }

  .node-dot {
    width: 10px;
    height: 10px;
    background: var(--text-tertiary);
    border-radius: 50%;
    flex-shrink: 0;
  }

  .node-content {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    min-width: 0;
  }

  .node-sha {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: var(--text-tertiary);
    font-weight: 600;
  }

  .node-msg {
    font-size: 13px;
    color: var(--text-primary);
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .node-branch {
    font-size: 11px;
    padding: 2px 8px;
    background: var(--text-tertiary);
    color: var(--bg-primary);
    border-radius: 3px;
    font-weight: 600;
  }

  .commit-edge {
    width: 2px;
    height: 20px;
    background: var(--border-primary);
    margin-left: 20px;
  }

  .screenshot-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 120%;
    height: 120%;
    background: radial-gradient(ellipse at center, var(--text-tertiary) 0%, transparent 70%);
    opacity: 0.03;
    pointer-events: none;
    z-index: -1;
  }

  /* Animated cursor */
  .demo-cursor {
    position: absolute;
    pointer-events: none;
    z-index: 100;
    transition: left 0.5s ease-out, top 0.5s ease-out;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
  }

  /* Tasks view */
  .tasks-view {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .tasks-header {
    margin-bottom: 16px;
  }

  .tasks-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .tasks-columns {
    display: flex;
    gap: 12px;
    flex: 1;
  }

  .task-column {
    flex: 1;
    background: var(--bg-secondary);
    border-radius: 6px;
    padding: 12px;
  }

  .column-header {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-tertiary);
    margin-bottom: 12px;
  }

  .task-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    padding: 10px 12px;
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }

  .task-card.active {
    border-color: var(--text-tertiary);
  }

  .task-card.done {
    opacity: 0.6;
    text-decoration: line-through;
  }

  /* Prompts view */
  .prompts-view {
    height: 100%;
  }

  .prompts-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }

  .prompts-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .prompts-total {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-tertiary);
  }

  .prompts-stats {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }

  .stat-card {
    flex: 1;
    background: var(--bg-secondary);
    border-radius: 6px;
    padding: 16px;
    text-align: center;
  }

  .stat-value {
    display: block;
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 10px;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .prompts-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .prompt-item {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--bg-secondary);
    border-radius: 4px;
    padding: 10px 12px;
  }

  .prompt-provider {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-tertiary);
    background: var(--bg-primary);
    padding: 2px 8px;
    border-radius: 3px;
  }

  .prompt-preview {
    flex: 1;
    font-size: 12px;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .prompt-cost {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-tertiary);
  }

  /* Architecture view */
  .arch-view {
    height: 100%;
  }

  .arch-header {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 20px;
  }

  .arch-diagram {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .arch-layer {
    display: flex;
    gap: 16px;
  }

  .arch-box {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    padding: 16px 32px;
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    min-width: 120px;
    text-align: center;
  }

  .arch-box.frontend {
    border-color: var(--text-tertiary);
  }

  .arch-box.api {
    border-color: var(--text-tertiary);
  }

  .arch-arrow {
    font-size: 18px;
    color: var(--text-tertiary);
  }

  /* Pillars */
  .pillars {
    padding: 60px 40px;
    max-width: 1100px;
    margin: 0 auto;
  }

  .pillars-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--border-secondary);
    border: 1px solid var(--border-secondary);
  }

  .pillar {
    background: var(--bg-secondary);
    padding: 32px 20px;
    text-align: center;
  }

  .pillar-title {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 0 0 10px 0;
    color: var(--text-primary);
  }

  .pillar-description {
    font-size: 13px;
    color: var(--text-tertiary);
    margin: 0;
    line-height: 1.5;
  }

  /* Install Section */
  .install-section {
    padding: 120px 40px;
    background: var(--bg-primary);
    border-top: 1px solid var(--border-secondary);
    border-bottom: 1px solid var(--border-secondary);
  }

  .install-content {
    max-width: 600px;
    margin: 0 auto;
    text-align: center;
  }

  .install-content h2 {
    font-size: 36px;
    font-weight: 700;
    margin: 0 0 16px 0;
    color: var(--text-primary);
  }


  /* Footer */
  .footer {
    padding: 40px;
    border-top: 1px solid var(--border-secondary);
  }

  .footer-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .footer-logo {
    font-size: 14px;
    font-weight: 600;
    font-family: 'Courier New', monospace;
    color: var(--text-tertiary);
  }

  .footer-links a {
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 14px;
    transition: color 0.2s;
  }

  .footer-links a:hover {
    color: var(--text-primary);
  }

  /* Responsive */
  @media (max-width: 900px) {
    .headline {
      font-size: 40px;
    }

    .tagline br {
      display: none;
    }

    .pillars-grid {
      grid-template-columns: repeat(3, 1fr);
    }

    .screenshot-content {
      height: 300px;
    }

    .screenshot-sidebar {
      width: 120px;
    }

    .sidebar-item {
      font-size: 11px;
      padding: 8px 12px;
    }

    .node-msg {
      display: none;
    }
  }

  @media (max-width: 600px) {
    .header-content {
      padding: 12px 20px;
    }

    .nav a {
      display: none;
    }

    .hero {
      padding: 120px 20px 60px;
    }

    .headline {
      font-size: 32px;
      letter-spacing: -0.5px;
    }

    .headline br {
      display: none;
    }

    .tagline {
      font-size: 16px;
    }

    .hero-buttons {
      flex-direction: column;
    }

    .cta-button {
      width: 100%;
    }

    .pillars,
    .install-section {
      padding: 60px 20px;
    }

    .pillars-grid {
      grid-template-columns: 1fr;
    }

    .screenshot-sidebar {
      display: none;
    }
  }
</style>
