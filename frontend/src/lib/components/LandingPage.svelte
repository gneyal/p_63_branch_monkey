<script>
  import { push } from 'svelte-spa-router';

  function onGetStarted() {
    push('/');
  }
</script>

<div class="landing-page">
  <div class="hero">
    <h1 class="title">
      <span class="monkey">🐵</span>
      Branch Monkey
    </h1>
    <p class="subtitle">
      Visualize your Git history. Experiment with confidence.
    </p>
    <button class="cta-button" on:click={onGetStarted}>
      Get Started →
    </button>
  </div>
</div>

<style>
  .landing-page {
    min-height: 100vh;
    background: #121212;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }

  .hero {
    text-align: center;
    max-width: 600px;
  }

  .monkey {
    font-size: 80px;
    display: block;
    margin-bottom: 24px;
  }

  .title {
    font-size: 48px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 16px 0;
    line-height: 1.2;
  }

  .subtitle {
    font-size: 20px;
    color: #b0b0b0;
    margin: 0 0 40px 0;
    line-height: 1.5;
  }

  .cta-button {
    background: #2196f3;
    color: white;
    border: none;
    padding: 14px 32px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .cta-button:hover {
    background: #1976d2;
    transform: translateY(-2px);
  }

  @media (max-width: 768px) {
    .monkey {
      font-size: 64px;
    }

    .title {
      font-size: 36px;
    }

    .subtitle {
      font-size: 18px;
    }
  }
</style>
