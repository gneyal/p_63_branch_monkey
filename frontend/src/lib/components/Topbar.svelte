<script>
  import { push } from 'svelte-spa-router';
  import { onMount } from 'svelte';
  import { Pin, PinOff } from 'lucide-svelte';
  import RepoSelector from './RepoSelector.svelte';

  export let activeView = 'commits'; // 'commits', 'tasks', 'prompts', 'arch', 'tests', 'spec', 'standards'

  const STORAGE_KEY = 'branch_monkey_pinned_tabs';

  // Define all tabs
  const allTabs = [
    { id: 'commits', label: 'Commits', route: '/commits', view: 'commits' },
    { id: 'tasks', label: 'Tasks', route: '/tasks', view: 'tasks' },
    { id: 'prompts', label: 'Prompts', route: '/prompts', view: 'prompts' },
    { id: 'context', label: 'Context', route: '/context', view: 'context' },
    { id: 'arch', label: 'Arch', route: '/architecture', view: 'arch' },
    { id: 'tests', label: 'Tests', route: '/tests', view: 'tests' },
    { id: 'spec', label: 'Spec', route: '/spec', view: 'spec' },
    { id: 'standards', label: 'Standards', route: '/standards', view: 'standards' },
  ];

  // Default pinned tabs
  const defaultPinned = ['commits', 'tasks', 'prompts'];

  let pinnedTabs = [...defaultPinned];
  let showMenu = false;

  onMount(() => {
    loadPinnedTabs();
  });

  function loadPinnedTabs() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        pinnedTabs = JSON.parse(saved);
      }
    } catch (e) {
      console.error('Failed to load pinned tabs:', e);
    }
  }

  function savePinnedTabs() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(pinnedTabs));
    } catch (e) {
      console.error('Failed to save pinned tabs:', e);
    }
  }

  function togglePin(tabId) {
    if (pinnedTabs.includes(tabId)) {
      pinnedTabs = pinnedTabs.filter(id => id !== tabId);
    } else {
      pinnedTabs = [...pinnedTabs, tabId];
    }
    savePinnedTabs();
  }

  function navigateTo(route) {
    push(route);
    showMenu = false;
  }

  function toggleMenu() {
    showMenu = !showMenu;
  }

  function closeMenu() {
    showMenu = false;
  }

  $: visibleTabs = allTabs.filter(tab => pinnedTabs.includes(tab.id));

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

  function goToInstall() {
    push('/install');
  }

  function goToHome() {
    push('/');
  }
</script>

<header class="topbar">
  <div class="header-left">
    <div class="title-container">
      <h1
        class="app-title"
        on:mouseenter={startMonkeyAnimation}
        on:mouseleave={stopMonkeyAnimation}
        on:click={goToHome}
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
        class="view-btn help-btn"
        class:active={activeView === 'install'}
        on:click={goToInstall}
        title="Getting Started"
      >
        ?
      </button>
      {#each visibleTabs as tab (tab.id)}
        <button
          class="view-btn"
          class:active={activeView === tab.view}
          on:click={() => navigateTo(tab.route)}
          title={tab.label}
        >
          {tab.label}
        </button>
      {/each}
      <div class="menu-container">
        <button
          class="view-btn help-btn"
          on:click={toggleMenu}
          title="More tabs"
        >
          ...
        </button>
        {#if showMenu}
          <div class="tabs-dropdown">
            {#each allTabs as tab (tab.id)}
              <div class="dropdown-item">
                <button
                  class="dropdown-tab-btn"
                  class:active={activeView === tab.view}
                  on:click={() => navigateTo(tab.route)}
                >
                  {tab.label}
                </button>
                <button
                  class="pin-btn"
                  class:pinned={pinnedTabs.includes(tab.id)}
                  on:click|stopPropagation={() => togglePin(tab.id)}
                  title={pinnedTabs.includes(tab.id) ? 'Unpin' : 'Pin'}
                >
                  {#if pinnedTabs.includes(tab.id)}
                    <Pin size={14} />
                  {:else}
                    <PinOff size={14} />
                  {/if}
                </button>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  </div>
</header>

{#if showMenu}
  <div class="menu-backdrop" on:click={closeMenu}></div>
{/if}

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
    position: relative;
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

  .view-btn.help-btn {
    font-weight: 700;
    font-size: 11px;
    padding: 6px 10px;
  }

  .menu-container {
    position: relative;
  }

  .tabs-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 6px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    box-shadow: var(--shadow-large);
    z-index: 1001;
    min-width: 180px;
    padding: 4px 0;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2px 8px;
  }

  .dropdown-tab-btn {
    flex: 1;
    padding: 8px 12px;
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    text-align: left;
    cursor: pointer;
    border-radius: 3px;
    transition: all 0.15s;
  }

  .dropdown-tab-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .dropdown-tab-btn.active {
    background: var(--accent-primary);
    color: var(--bg-primary);
  }

  .pin-btn {
    padding: 6px 8px;
    background: none;
    border: none;
    color: var(--text-tertiary);
    font-size: 14px;
    cursor: pointer;
    border-radius: 3px;
    transition: all 0.15s;
  }

  .pin-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .pin-btn.pinned {
    color: var(--accent-primary);
  }

  .pin-btn.pinned :global(svg) {
    fill: var(--accent-primary);
  }

  .menu-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
  }
</style>
