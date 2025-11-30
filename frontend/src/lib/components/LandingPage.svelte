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
      description: 'AI assistants forget everything between sessions. Branch Monkey remembers for them. Store your project knowledge once, use it with any AI - switch between Claude, GPT, or Gemini without losing context.'
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
    {#each features as feature, i}
      <div class="feature-section" class:reverse={i % 2 === 1}>
        <div class="feature-content">
          <h2 class="feature-title">{feature.title}</h2>
          <p class="feature-description">{feature.description}</p>
        </div>
      </div>
    {/each}
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
    max-width: 600px;
    margin: 0 auto;
    padding: 0 20px 60px;
  }

  .feature-section {
    padding: 48px 0;
    border-bottom: 1px solid var(--border-secondary);
  }

  .feature-section:last-child {
    border-bottom: none;
  }

  .feature-content {
    text-align: center;
  }

  .feature-title {
    font-size: 24px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: var(--text-primary);
  }

  .feature-description {
    font-size: 16px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.7;
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
  }
</style>
