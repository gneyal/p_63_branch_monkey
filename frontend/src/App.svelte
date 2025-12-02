<script>
  import Router from 'svelte-spa-router';
  import LandingPage from './lib/components/LandingPage.svelte';
  import MainApp from './lib/components/MainApp.svelte';
  import TasksPage from './lib/components/TasksPage.svelte';
  import PromptsPage from './lib/components/PromptsPage.svelte';
  import ArchitecturePage from './lib/components/ArchitecturePage.svelte';
  import TestsPage from './lib/components/TestsPage.svelte';
  import InstallPage from './lib/components/InstallPage.svelte';
  import { push } from 'svelte-spa-router';

  const routes = {
    '/': LandingPage,
    '/home': LandingPage,
    '/commits': MainApp,
    '/tasks': TasksPage,
    '/prompts': PromptsPage,
    '/architecture': ArchitecturePage,
    '/tests': TestsPage,
    '/install': InstallPage,
  };

  function handleGetStarted() {
    push('/commits');
  }
</script>

<Router {routes} />

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  /* Gruvbox Dark - warm retro theme */
  :global(:root[data-theme="gruvbox-dark"]) {
    --bg-primary: #282828;
    --bg-secondary: #1d2021;
    --bg-hover: #3c3836;
    --text-primary: #ebdbb2;
    --text-secondary: #bdae93;
    --text-tertiary: #928374;
    --border-primary: #504945;
    --border-secondary: #3c3836;
    --border-hover: #665c54;
    --accent-primary: #fabd2f;
    --accent-secondary: #d79921;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #83a598;
    --branch-experiment: #b8bb26;
    --branch-feature: #d3869b;
    --branch-fix: #fb4934;
    --branch-default: #a89984;
  }

  /* Gruvbox Light */
  :global(:root[data-theme="gruvbox-light"]) {
    --bg-primary: #fbf1c7;
    --bg-secondary: #f2e5bc;
    --bg-hover: #ebdbb2;
    --text-primary: #3c3836;
    --text-secondary: #504945;
    --text-tertiary: #7c6f64;
    --border-primary: #d5c4a1;
    --border-secondary: #ebdbb2;
    --border-hover: #bdae93;
    --accent-primary: #d79921;
    --accent-secondary: #b57614;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #458588;
    --branch-experiment: #79740e;
    --branch-feature: #8f3f71;
    --branch-fix: #cc241d;
    --branch-default: #7c6f64;
  }

  /* Nord - arctic blue theme */
  :global(:root[data-theme="nord"]) {
    --bg-primary: #2e3440;
    --bg-secondary: #242933;
    --bg-hover: #3b4252;
    --text-primary: #eceff4;
    --text-secondary: #d8dee9;
    --text-tertiary: #a3b1c7;
    --border-primary: #4c566a;
    --border-secondary: #3b4252;
    --border-hover: #5c6a82;
    --accent-primary: #88c0d0;
    --accent-secondary: #81a1c1;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #81a1c1;
    --branch-experiment: #a3be8c;
    --branch-feature: #b48ead;
    --branch-fix: #bf616a;
    --branch-default: #d8dee9;
  }

  /* Dracula - purple dark theme */
  :global(:root[data-theme="dracula"]) {
    --bg-primary: #282a36;
    --bg-secondary: #21222c;
    --bg-hover: #44475a;
    --text-primary: #f8f8f2;
    --text-secondary: #d0d0d0;
    --text-tertiary: #6272a4;
    --border-primary: #44475a;
    --border-secondary: #363848;
    --border-hover: #6272a4;
    --accent-primary: #bd93f9;
    --accent-secondary: #ff79c6;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #8be9fd;
    --branch-experiment: #50fa7b;
    --branch-feature: #bd93f9;
    --branch-fix: #ff5555;
    --branch-default: #f8f8f2;
  }

  /* One Dark - Atom theme */
  :global(:root[data-theme="one-dark"]) {
    --bg-primary: #282c34;
    --bg-secondary: #21252b;
    --bg-hover: #2c313a;
    --text-primary: #abb2bf;
    --text-secondary: #9da5b4;
    --text-tertiary: #5c6370;
    --border-primary: #3e4451;
    --border-secondary: #2c313a;
    --border-hover: #4b5363;
    --accent-primary: #61afef;
    --accent-secondary: #528bff;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #61afef;
    --branch-experiment: #98c379;
    --branch-feature: #c678dd;
    --branch-fix: #e06c75;
    --branch-default: #abb2bf;
  }

  /* Solarized Dark */
  :global(:root[data-theme="solarized-dark"]) {
    --bg-primary: #002b36;
    --bg-secondary: #073642;
    --bg-hover: #094555;
    --text-primary: #839496;
    --text-secondary: #93a1a1;
    --text-tertiary: #657b83;
    --border-primary: #094555;
    --border-secondary: #073642;
    --border-hover: #586e75;
    --accent-primary: #2aa198;
    --accent-secondary: #268bd2;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #268bd2;
    --branch-experiment: #859900;
    --branch-feature: #6c71c4;
    --branch-fix: #dc322f;
    --branch-default: #93a1a1;
  }

  /* Solarized Light */
  :global(:root[data-theme="solarized-light"]) {
    --bg-primary: #fdf6e3;
    --bg-secondary: #eee8d5;
    --bg-hover: #e4ddc8;
    --text-primary: #657b83;
    --text-secondary: #586e75;
    --text-tertiary: #93a1a1;
    --border-primary: #d3cbb7;
    --border-secondary: #eee8d5;
    --border-hover: #93a1a1;
    --accent-primary: #2aa198;
    --accent-secondary: #268bd2;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #268bd2;
    --branch-experiment: #859900;
    --branch-feature: #6c71c4;
    --branch-fix: #dc322f;
    --branch-default: #586e75;
  }

  /* Monokai - classic dark theme */
  :global(:root[data-theme="monokai"]) {
    --bg-primary: #272822;
    --bg-secondary: #1e1f1a;
    --bg-hover: #3e3d32;
    --text-primary: #f8f8f2;
    --text-secondary: #cfcfc2;
    --text-tertiary: #75715e;
    --border-primary: #3e3d32;
    --border-secondary: #2d2e27;
    --border-hover: #525246;
    --accent-primary: #a6e22e;
    --accent-secondary: #f92672;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #66d9ef;
    --branch-experiment: #a6e22e;
    --branch-feature: #ae81ff;
    --branch-fix: #f92672;
    --branch-default: #f8f8f2;
  }

  /* Tokyo Night - Japanese neon theme */
  :global(:root[data-theme="tokyo-night"]) {
    --bg-primary: #1a1b26;
    --bg-secondary: #16161e;
    --bg-hover: #24283b;
    --text-primary: #c0caf5;
    --text-secondary: #a9b1d6;
    --text-tertiary: #565f89;
    --border-primary: #292e42;
    --border-secondary: #1f2335;
    --border-hover: #3b4261;
    --accent-primary: #7aa2f7;
    --accent-secondary: #bb9af7;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #7aa2f7;
    --branch-experiment: #9ece6a;
    --branch-feature: #bb9af7;
    --branch-fix: #f7768e;
    --branch-default: #a9b1d6;
  }

  /* Catppuccin Mocha - pastel dark theme */
  :global(:root[data-theme="catppuccin"]) {
    --bg-primary: #1e1e2e;
    --bg-secondary: #181825;
    --bg-hover: #313244;
    --text-primary: #cdd6f4;
    --text-secondary: #bac2de;
    --text-tertiary: #6c7086;
    --border-primary: #45475a;
    --border-secondary: #313244;
    --border-hover: #585b70;
    --accent-primary: #cba6f7;
    --accent-secondary: #f5c2e7;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #89b4fa;
    --branch-experiment: #a6e3a1;
    --branch-feature: #cba6f7;
    --branch-fix: #f38ba8;
    --branch-default: #bac2de;
  }

  /* Everforest - soft green theme */
  :global(:root[data-theme="everforest"]) {
    --bg-primary: #2d353b;
    --bg-secondary: #272e33;
    --bg-hover: #343f44;
    --text-primary: #d3c6aa;
    --text-secondary: #9da9a0;
    --text-tertiary: #7a8478;
    --border-primary: #414b50;
    --border-secondary: #343f44;
    --border-hover: #4f585e;
    --accent-primary: #a7c080;
    --accent-secondary: #83c092;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #7fbbb3;
    --branch-experiment: #a7c080;
    --branch-feature: #d699b6;
    --branch-fix: #e67e80;
    --branch-default: #9da9a0;
  }

  /* Rose Pine - elegant dark theme */
  :global(:root[data-theme="rose-pine"]) {
    --bg-primary: #191724;
    --bg-secondary: #1f1d2e;
    --bg-hover: #26233a;
    --text-primary: #e0def4;
    --text-secondary: #908caa;
    --text-tertiary: #6e6a86;
    --border-primary: #403d52;
    --border-secondary: #26233a;
    --border-hover: #524f67;
    --accent-primary: #ebbcba;
    --accent-secondary: #f6c177;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #9ccfd8;
    --branch-experiment: #31748f;
    --branch-feature: #c4a7e7;
    --branch-fix: #eb6f92;
    --branch-default: #908caa;
  }

  /* Kanagawa - Japanese ink painting */
  :global(:root[data-theme="kanagawa"]) {
    --bg-primary: #1f1f28;
    --bg-secondary: #16161d;
    --bg-hover: #2a2a37;
    --text-primary: #dcd7ba;
    --text-secondary: #c8c093;
    --text-tertiary: #727169;
    --border-primary: #363646;
    --border-secondary: #2a2a37;
    --border-hover: #54546d;
    --accent-primary: #7e9cd8;
    --accent-secondary: #957fb8;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #7e9cd8;
    --branch-experiment: #98bb6c;
    --branch-feature: #957fb8;
    --branch-fix: #e82424;
    --branch-default: #c8c093;
  }

  /* Nightfox - blue arctic night */
  :global(:root[data-theme="nightfox"]) {
    --bg-primary: #192330;
    --bg-secondary: #131a24;
    --bg-hover: #212e3f;
    --text-primary: #cdcecf;
    --text-secondary: #aeafb0;
    --text-tertiary: #71839b;
    --border-primary: #2b3b51;
    --border-secondary: #212e3f;
    --border-hover: #39506d;
    --accent-primary: #719cd6;
    --accent-secondary: #9d79d6;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #719cd6;
    --branch-experiment: #81b29a;
    --branch-feature: #9d79d6;
    --branch-fix: #c94f6d;
    --branch-default: #aeafb0;
  }

  /* Material - Google material dark */
  :global(:root[data-theme="material"]) {
    --bg-primary: #263238;
    --bg-secondary: #1e272c;
    --bg-hover: #37474f;
    --text-primary: #eeffff;
    --text-secondary: #b0bec5;
    --text-tertiary: #607d8b;
    --border-primary: #37474f;
    --border-secondary: #2c3940;
    --border-hover: #546e7a;
    --accent-primary: #82aaff;
    --accent-secondary: #c792ea;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #82aaff;
    --branch-experiment: #c3e88d;
    --branch-feature: #c792ea;
    --branch-fix: #ff5370;
    --branch-default: #b0bec5;
  }

  /* Palenight - soft purple night */
  :global(:root[data-theme="palenight"]) {
    --bg-primary: #292d3e;
    --bg-secondary: #1f2233;
    --bg-hover: #34394e;
    --text-primary: #a6accd;
    --text-secondary: #8087a2;
    --text-tertiary: #676e95;
    --border-primary: #3a3f58;
    --border-secondary: #34394e;
    --border-hover: #4e5579;
    --accent-primary: #c792ea;
    --accent-secondary: #89ddff;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #82aaff;
    --branch-experiment: #c3e88d;
    --branch-feature: #c792ea;
    --branch-fix: #ff5370;
    --branch-default: #8087a2;
  }

  /* Ayu Dark - minimal dark */
  :global(:root[data-theme="ayu-dark"]) {
    --bg-primary: #0d1017;
    --bg-secondary: #0a0e14;
    --bg-hover: #151a22;
    --text-primary: #bfbdb6;
    --text-secondary: #8b8680;
    --text-tertiary: #565b66;
    --border-primary: #1c212b;
    --border-secondary: #151a22;
    --border-hover: #2d3640;
    --accent-primary: #e6b450;
    --accent-secondary: #ffb454;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.6);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.7);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.8);
    --branch-main: #59c2ff;
    --branch-experiment: #aad94c;
    --branch-feature: #d2a6ff;
    --branch-fix: #f07178;
    --branch-default: #8b8680;
  }

  /* GitHub Dark */
  :global(:root[data-theme="github-dark"]) {
    --bg-primary: #0d1117;
    --bg-secondary: #010409;
    --bg-hover: #161b22;
    --text-primary: #c9d1d9;
    --text-secondary: #8b949e;
    --text-tertiary: #6e7681;
    --border-primary: #30363d;
    --border-secondary: #21262d;
    --border-hover: #484f58;
    --accent-primary: #58a6ff;
    --accent-secondary: #1f6feb;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #58a6ff;
    --branch-experiment: #3fb950;
    --branch-feature: #a371f7;
    --branch-fix: #f85149;
    --branch-default: #8b949e;
  }

  /* Horizon - warm sunset theme */
  :global(:root[data-theme="horizon"]) {
    --bg-primary: #1c1e26;
    --bg-secondary: #16161c;
    --bg-hover: #232530;
    --text-primary: #d5d8da;
    --text-secondary: #b0b3b5;
    --text-tertiary: #6c6f93;
    --border-primary: #2e303e;
    --border-secondary: #232530;
    --border-hover: #3d3f52;
    --accent-primary: #e95678;
    --accent-secondary: #fab795;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #25b0bc;
    --branch-experiment: #09f7a0;
    --branch-feature: #b877db;
    --branch-fix: #e95678;
    --branch-default: #b0b3b5;
  }

  /* Iceberg - cool blue theme */
  :global(:root[data-theme="iceberg"]) {
    --bg-primary: #161821;
    --bg-secondary: #0f1117;
    --bg-hover: #1e2132;
    --text-primary: #c6c8d1;
    --text-secondary: #9a9ca5;
    --text-tertiary: #6b7089;
    --border-primary: #2a2e3f;
    --border-secondary: #1e2132;
    --border-hover: #3d435c;
    --accent-primary: #84a0c6;
    --accent-secondary: #89b8c2;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.5);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.6);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.7);
    --branch-main: #84a0c6;
    --branch-experiment: #b4be82;
    --branch-feature: #a093c7;
    --branch-fix: #e27878;
    --branch-default: #9a9ca5;
  }

  /* One Light */
  :global(:root[data-theme="one-light"]) {
    --bg-primary: #fafafa;
    --bg-secondary: #f0f0f0;
    --bg-hover: #e5e5e6;
    --text-primary: #383a42;
    --text-secondary: #4f525e;
    --text-tertiary: #a0a1a7;
    --border-primary: #d4d4d4;
    --border-secondary: #e5e5e6;
    --border-hover: #b4b4b4;
    --accent-primary: #4078f2;
    --accent-secondary: #0184bc;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #4078f2;
    --branch-experiment: #50a14f;
    --branch-feature: #a626a4;
    --branch-fix: #e45649;
    --branch-default: #4f525e;
  }

  /* GitHub Light */
  :global(:root[data-theme="github-light"]) {
    --bg-primary: #ffffff;
    --bg-secondary: #f6f8fa;
    --bg-hover: #f3f4f6;
    --text-primary: #24292f;
    --text-secondary: #57606a;
    --text-tertiary: #8c959f;
    --border-primary: #d0d7de;
    --border-secondary: #e1e4e8;
    --border-hover: #afb8c1;
    --accent-primary: #0969da;
    --accent-secondary: #0550ae;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.1);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.15);
    --branch-main: #0969da;
    --branch-experiment: #1a7f37;
    --branch-feature: #8250df;
    --branch-fix: #cf222e;
    --branch-default: #57606a;
  }

  /* Ayu Light */
  :global(:root[data-theme="ayu-light"]) {
    --bg-primary: #fafafa;
    --bg-secondary: #f3f3f3;
    --bg-hover: #e8e8e8;
    --text-primary: #5c6166;
    --text-secondary: #787b80;
    --text-tertiary: #abb0b6;
    --border-primary: #d8d8d8;
    --border-secondary: #e8e8e8;
    --border-hover: #c0c0c0;
    --accent-primary: #ff9940;
    --accent-secondary: #f2ae49;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.06);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.1);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.15);
    --branch-main: #399ee6;
    --branch-experiment: #86b300;
    --branch-feature: #a37acc;
    --branch-fix: #f51818;
    --branch-default: #787b80;
  }

  /* Rose Pine Dawn - light rose theme */
  :global(:root[data-theme="rose-pine-dawn"]) {
    --bg-primary: #faf4ed;
    --bg-secondary: #fffaf3;
    --bg-hover: #f2e9de;
    --text-primary: #575279;
    --text-secondary: #6e6a86;
    --text-tertiary: #9893a5;
    --border-primary: #dfdad9;
    --border-secondary: #f2e9de;
    --border-hover: #cecacd;
    --accent-primary: #d7827e;
    --accent-secondary: #ea9d34;
    --shadow-small: 0 1px 3px rgba(87, 82, 121, 0.08);
    --shadow-medium: 0 2px 6px rgba(87, 82, 121, 0.12);
    --shadow-large: 0 4px 12px rgba(87, 82, 121, 0.16);
    --branch-main: #56949f;
    --branch-experiment: #286983;
    --branch-feature: #907aa9;
    --branch-fix: #b4637a;
    --branch-default: #6e6a86;
  }

  /* Legacy fallbacks for 'light' and 'dark' */
  :global(:root[data-theme="light"]) {
    --bg-primary: #fbf1c7;
    --bg-secondary: #f2e5bc;
    --bg-hover: #ebdbb2;
    --text-primary: #3c3836;
    --text-secondary: #504945;
    --text-tertiary: #7c6f64;
    --border-primary: #d5c4a1;
    --border-secondary: #ebdbb2;
    --border-hover: #bdae93;
    --accent-primary: #d79921;
    --accent-secondary: #b57614;
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.08);
    --shadow-medium: 0 2px 6px rgba(0, 0, 0, 0.12);
    --shadow-large: 0 4px 12px rgba(0, 0, 0, 0.16);
    --branch-main: #458588;
    --branch-experiment: #79740e;
    --branch-feature: #8f3f71;
    --branch-fix: #cc241d;
    --branch-default: #7c6f64;
  }

  :global(:root[data-theme="dark"]) {
    --bg-primary: #282828;
    --bg-secondary: #1d2021;
    --bg-hover: #3c3836;
    --text-primary: #ebdbb2;
    --text-secondary: #bdae93;
    --text-tertiary: #928374;
    --border-primary: #504945;
    --border-secondary: #3c3836;
    --border-hover: #665c54;
    --accent-primary: #fabd2f;
    --accent-secondary: #d79921;
    --shadow-small: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-medium: 0 2px 4px rgba(0, 0, 0, 0.5);
    --shadow-large: 0 4px 8px rgba(0, 0, 0, 0.6);
    --branch-main: #83a598;
    --branch-experiment: #b8bb26;
    --branch-feature: #d3869b;
    --branch-fix: #fb4934;
    --branch-default: #a89984;
  }

  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  :global(*) {
    box-sizing: border-box;
  }
</style>
