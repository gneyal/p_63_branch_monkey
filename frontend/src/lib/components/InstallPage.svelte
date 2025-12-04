<script>
  import { onMount } from 'svelte';
  import { push } from 'svelte-spa-router';
  import { repoInfo } from '../stores/store.js';
  import { fetchRepoInfo } from '../services/api.js';
  import Toast from './Toast.svelte';
  import Topbar from './Topbar.svelte';
  import ThemePicker from './ThemePicker.svelte';

  let copiedSection = null;

  const aiInstallPrompt = `Install and run Branch Monkey for me:

1. git clone https://github.com/gneyal/p_63_branch_monkey.git
2. cd p_63_branch_monkey
3. pip install -e .
4. cd frontend && npm install
5. Start backend: python fastapi_server.py (in background)
6. Start frontend: cd frontend && npm run dev
7. Open http://localhost:5173 in browser`;

  const aiHookPrompt = `Set up Claude Code hook for Branch Monkey prompt tracking:

Add this to your project's .claude/settings.local.json file:
{
  "hooks": {
    "Stop": [
      {
        "command": "python /path/to/branch_monkey/branch_monkey/hooks/claude_code_hook.py"
      }
    ]
  }
}

This installs the hook per-project, so each project tracks its own prompts separately.

The "Stop" hook fires once when Claude finishes responding, giving you complete token counts and costs.

Examples - replace the path based on where you cloned Branch Monkey:

macOS:
  "command": "python /Users/john/Code/p_63_branch_monkey/branch_monkey/hooks/claude_code_hook.py"

Linux:
  "command": "python /home/alex/dev/p_63_branch_monkey/branch_monkey/hooks/claude_code_hook.py"

Windows:
  "command": "python C:/Users/mike/Code/p_63_branch_monkey/branch_monkey/hooks/claude_code_hook.py"

With pip install -e (editable):
  "command": "python -m branch_monkey.hooks.claude_code_hook"`;

  function copyAiPrompt(prompt, section) {
    navigator.clipboard.writeText(prompt).then(() => {
      copiedSection = section;
      setTimeout(() => copiedSection = null, 2000);
    });
  }

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

  function copyToClipboard(text, section) {
    navigator.clipboard.writeText(text).then(() => {
      copiedSection = section;
      setTimeout(() => copiedSection = null, 2000);
    });
  }
</script>

