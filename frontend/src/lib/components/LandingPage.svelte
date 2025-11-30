<script>
  import { push } from 'svelte-spa-router';

  function onGetStarted() {
    push('/');
  }

  const pillars = [
    {
      title: 'UI',
      description: 'Visual interfaces for when you need to see the big picture'
    },
    {
      title: 'Agent',
      description: 'AI-powered workflows that understand your codebase'
    },
    {
      title: 'CLI',
      description: 'Command-line tools for when speed is everything'
    }
  ];

  const principles = [
    {
      title: 'Own Your Memory',
      description: 'LLMs forget between sessions. We remember. Your project knowledge persists, grows, and travels with you.'
    },
    {
      title: 'Own Your Context',
      description: 'Stop re-explaining your architecture. Build context once, use it everywhere - with any AI, any tool, any workflow.'
    },
    {
      title: 'Provider Agnostic',
      description: 'Claude today, GPT tomorrow, something new next week. Your context works with all of them. Never locked in.'
    }
  ];
</script>

<div class="landing-page">
  <header class="header">
    <div class="logo-mark">branch/monkey</div>
  </header>

  <section class="hero">
    <h1 class="headline">
      A framework for<br/>
      <span class="highlight">today</span>
    </h1>
    <p class="tagline">
      Move fast across projects. Work with any AI.<br/>
      Own your context. Own your memory.
    </p>
    <button class="cta-button" on:click={onGetStarted}>
      Get Started
    </button>
  </section>

  <section class="pillars">
    <div class="pillars-grid">
      {#each pillars as pillar}
        <div class="pillar">
          <h3 class="pillar-title">{pillar.title}</h3>
          <p class="pillar-description">{pillar.description}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="manifesto">
    <div class="manifesto-content">
      <p class="manifesto-text">
        LLMs are advancing constantly. Providers come and go.
        <strong>Your knowledge shouldn't be locked inside someone else's system.</strong>
      </p>
    </div>
  </section>

  <section class="principles">
    {#each principles as principle, i}
      <div class="principle">
        <span class="principle-number">{String(i + 1).padStart(2, '0')}</span>
        <div class="principle-content">
          <h3 class="principle-title">{principle.title}</h3>
          <p class="principle-description">{principle.description}</p>
        </div>
      </div>
    {/each}
  </section>

  <section class="cta-section">
    <button class="cta-button" on:click={onGetStarted}>
      Open App
    </button>
  </section>

  <footer class="footer">
    <p>branch/monkey</p>
  </footer>
</div>

<style>
  .landing-page {
    min-height: 100vh;
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .header {
    padding: 24px 40px;
  }

  .logo-mark {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: lowercase;
    color: var(--text-primary);
    font-family: 'Courier New', monospace;
  }

  /* Hero */
  .hero {
    text-align: center;
    padding: 120px 20px 80px;
    max-width: 800px;
    margin: 0 auto;
  }

  .headline {
    font-size: 72px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 24px 0;
    line-height: 1.05;
    letter-spacing: -2px;
  }

  .highlight {
    color: var(--text-tertiary);
  }

  .tagline {
    font-size: 20px;
    color: var(--text-secondary);
    margin: 0 0 48px 0;
    line-height: 1.6;
  }

  .cta-button {
    background: var(--text-primary);
    color: var(--bg-primary);
    border: none;
    padding: 16px 40px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .cta-button:hover {
    opacity: 0.85;
    transform: translateY(-1px);
  }

  /* Pillars */
  .pillars {
    padding: 60px 40px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .pillars-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border-secondary);
    border: 1px solid var(--border-secondary);
  }

  .pillar {
    background: var(--bg-secondary);
    padding: 40px 32px;
    text-align: center;
  }

  .pillar-title {
    font-size: 14px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 12px 0;
    color: var(--text-primary);
  }

  .pillar-description {
    font-size: 14px;
    color: var(--text-tertiary);
    margin: 0;
    line-height: 1.6;
  }

  /* Manifesto */
  .manifesto {
    padding: 80px 40px;
    background: var(--bg-primary);
    border-top: 1px solid var(--border-secondary);
    border-bottom: 1px solid var(--border-secondary);
  }

  .manifesto-content {
    max-width: 700px;
    margin: 0 auto;
    text-align: center;
  }

  .manifesto-text {
    font-size: 24px;
    line-height: 1.6;
    color: var(--text-secondary);
    margin: 0;
  }

  .manifesto-text strong {
    color: var(--text-primary);
  }

  /* Principles */
  .principles {
    max-width: 700px;
    margin: 0 auto;
    padding: 80px 40px;
  }

  .principle {
    display: flex;
    gap: 32px;
    padding: 40px 0;
    border-bottom: 1px solid var(--border-secondary);
  }

  .principle:last-child {
    border-bottom: none;
  }

  .principle-number {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-tertiary);
    font-family: 'Courier New', monospace;
    flex-shrink: 0;
    padding-top: 4px;
  }

  .principle-content {
    flex: 1;
  }

  .principle-title {
    font-size: 20px;
    font-weight: 600;
    margin: 0 0 12px 0;
    color: var(--text-primary);
  }

  .principle-description {
    font-size: 16px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.7;
  }

  /* CTA Section */
  .cta-section {
    text-align: center;
    padding: 80px 40px;
    background: var(--bg-primary);
    border-top: 1px solid var(--border-secondary);
  }

  .cta-text {
    font-size: 18px;
    color: var(--text-secondary);
    margin: 0 0 24px 0;
  }

  /* Footer */
  .footer {
    padding: 40px;
    text-align: center;
    border-top: 1px solid var(--border-secondary);
  }

  .footer p {
    margin: 0;
    font-size: 12px;
    color: var(--text-tertiary);
    font-family: 'Courier New', monospace;
    letter-spacing: 1px;
  }

  @media (max-width: 768px) {
    .hero {
      padding: 80px 20px 60px;
    }

    .headline {
      font-size: 48px;
      letter-spacing: -1px;
    }

    .tagline {
      font-size: 18px;
    }

    .pillars-grid {
      grid-template-columns: 1fr;
    }

    .principle {
      flex-direction: column;
      gap: 16px;
    }

    .principle-number {
      padding-top: 0;
    }
  }
</style>
