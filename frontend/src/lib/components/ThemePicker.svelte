<script>
  import { theme, themes, setTheme } from '../stores/theme.js';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let compact = false;
  export let dropdownDirection = 'up'; // 'up' or 'down'

  let showPicker = false;

  function handleThemeSelect(themeId) {
    setTheme(themeId);
    showPicker = false;
    dispatch('change', themeId);
  }

  function handleClickOutside(e) {
    if (showPicker && !e.target.closest('.theme-picker-container')) {
      showPicker = false;
    }
  }

  $: currentTheme = themes.find(t => t.id === $theme) || themes[0];
</script>

<svelte:window on:click={handleClickOutside} />

<div class="theme-picker-container" class:compact>
  <button
    class="theme-picker-trigger"
    on:click|stopPropagation={() => showPicker = !showPicker}
    title="Change theme"
  >
    {#if compact}
      <div class="compact-preview" style="background: {currentTheme.preview.bg}">
        <span class="compact-text" style="color: {currentTheme.preview.fg}">Aa</span>
        <span class="compact-accent" style="background: {currentTheme.preview.accent}"></span>
      </div>
    {:else}
      <div class="theme-swatch">
        <span class="swatch-color" style="background: {currentTheme.preview.bg}"></span>
        <span class="swatch-color" style="background: {currentTheme.preview.fg}"></span>
        <span class="swatch-color" style="background: {currentTheme.preview.accent}"></span>
      </div>
      <span class="theme-name">{currentTheme.name}</span>
      <span class="chevron">{showPicker ? '▲' : '▼'}</span>
    {/if}
  </button>

  {#if showPicker}
    <div class="theme-dropdown" class:dropdown-down={dropdownDirection === 'down'} on:click|stopPropagation>
      <div class="theme-dropdown-header">
        <span class="dropdown-title">Color Themes</span>
        <span class="dropdown-subtitle">vim-inspired</span>
      </div>
      <div class="theme-grid">
        {#each themes as t (t.id)}
          <button
            class="theme-option"
            class:active={$theme === t.id}
            on:click={() => handleThemeSelect(t.id)}
          >
            <div class="theme-preview" style="background: {t.preview.bg}">
              <div class="preview-content">
                <span class="preview-text" style="color: {t.preview.fg}">Aa</span>
                <span class="preview-accent" style="background: {t.preview.accent}"></span>
              </div>
            </div>
            <span class="theme-label">{t.name}</span>
            {#if t.type === 'light'}
              <span class="theme-type light">light</span>
            {:else}
              <span class="theme-type dark">dark</span>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .theme-picker-container {
    position: relative;
  }

  .theme-picker-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .compact .theme-picker-trigger {
    padding: 6px 10px;
    gap: 8px;
  }

  .theme-picker-trigger:hover {
    background: var(--bg-hover);
    border-color: var(--border-hover);
    color: var(--text-primary);
  }

  .compact-preview {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 3px 6px;
    border-radius: 3px;
    border: 1px solid var(--border-secondary);
  }

  .compact-text {
    font-size: 11px;
    font-weight: 700;
    font-family: 'Courier New', monospace;
    line-height: 1;
  }

  .compact-accent {
    width: 8px;
    height: 8px;
    border-radius: 2px;
  }

  .compact-name {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-secondary);
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .theme-swatch {
    display: flex;
    gap: 2px;
  }

  .swatch-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    border: 1px solid var(--border-secondary);
  }

  .theme-name {
    font-weight: 500;
    text-transform: capitalize;
  }

  .chevron {
    font-size: 8px;
    opacity: 0.6;
  }

  .theme-dropdown {
    position: absolute;
    bottom: calc(100% + 4px);
    right: 0;
    min-width: 320px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    box-shadow: var(--shadow-large);
    z-index: 1000;
    overflow: hidden;
  }

  .theme-dropdown.dropdown-down {
    bottom: auto;
    top: calc(100% + 4px);
  }

  .theme-dropdown-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-secondary);
    background: var(--bg-secondary);
  }

  .dropdown-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-primary);
  }

  .dropdown-subtitle {
    font-size: 10px;
    color: var(--text-tertiary);
    font-style: italic;
  }

  .theme-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 12px;
    max-height: 400px;
    overflow-y: auto;
  }

  .theme-option {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 8px;
    background: transparent;
    border: 2px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .theme-option:hover {
    background: var(--bg-hover);
  }

  .theme-option.active {
    border-color: var(--accent-primary);
    background: var(--bg-secondary);
  }

  .theme-preview {
    width: 100%;
    aspect-ratio: 16/10;
    border-radius: 4px;
    border: 1px solid var(--border-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .preview-content {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .preview-text {
    font-size: 16px;
    font-weight: 700;
    font-family: 'Courier New', monospace;
  }

  .preview-accent {
    width: 16px;
    height: 16px;
    border-radius: 3px;
  }

  .theme-label {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-primary);
    text-transform: capitalize;
  }

  .theme-type {
    font-size: 8px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 2px 6px;
    border-radius: 3px;
  }

  .theme-type.light {
    background: #fef3c7;
    color: #92400e;
  }

  .theme-type.dark {
    background: #374151;
    color: #9ca3af;
  }

  :global([data-theme="dark"]) .theme-type.light {
    background: #78350f;
    color: #fcd34d;
  }
</style>
