<script>
  import { push } from 'svelte-spa-router';

  function onGetStarted() {
    push('/');
  }

  const features = [
    {
      icon: '',
      title: 'Visual Commit Tree',
      description: 'See your Git history as an interactive flow diagram. Navigate branches, view commit details, and understand your project evolution.'
    },
    {
      icon: '',
      title: 'Safe Experiments',
      description: 'Create experimental branches without fear. Branch Monkey tracks your experiments and makes it easy to compare and merge changes.'
    },
    {
      icon: '',
      title: 'Architecture Docs',
      description: 'Generate structured architecture documentation with AI. Visualize endpoints, entities, database tables, and UI components as a flow diagram.'
    },
    {
      icon: '',
      title: 'Context Library',
      description: 'Store and retrieve project context. Keep your codebase summaries, architecture docs, and prompts organized and accessible.'
    }
  ];
</script>

<div class="landing-page">
  <div class="hero">
    <div class="logo">
      <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 16 16">
        <path fill="currentColor" d="M9.5 3.25a2.25 2.25 0 1 1 3 2.122V6A2.5 2.5 0 0 1 10 8.5H6a1 1 0 0 0-1 1v1.128a2.251 2.251 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.5 0v1.836A2.5 2.5 0 0 1 6 7h4a1 1 0 0 0 1-1v-.628A2.25 2.25 0 0 1 9.5 3.25m-6 0a.75.75 0 1 0 1.5 0a.75.75 0 0 0-1.5 0m8.25-.75a.75.75 0 1 0 0 1.5a.75.75 0 0 0 0-1.5M4.25 12a.75.75 0 1 0 0 1.5a.75.75 0 0 0 0-1.5"/>
      </svg>
    </div>
    <h1 class="title">Branch Monkey</h1>
    <p class="subtitle">
      Visualize your Git history. Experiment with confidence. Document your architecture.
    </p>
    <button class="cta-button" on:click={onGetStarted}>
      Open App
    </button>
  </div>

  <div class="features">
    <h2 class="features-title">Features</h2>
    <div class="features-grid">
      {#each features as feature}
        <div class="feature-card">
          <div class="feature-icon">{feature.icon}</div>
          <h3 class="feature-title">{feature.title}</h3>
          <p class="feature-description">{feature.description}</p>
        </div>
      {/each}
    </div>
  </div>

  <div class="tech-section">
    <h2 class="tech-title">Built With</h2>
    <div class="tech-stack">
      <span class="tech-badge">Svelte</span>
      <span class="tech-badge">SvelteFlow</span>
      <span class="tech-badge">FastAPI</span>
      <span class="tech-badge">Python</span>
      <span class="tech-badge">Git</span>
    </div>
  </div>

  <footer class="footer">
    <p>Branch Monkey - Git visualization and experimentation tool</p>
  </footer>
</div>

<style>
  .landing-page {
    min-height: 100vh;
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .hero {
    text-align: center;
    padding: 80px 20px 60px;
    max-width: 700px;
    margin: 0 auto;
  }

  .logo {
    color: var(--text-primary);
    margin-bottom: 24px;
  }

  .title {
    font-size: 48px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 16px 0;
    line-height: 1.2;
  }

  .subtitle {
    font-size: 18px;
    color: var(--text-secondary);
    margin: 0 0 32px 0;
    line-height: 1.6;
  }

  .cta-button {
    background: var(--text-primary);
    color: var(--bg-primary);
    border: none;
    padding: 14px 32px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .cta-button:hover {
    opacity: 0.9;
    transform: translateY(-2px);
  }

  .features {
    padding: 60px 20px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .features-title {
    text-align: center;
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 40px 0;
    color: var(--text-primary);
  }

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 24px;
  }

  .feature-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    border-radius: 8px;
    padding: 24px;
    transition: all 0.2s ease;
  }

  .feature-card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-medium);
  }

  .feature-icon {
    font-size: 32px;
    margin-bottom: 12px;
  }

  .feature-title {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: var(--text-primary);
  }

  .feature-description {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.5;
  }

  .tech-section {
    padding: 40px 20px;
    text-align: center;
    border-top: 1px solid var(--border-secondary);
  }

  .tech-title {
    font-size: 18px;
    font-weight: 500;
    margin: 0 0 20px 0;
    color: var(--text-secondary);
  }

  .tech-stack {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .tech-badge {
    background: var(--bg-primary);
    border: 1px solid var(--border-secondary);
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .footer {
    padding: 40px 20px;
    text-align: center;
    border-top: 1px solid var(--border-secondary);
  }

  .footer p {
    margin: 0;
    font-size: 12px;
    color: var(--text-tertiary);
  }

  @media (max-width: 768px) {
    .hero {
      padding: 60px 20px 40px;
    }

    .title {
      font-size: 36px;
    }

    .subtitle {
      font-size: 16px;
    }

    .features-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
