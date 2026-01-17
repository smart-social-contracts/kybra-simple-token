<script>
  import "../index.scss";
  
  const version = __APP_VERSION__ || "dev";
  const commitHash = __COMMIT_HASH__ || "local";
  const buildTime = __BUILD_TIME__ || new Date().toISOString();
  const repoUrl = "https://github.com/smart-social-contracts/kybra-simple-token";
</script>

<div class="app-container">
  <slot />
  
  <footer class="app-footer">
    <div class="footer-row ic-branding">
      <svg width="24" height="24" viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M64 128C99.3462 128 128 99.3462 128 64C128 28.6538 99.3462 0 64 0C28.6538 0 0 28.6538 0 64C0 99.3462 28.6538 128 64 128Z" fill="url(#paint0_linear)"/>
        <path d="M54.5 42C61.4036 42 67 47.5964 67 54.5C67 61.4036 61.4036 67 54.5 67C47.5964 67 42 61.4036 42 54.5C42 47.5964 47.5964 42 54.5 42Z" fill="white"/>
        <path d="M73.5 61C80.4036 61 86 66.5964 86 73.5C86 80.4036 80.4036 86 73.5 86C66.5964 86 61 80.4036 61 73.5C61 66.5964 66.5964 61 73.5 61Z" fill="white"/>
        <defs>
          <linearGradient id="paint0_linear" x1="64" y1="0" x2="64" y2="128" gradientUnits="userSpaceOnUse">
            <stop stop-color="#F15A24"/>
            <stop offset="0.21" stop-color="#FBB03B"/>
            <stop offset="0.52" stop-color="#ED1E79"/>
            <stop offset="0.9" stop-color="#522785"/>
          </linearGradient>
        </defs>
      </svg>
      <span>Built on the Internet Computer</span>
    </div>
    
    <a href={repoUrl} target="_blank" rel="noopener noreferrer" class="footer-row github-link">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
      </svg>
    </a>
    
    <div class="footer-row version-info">
      Simple Token {version} ({commitHash}) - {buildTime}
    </div>
  </footer>
</div>

<style>
  .app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .app-footer {
    margin-top: auto;
    padding: 24px;
    text-align: center;
    border-top: 1px solid var(--color-border);
    background: var(--color-bg-secondary);
  }

  .footer-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  .footer-row:last-child {
    margin-bottom: 0;
  }

  .ic-branding {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
  }

  .github-link {
    color: var(--color-text-tertiary);
    text-decoration: none;
    transition: color 0.15s;
  }

  .github-link:hover {
    color: var(--color-text-primary);
  }

  .version-info {
    color: var(--color-text-tertiary);
    font-size: 0.75rem;
    font-family: monospace;
  }
</style>
