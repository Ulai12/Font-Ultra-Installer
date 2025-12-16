<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import FontSelector from "../components/FontSelector.svelte";
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { t } from "../lib/i18n";

  let selectedFont = "Arial";
  let suggestions: { font: string; reason: string; previewUrl?: string }[] = [];
  let allFonts: string[] = [];

  // API Key shared with simple logic
  const API_KEY = "AIzaSyCBB7xqGzhXyOwx3785foT1445WZhq7gMY";
  let googleFontCategories: Record<string, string> = {};

  // Heuristics
  const SERIF_REGEX = /serif|times|garamond|baskerville|georgia/i;
  const SANS_REGEX = /sans|arial|helvetica|calibri|verdana|tahoma/i;
  const MONO_REGEX = /mono|courier|console|code/i;

  async function loadGoogleFontCategories() {
    try {
      const res = await fetch(
        `https://www.googleapis.com/webfonts/v1/webfonts?key=${API_KEY}&fields=items(family,category)`
      );
      const data = await res.json();
      if (data.items) {
        data.items.forEach((item: any) => {
          googleFontCategories[item.family.toLowerCase()] = item.category;
        });
      }
    } catch (e) {
      console.warn(
        "Could not load Google Fonts metadata for pairing categorization (offline?)"
      );
    }
  }

  // Load categories on mount implicitly if needed, or lazy load
  loadGoogleFontCategories();

  function getCategory(fontName: string): string {
    const lower = fontName.toLowerCase();
    // 1. Check API data
    if (googleFontCategories[lower]) {
      return googleFontCategories[lower]; // 'serif', 'sans-serif', 'display', 'handwriting', 'monospace'
    }

    // 2. Fallback to Regex
    if (SERIF_REGEX.test(lower)) return "serif";
    if (SANS_REGEX.test(lower)) return "sans-serif";
    if (MONO_REGEX.test(lower)) return "monospace";

    return "unknown";
  }

  async function generateSuggestions() {
    if (allFonts.length === 0) {
      allFonts = await invoke<string[]>("get_installed_fonts");
    }

    const mainCategory = getCategory(selectedFont);

    let results: { font: string; reason: string }[] = [];

    // Logic based on category contrast
    if (mainCategory === "serif") {
      // Suggest Sans-Serif
      const matches = allFonts.filter(
        (f) =>
          getCategory(f) === "sans-serif" &&
          !f.toLowerCase().includes(selectedFont.toLowerCase())
      );
      matches
        .slice(0, 5)
        .forEach((f) =>
          results.push({
            font: f,
            reason: "Contraste Serif / Sans-Serif (Idéal)",
          })
        );
    } else if (mainCategory === "sans-serif") {
      // Suggest Serif or Display
      const matches = allFonts.filter(
        (f) =>
          (getCategory(f) === "serif" || getCategory(f) === "display") &&
          !f.toLowerCase().includes(selectedFont.toLowerCase())
      );
      matches
        .slice(0, 5)
        .forEach((f) =>
          results.push({ font: f, reason: "Contraste pour Titres" })
        );
    } else if (mainCategory === "display" || mainCategory === "handwriting") {
      // Suggest clean Sans-Serif for readability
      const matches = allFonts.filter(
        (f) =>
          getCategory(f) === "sans-serif" &&
          !f.toLowerCase().includes(selectedFont.toLowerCase())
      );
      matches
        .slice(0, 5)
        .forEach((f) =>
          results.push({ font: f, reason: "Équilibre Décoratif / Lisible" })
        );
    } else {
      // Fallback default logic if unknown
      const sans = allFonts.filter((f) => SANS_REGEX.test(f));
      sans
        .slice(0, 3)
        .forEach((f) =>
          results.push({ font: f, reason: "Suggestion Standard" })
        );
    }

    // Add favorites/popular fallback if empty
    if (results.length < 3) {
      const popular = [
        "Arial",
        "Verdana",
        "Georgia",
        "Impact",
        "Comic Sans MS",
      ];
      popular.forEach((p) => {
        if (
          allFonts.find((f) => f.includes(p)) &&
          !results.find((r) => r.font.includes(p))
        ) {
          results.push({ font: p, reason: "Choix Populaire (Fallback)" });
        }
      });
    }

    suggestions = results.slice(0, 5);
  }
</script>

<div class="pairing-container">
  <div class="header">
    <VariableTitle text={$t("pairing.title")} />
    <p class="subtitle">{$t("pairing.subtitle")}</p>
  </div>

  <GlassPanel>
    <div class="controls">
      <div class="selector-group">
        <span class="label">{$t("pairing.main_font")}</span>
        <FontSelector bind:selectedFont on:change={generateSuggestions} />
      </div>
      <button class="action-btn" on:click={generateSuggestions}
        >{$t("pairing.generate_btn")}</button
      >
    </div>

    <div class="suggestions-list">
      {#each suggestions as suggest, i}
        <div class="pairing-card">
          <div class="card-header">
            <span class="rank">#{i + 1}</span>
            <span class="reason">{suggest.reason}</span>
          </div>

          <div class="preview-block">
            <div
              class="title-preview"
              style="font-family: '{selectedFont}', sans-serif"
            >
              {selectedFont} (Titre)
            </div>
            <div
              class="body-preview"
              style="font-family: '{suggest.font}', sans-serif"
            >
              La vif zéphyr jubile sur les kumquats du clown gracieux. ({suggest.font})
            </div>
          </div>
        </div>
      {:else}
        <div class="empty">
          {$t("pairing.empty")}
        </div>
      {/each}
    </div>
  </GlassPanel>
</div>

<style>
  .pairing-container {
    padding: 40px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .header {
    margin-bottom: 20px;
  }
  .subtitle {
    color: rgba(255, 255, 255, 0.6);
    margin-top: 4px;
  }

  .controls {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
    background: rgba(255, 255, 255, 0.05);
    padding: 16px;
    border-radius: 12px;
  }

  .selector-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .action-btn {
    background: #00cc6a;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
  }

  .suggestions-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow-y: auto;
    flex: 1;
    padding-right: 10px;
  }

  .pairing-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
  }

  .card-header {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
    align-items: center;
  }

  .rank {
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
  }

  .reason {
    color: #00cc6a;
    font-size: 13px;
  }

  .title-preview {
    font-size: 32px;
    margin-bottom: 8px;
    color: white;
  }

  .body-preview {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.5;
  }

  .empty {
    text-align: center;
    padding: 40px;
    opacity: 0.4;
    font-style: italic;
  }
</style>
