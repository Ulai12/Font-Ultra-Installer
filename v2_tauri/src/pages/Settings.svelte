<script lang="ts">
  import { onMount } from "svelte";
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { currentLang, t } from "../lib/i18n";
  import { theme } from "../lib/theme";
  // Import theme store

  // State
  let animatedBg = true;
  let transparency = "high";

  onMount(() => {
    // Other settings
    animatedBg = localStorage.getItem("settings_animatedBg") === "true";
    transparency = localStorage.getItem("settings_transparency") || "high";
  });

  function updateLanguage(e: Event) {
    const target = e.target as HTMLSelectElement;
    currentLang.set(target.value);
    localStorage.setItem("settings_language", target.value);
  }

  function updateTheme(e: Event) {
    const target = e.target as HTMLSelectElement;
    theme.set(target.value); // Triggers store update -> update CSS attr -> update App
  }

  // Reactive saves
  $: {
    localStorage.setItem("settings_animatedBg", String(animatedBg));
    localStorage.setItem("settings_transparency", transparency);
  }
</script>

<div class="settings-container">
  <div class="header">
    <VariableTitle text="Paramètres" />
  </div>

  <GlassPanel>
    <div class="settings-group">
      <h3>Apparence</h3>

      <div class="setting-item">
        <div class="info">
          <span class="label">{$t("settings.theme")}</span>
          <span class="desc">Changer l'apparence de l'application</span>
        </div>
        <select value={$theme} on:change={updateTheme} class="control">
          <option value="system">Système</option>
          <option value="dark">Sombre</option>
          <option value="light">Clair</option>
        </select>
      </div>

      <div class="setting-item">
        <div class="info">
          <span class="label">Animation Fond</span>
          <span class="desc">Activer les bulles animées</span>
        </div>
        <input type="checkbox" bind:checked={animatedBg} class="toggle" />
      </div>

      <div class="setting-item">
        <div class="info">
          <span class="label">Transparence</span>
          <span class="desc">Intensité de l'effet verre</span>
        </div>
        <select bind:value={transparency} class="control">
          <option value="low">Basse</option>
          <option value="medium">Moyenne</option>
          <option value="high">Haute</option>
        </select>
      </div>
    </div>

    <div class="divider"></div>

    <div class="settings-group">
      <h3>Général</h3>

      <div class="setting-item">
        <div class="info">
          <span class="label">Langue</span>
          <span class="desc">Langue de l'interface</span>
        </div>
        <select value={$currentLang} on:change={updateLanguage} class="control">
          <option value="fr">Français</option>
          <option value="en">English</option>
        </select>
      </div>
    </div>

    <div class="divider"></div>

    <div class="info-block">
      <p>Ultra Font Installer v2.0.0-beta</p>
      <p class="sub">Tauri v2 + SvelteKit</p>
    </div>
  </GlassPanel>
</div>

<style>
  .settings-container {
    padding: 40px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .header {
    margin-bottom: 30px;
  }

  .settings-group h3 {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 20px;
  }

  .setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    background: rgba(255, 255, 255, 0.05);
    padding: 16px;
    border-radius: 12px;
  }

  .info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .label {
    font-weight: 500;
    font-size: 16px;
    color: white;
  }
  .desc {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
  }

  .control {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    outline: none;
    min-width: 120px;
  }

  .toggle {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  .divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 30px 0;
  }

  .info-block {
    text-align: center;
    color: rgba(255, 255, 255, 0.3);
    font-size: 12px;
  }
</style>
