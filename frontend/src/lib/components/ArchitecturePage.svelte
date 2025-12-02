<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { repoInfo } from '../stores/store.js';
  import { fetchRepoInfo } from '../services/api.js';
  import Toast from './Toast.svelte';
  import ArchitectureLibrary from './ArchitectureLibrary.svelte';
  import Topbar from './Topbar.svelte';
  import GlobalActions from './GlobalActions.svelte';
  import ThemePicker from './ThemePicker.svelte';

  onMount(async () => {
    if (!$repoInfo || !$repoInfo.path) {
      try {
        const info = await fetchRepoInfo();
        repoInfo.set(info);
      } catch (err) {
        console.error('Failed to load repo info:', err);
      }
    }
  });

  function handleGoToTop() {
    push('/commits');
  }

  function handleGoToBottom() {
    push('/commits');
  }

  function handleShowRemote() {
    push('/commits');
  }

  function handleNameBranches() {
    push('/commits');
  }

  function handleShowPrompts() {
    push('/commits');
  }

  function handleShowContext() {
    push('/commits');
  }
</script>

<main class="architecture-page">
  <Topbar activeView="arch" />

  <div class="page-content">
    <ArchitectureLibrary inline={true} />
  </div>

  <footer class="app-footer">
    <div class="footer-left">
      <GlobalActions
        onGoToTop={handleGoToTop}
        onGoToBottom={handleGoToBottom}
        onShowRemote={handleShowRemote}
        onNameBranches={handleNameBranches}
        onShowPrompts={handleShowPrompts}
        onShowContext={handleShowContext}
      />
    </div>

    <div class="footer-center">
    </div>

    <div class="footer-right">
      <ThemePicker compact={true} />
    </div>
  </footer>

  <Toast />
</main>

<style>
  .architecture-page {
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
    overflow: hidden;
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

  .footer-left {
    display: flex;
    justify-content: flex-start;
  }

  .footer-center {
    display: flex;
    justify-content: center;
  }

  .footer-right {
    display: flex;
    justify-content: flex-end;
  }

  @media (max-width: 768px) {
    .app-header {
      grid-template-columns: 1fr;
      gap: 12px;
      padding: 12px 16px;
    }

    .header-left,
    .header-center,
    .header-right {
      justify-content: center;
    }

    .app-footer {
      grid-template-columns: 1fr;
      gap: 8px;
      padding: 8px 16px;
    }

    .footer-left,
    .footer-center,
    .footer-right {
      justify-content: center;
    }
  }
</style>
