<script>
  import { push } from 'svelte-spa-router';
  import RepoSelector from './RepoSelector.svelte';

  export let activeView = 'commits'; // 'commits', 'tasks', 'arch', 'tests'

  let showMonkey = false;
  let monkeyFrame = 0;
  let animationInterval;

  const monkeyFrames = [
    `        ___
     {. .}
      >o<
     /|||\\
    // \\\\\\\\
=========
   ||
   ||`,
    `
    {. .}
     >o<
    /|||\\
   // \\\\\\\\

=========
   ||
   ||`,
    `
     {. .}
      >o<
     /|||\\
    // \\\\\\\\
       =========
            ||
            ||`,
    `
    {. .}
     >o<
    /|||\\
   // \\\\\\\\

=========
   ||
   ||`,
  ];

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

  function goToCommits() {
    push('/commits');
  }

  function goToTasks() {
    push('/tasks');
  }

  function goToArch() {
    push('/architecture');
  }

  function goToTests() {
    push('/tests');
  }
</script>

<header class="topbar">
  <div class="header-left">
    <div class="title-container">
      <h1
        class="app-title"
        on:mouseenter={startMonkeyAnimation}
        on:mouseleave={stopMonkeyAnimation}
        on:click={goToCommits}
      >
        branch/monkey
      </h1>
      {#if showMonkey}
        <div class="ascii-monkey">
          <pre>{monkeyFrames[monkeyFrame]}</pre>
        </div>
      {/if}
    </div>
  </div>

  <div class="header-center">
    <RepoSelector />
  </div>

  <div class="header-right">
    <div class="view-toggle">
      <button
        class="view-btn"
        class:active={activeView === 'commits'}
        on:click={goToCommits}
        title="Commits view"
      >
        Commits
      </button>
      <button
        class="view-btn"
        class:active={activeView === 'tasks'}
        on:click={goToTasks}
        title="Tasks view"
      >
        Tasks
      </button>
      <button
        class="view-btn"
        class:active={activeView === 'arch'}
        on:click={goToArch}
        title="Architecture view"
      >
        Arch
      </button>
      <button
        class="view-btn"
        class:active={activeView === 'tests'}
        on:click={goToTests}
        title="Tests view"
      >
        Tests
      </button>
    </div>
  </div>
</header>

<style>
  .topbar {
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
    .topbar {
      grid-template-columns: auto 1fr auto;
      gap: 16px;
      padding: 12px 16px;
    }

    .app-title {
      font-size: 10px;
    }
  }

  @media (max-width: 768px) {
    .topbar {
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

  .app-title:hover {
    color: var(--accent-primary);
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
</style>
