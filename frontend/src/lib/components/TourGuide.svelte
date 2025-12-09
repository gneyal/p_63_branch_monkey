<script>
  import { onMount, onDestroy } from 'svelte';
  import { push } from 'svelte-spa-router';

  export let isActive = false;
  export let oncomplete = () => {};

  let currentStep = 0;
  let tooltipPosition = { top: 0, left: 0 };
  let spotlightStyle = '';
  let arrowDirection = 'top'; // top, bottom, left, right

  const tourSteps = [
    {
      id: 'welcome',
      title: 'Welcome to Branch Monkey!',
      content: 'Let\'s take a quick tour of the app. This will help you get started with the key features.',
      selector: null, // No element highlight for welcome
      position: 'center',
      route: '/commits'
    },
    {
      id: 'repo-selector',
      title: 'Repository Selector',
      content: 'Switch between different repositories here. Your current repo is shown in the center.',
      selector: '.header-center',
      position: 'bottom',
      route: '/commits'
    },
    {
      id: 'commits',
      title: 'Commits',
      content: 'See your commit history as a visual timeline. Great for understanding project progress.',
      selector: '[title="Commits"]',
      position: 'bottom',
      route: '/commits'
    },
    {
      id: 'tasks',
      title: 'Tasks',
      content: 'Track your development tasks. Organize work with a simple kanban-style board.',
      selector: '[title="Tasks"]',
      position: 'bottom',
      route: '/tasks'
    },
    {
      id: 'prompts',
      title: 'Prompts',
      content: 'View your AI prompt history, token usage, and costs. Track your AI-assisted development.',
      selector: '[title="Prompts"]',
      position: 'bottom',
      route: '/prompts'
    },
    {
      id: 'more-menu',
      title: 'More Pages',
      content: 'Click the ··· menu to access additional pages like Context and Standards. You can also pin/unpin tabs here.',
      selector: '.menu-container',
      position: 'bottom-left',
      route: '/prompts'
    },
    {
      id: 'context',
      title: 'Context',
      content: 'Generate and store AI summaries of your codebase and prompt history. Great for onboarding and documentation.',
      selector: '[title="Context"]',
      position: 'bottom-left',
      route: '/context'
    },
    {
      id: 'architecture',
      title: 'Architecture',
      content: 'Visualize and document your system architecture. See entities, endpoints, UI components, and tech stack at a glance.',
      selector: '[title="Architecture"]',
      position: 'bottom-left',
      route: '/architecture'
    },
    {
      id: 'standards',
      title: 'Standards',
      content: 'Define your team\'s coding standards for Design, Backend, API, and Code. AI assistants can reference these to maintain consistency.',
      selector: '[title="Standards"]',
      position: 'bottom-left',
      route: '/standards'
    },
    {
      id: 'theme-picker',
      title: 'Theme Picker',
      content: 'Customize your experience with 25+ vim-inspired color themes. Light and dark options available.',
      selector: '.theme-picker-container',
      position: 'top-left',
      route: '/standards'
    },
    {
      id: 'complete',
      title: 'You\'re all set!',
      content: 'Explore the app and make it yours. You can restart this tour anytime from the menu.',
      selector: null,
      position: 'center',
      route: '/commits'
    }
  ];

  $: currentTourStep = tourSteps[currentStep];
  $: progress = ((currentStep + 1) / tourSteps.length) * 100;

  function calculatePosition(selector, position) {
    if (!selector || position === 'center') {
      return {
        tooltipStyle: 'top: 50%; left: 50%; transform: translate(-50%, -50%);',
        spotlightStyle: '',
        arrowDir: 'none'
      };
    }

    const element = document.querySelector(selector);
    if (!element) {
      return {
        tooltipStyle: 'top: 50%; left: 50%; transform: translate(-50%, -50%);',
        spotlightStyle: '',
        arrowDir: 'none'
      };
    }

    const rect = element.getBoundingClientRect();
    const padding = 8;

    // Spotlight around the element
    const spotlight = `
      top: ${rect.top - padding}px;
      left: ${rect.left - padding}px;
      width: ${rect.width + padding * 2}px;
      height: ${rect.height + padding * 2}px;
    `;

    let tooltip = '';
    let arrowDir = 'top';

    switch (position) {
      case 'bottom':
        tooltip = `top: ${rect.bottom + 16}px; left: ${rect.left + rect.width / 2}px; transform: translateX(-50%);`;
        arrowDir = 'top';
        break;
      case 'bottom-left':
        tooltip = `top: ${rect.bottom + 16}px; left: ${rect.right}px; transform: translateX(-100%);`;
        arrowDir = 'top-right';
        break;
      case 'top':
        tooltip = `bottom: ${window.innerHeight - rect.top + 16}px; left: ${rect.left + rect.width / 2}px; transform: translateX(-50%);`;
        arrowDir = 'bottom';
        break;
      case 'top-left':
        tooltip = `bottom: ${window.innerHeight - rect.top + 16}px; right: ${window.innerWidth - rect.right}px;`;
        arrowDir = 'bottom-right';
        break;
      case 'left':
        tooltip = `top: ${rect.top + rect.height / 2}px; right: ${window.innerWidth - rect.left + 16}px; transform: translateY(-50%);`;
        arrowDir = 'right';
        break;
      case 'right':
        tooltip = `top: ${rect.top + rect.height / 2}px; left: ${rect.right + 16}px; transform: translateY(-50%);`;
        arrowDir = 'left';
        break;
      default:
        tooltip = `top: ${rect.bottom + 16}px; left: ${rect.left + rect.width / 2}px; transform: translateX(-50%);`;
        arrowDir = 'top';
    }

    return { tooltipStyle: tooltip, spotlightStyle: spotlight, arrowDir };
  }

  function updatePosition() {
    if (!isActive) return;

    const { tooltipStyle, spotlightStyle: spotlight, arrowDir } = calculatePosition(
      currentTourStep.selector,
      currentTourStep.position
    );

    tooltipPosition = tooltipStyle;
    spotlightStyle = spotlight;
    arrowDirection = arrowDir;
  }

  function navigateToStep(step) {
    const route = tourSteps[step]?.route;
    if (route && window.location.hash !== `#${route}`) {
      push(route);
      // Give the page time to load before updating position
      setTimeout(updatePosition, 150);
    } else {
      setTimeout(updatePosition, 50);
    }
  }

  function nextStep() {
    if (currentStep < tourSteps.length - 1) {
      currentStep++;
      navigateToStep(currentStep);
    } else {
      completeTour();
    }
  }

  function prevStep() {
    if (currentStep > 0) {
      currentStep--;
      navigateToStep(currentStep);
    }
  }

  function skipTour() {
    completeTour();
  }

  function completeTour() {
    localStorage.setItem('branch_monkey_tour_completed', 'true');
    isActive = false;
    currentStep = 0;
    oncomplete();
  }

  function handleKeydown(e) {
    if (!isActive) return;

    if (e.key === 'Escape') {
      skipTour();
    } else if (e.key === 'ArrowRight' || e.key === 'Enter') {
      nextStep();
    } else if (e.key === 'ArrowLeft') {
      prevStep();
    }
  }

  onMount(() => {
    if (isActive) {
      setTimeout(updatePosition, 100);
    }
    window.addEventListener('resize', updatePosition);
  });

  onDestroy(() => {
    window.removeEventListener('resize', updatePosition);
  });

  $: if (isActive) {
    setTimeout(updatePosition, 100);
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isActive}
  <div class="tour-overlay">
    <!-- Dark overlay with spotlight cutout -->
    <div class="tour-backdrop"></div>

    <!-- Spotlight highlight -->
    {#if spotlightStyle}
      <div class="tour-spotlight" style={spotlightStyle}></div>
    {/if}

    <!-- Tooltip -->
    <div class="tour-tooltip" style={tooltipPosition} class:center={currentTourStep.position === 'center'}>
      <div class="tour-arrow {arrowDirection}"></div>

      <div class="tour-header">
        <span class="tour-step-indicator">
          {currentStep + 1} / {tourSteps.length}
        </span>
        <button class="tour-close" on:click={skipTour} title="Skip tour">X</button>
      </div>

      <h3 class="tour-title">{currentTourStep.title}</h3>
      <p class="tour-content">{currentTourStep.content}</p>

      <div class="tour-progress">
        <div class="tour-progress-bar" style="width: {progress}%"></div>
      </div>

      <div class="tour-actions">
        {#if currentStep > 0}
          <button class="tour-btn secondary" on:click={prevStep}>Back</button>
        {:else}
          <button class="tour-btn secondary" on:click={skipTour}>Skip</button>
        {/if}

        <button class="tour-btn primary" on:click={nextStep}>
          {currentStep === tourSteps.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .tour-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 10000;
    pointer-events: none;
  }

  .tour-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: transparent;
    pointer-events: auto;
  }

  .tour-spotlight {
    position: absolute;
    background: transparent;
    border-radius: 8px;
    border: 2px solid var(--accent-primary);
    box-shadow: 0 0 0 4px rgba(var(--accent-primary-rgb, 250, 189, 47), 0.3);
    pointer-events: none;
    transition: all 0.3s ease;
  }

  .tour-tooltip {
    position: fixed;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    padding: 20px;
    max-width: 360px;
    min-width: 300px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    pointer-events: auto;
    z-index: 10001;
    animation: tooltipFadeIn 0.2s ease;
  }

  .tour-tooltip.center {
    text-align: center;
  }

  @keyframes tooltipFadeIn {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .tour-arrow {
    position: absolute;
    width: 12px;
    height: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    transform: rotate(45deg);
  }

  .tour-arrow.top {
    top: -7px;
    left: 50%;
    margin-left: -6px;
    border-bottom: none;
    border-right: none;
  }

  .tour-arrow.top-right {
    top: -7px;
    right: 24px;
    border-bottom: none;
    border-right: none;
  }

  .tour-arrow.bottom {
    bottom: -7px;
    left: 50%;
    margin-left: -6px;
    border-top: none;
    border-left: none;
  }

  .tour-arrow.bottom-right {
    bottom: -7px;
    right: 24px;
    border-top: none;
    border-left: none;
  }

  .tour-arrow.left {
    left: -7px;
    top: 50%;
    margin-top: -6px;
    border-top: none;
    border-right: none;
  }

  .tour-arrow.right {
    right: -7px;
    top: 50%;
    margin-top: -6px;
    border-bottom: none;
    border-left: none;
  }

  .tour-arrow.none {
    display: none;
  }

  .tour-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .tour-step-indicator {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .tour-close {
    background: transparent;
    border: none;
    color: var(--text-tertiary);
    font-size: 14px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.15s;
  }

  .tour-close:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .tour-title {
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .tour-content {
    margin: 0 0 16px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-secondary);
  }

  .tour-progress {
    height: 3px;
    background: var(--bg-secondary);
    border-radius: 2px;
    margin-bottom: 16px;
    overflow: hidden;
  }

  .tour-progress-bar {
    height: 100%;
    background: var(--accent-primary);
    border-radius: 2px;
    transition: width 0.3s ease;
  }

  .tour-actions {
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }

  .tour-btn {
    flex: 1;
    padding: 10px 16px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }

  .tour-btn.primary {
    background: var(--accent-primary);
    border: none;
    color: var(--bg-primary);
  }

  .tour-btn.primary:hover {
    opacity: 0.9;
  }

  .tour-btn.secondary {
    background: transparent;
    border: 1px solid var(--border-primary);
    color: var(--text-secondary);
  }

  .tour-btn.secondary:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    border-color: var(--border-hover);
  }
</style>