<main class="install-page">
  <Topbar activeView="install" />

  <div class="page-content">
    <div class="install-container">
      <div class="install-header">
        <h1>Getting Started with Branch Monkey</h1>
        <p class="subtitle">A visual Git companion for AI-assisted development</p>
      </div>

      <div class="sections">
        <!-- Quick Install with AI -->
        <section class="install-section ai-section">
          <h2>Quick Install</h2>
          <p class="section-desc">Copy this prompt and paste it to your AI assistant to install Branch Monkey.</p>

          <div class="ai-prompt-box">
            <pre class="ai-prompt">{aiInstallPrompt}</pre>
            <button
              class="copy-ai-btn"
              class:copied={copiedSection === 'ai-install'}
              on:click={() => copyAiPrompt(aiInstallPrompt, 'ai-install')}
            >
              {copiedSection === 'ai-install' ? 'Copied!' : 'Copy for AI'}
            </button>
          </div>
        </section>

        <!-- Claude Code Hook with AI -->
        <section class="install-section ai-section">
          <h2>Claude Code Hook</h2>
          <p class="section-desc">Track your AI prompt usage automatically. Copy this to set up the hook.</p>

          <div class="ai-prompt-box">
            <pre class="ai-prompt">{aiHookPrompt}</pre>
            <button
              class="copy-ai-btn"
              class:copied={copiedSection === 'ai-hook'}
              on:click={() => copyAiPrompt(aiHookPrompt, 'ai-hook')}
            >
              {copiedSection === 'ai-hook' ? 'Copied!' : 'Copy for AI'}
            </button>
          </div>
        </section>

        <!-- Features -->
        <section class="install-section">
          <h2>Features</h2>
          <div class="features-grid">
            <div class="feature">
              <div class="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="3"/>
                  <path d="M12 2v4m0 12v4M2 12h4m12 0h4"/>
                </svg>
              </div>
              <h3>Commits</h3>
              <p>Visual commit tree with branch visualization, navigation, and quick actions</p>
            </div>

            <div class="feature">
              <div class="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <path d="M9 9h6m-6 4h6m-6 4h4"/>
                </svg>
              </div>
              <h3>Tasks</h3>
              <p>Kanban-style task management with versions, priorities, and drag-and-drop</p>
            </div>

            <div class="feature">
              <div class="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"/>
                </svg>
              </div>
              <h3>Prompts</h3>
              <p>Track AI prompt usage with token counts, costs, and performance metrics</p>
            </div>

            <div class="feature">
              <div class="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 3h18v18H3zM9 3v18M3 9h18"/>
                </svg>
              </div>
              <h3>Architecture</h3>
              <p>Document and visualize your codebase architecture with AI-generated summaries</p>
            </div>

            <div class="feature">
              <div class="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12l2 2 4-4"/>
                  <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <h3>Tests</h3>
              <p>Monitor test results and coverage across your project</p>
            </div>

            <div class="feature">
              <div class="feature-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
              </div>
              <h3>25+ Themes</h3>
              <p>Choose from vim-inspired color themes like Gruvbox, Nord, Dracula, and more</p>
            </div>
          </div>
        </section>

        <!-- Keyboard Shortcuts -->
        <section class="install-section">
          <h2>Tips</h2>
          <ul class="tips-list">
            <li>Click the <strong>branch/monkey</strong> logo to return to the commits view</li>
            <li>Use the repo selector in the topbar to switch between repositories</li>
            <li>Star your favorite repos for quick access</li>
            <li>Click on commit nodes in the tree to see details and actions</li>
            <li>Drag tasks between columns to change their status</li>
          </ul>
        </section>
      </div>
    </div>
  </div>

  <footer class="app-footer">
    <div class="footer-left">
      <button class="back-btn" on:click={() => push('/commits')}>
        Back to Commits
      </button>
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
  .install-page {
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

  .install-container {
    max-width: 900px;
    margin: 0 auto;
  }

  .install-header {
    text-align: center;
    margin-bottom: 48px;
  }

  .install-header h1 {
    margin: 0 0 12px 0;
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .subtitle {
    margin: 0;
    font-size: 16px;
    color: var(--text-secondary);
  }

  .sections {
    display: flex;
    flex-direction: column;
    gap: 48px;
  }

  .install-section {
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 8px;
    padding: 24px;
  }

  .install-section h2 {
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-primary);
  }

  .section-desc {
    margin: -8px 0 20px 0;
    color: var(--text-secondary);
    font-size: 14px;
  }

  .ai-section {
    border: 2px solid var(--accent-primary);
  }

  .ai-prompt-box {
    position: relative;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
    overflow: hidden;
  }

  .ai-prompt {
    margin: 0;
    padding: 16px;
    padding-right: 100px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .copy-ai-btn {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 8px 16px;
    background: var(--accent-primary);
    border: none;
    border-radius: 4px;
    color: var(--bg-primary);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }

  .copy-ai-btn:hover {
    filter: brightness(1.1);
    transform: scale(1.02);
  }

  .copy-ai-btn.copied {
    background: #22c55e;
  }

  .step {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
  }

  .step:last-child {
    margin-bottom: 0;
  }

  .step-number {
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-primary);
    color: var(--bg-primary);
    border-radius: 50%;
    font-size: 14px;
    font-weight: 600;
  }

  .step-content {
    flex: 1;
    min-width: 0;
  }

  .step-content h3 {
    margin: 0 0 8px 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .step-content p {
    margin: 8px 0 0 0;
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .code-block {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    padding: 12px 16px;
  }

  .code-block code,
  .code-block pre {
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: var(--accent-primary);
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
  }

  .code-json pre {
    white-space: pre;
  }

  .copy-btn {
    flex-shrink: 0;
    padding: 4px 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-primary);
    border-radius: 3px;
    color: var(--text-secondary);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .copy-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .note {
    font-size: 13px !important;
    color: var(--text-tertiary) !important;
  }

  .note code {
    background: var(--bg-secondary);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }

  .feature {
    padding: 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: 6px;
  }

  .feature-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-primary);
    color: var(--bg-primary);
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .feature h3 {
    margin: 0 0 6px 0;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .feature p {
    margin: 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .tips-list {
    margin: 0;
    padding: 0 0 0 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .tips-list li {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
  }

  .tips-list strong {
    color: var(--text-primary);
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

  .back-btn {
    padding: 6px 16px;
    background: var(--bg-primary);
    border: 1px solid var(--border-primary);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s;
  }

  .back-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    border-color: var(--accent-primary);
  }

  @media (max-width: 768px) {
    .page-content {
      padding: 16px;
    }

    .install-header h1 {
      font-size: 24px;
    }

    .step {
      flex-direction: column;
      gap: 8px;
    }

    .step-number {
      width: 24px;
      height: 24px;
      font-size: 12px;
    }

    .code-block {
      flex-direction: column;
      align-items: stretch;
    }

    .copy-btn {
      align-self: flex-end;
    }

    .features-grid {
      grid-template-columns: 1fr;
    }

    .app-footer {
      grid-template-columns: 1fr;
      gap: 8px;
    }

    .footer-left,
    .footer-center,
    .footer-right {
      justify-content: center;
    }
  }
</style>
