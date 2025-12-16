<script lang="ts">
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { t } from "../lib/i18n";
</script>

<div class="about-container">
  <div class="header">
    <VariableTitle text={$t("about.title")} />
  </div>

  <GlassPanel>
    <div class="content">
      <div class="logo">
        <!-- Simple SVG Logo Placeholder -->
        <svg viewBox="0 0 100 100" width="80" height="80">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="#00c2ff"
            stroke-width="5"
          />
          <text
            x="50"
            y="65"
            text-anchor="middle"
            fill="white"
            font-size="50"
            font-weight="bold"
            font-family="Arial">U</text
          >
        </svg>
      </div>

      <h2>Ultra Font Installer</h2>
      <span class="version">Version 2.0.0 (Tauri Edition)</span>

      <p class="desc">
        {$t("about.desc")}
      </p>

      <div class="credits">
        <p>{$t("about.developed_by")} <strong>Ulai</strong></p>
        <p>{$t("about.powered_by")}</p>
      </div>

      <div class="links">
        <a href="https://github.com/ulai/ultra-font-installer" target="_blank"
          >GitHub</a
        >
        <span class="sep">•</span>
        <a href="https://example.com" target="_blank">{$t("about.website")}</a>
      </div>
    </div>
  </GlassPanel>
</div>

<style>
  .about-container {
    padding: 40px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 40px 20px;
    color: white;
  }

  .logo {
    margin-bottom: 20px;
  }

  h2 {
    font-size: 28px;
    margin: 0 0 8px 0;
    background: linear-gradient(45deg, #fff, #00c2ff);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .version {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.1);
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 30px;
  }

  .desc {
    font-size: 16px;
    line-height: 1.6;
    max-width: 400px;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 40px;
  }

  .credits {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
    margin-bottom: 30px;
  }

  .credits strong {
    color: white;
  }

  .links {
    display: flex;
    gap: 15px;
    font-size: 14px;
  }

  .links a {
    color: #00c2ff;
    text-decoration: none;
    transition: color 0.2s;
  }

  .links a:hover {
    color: white;
  }
  .sep {
    color: rgba(255, 255, 255, 0.2);
  }
</style>
