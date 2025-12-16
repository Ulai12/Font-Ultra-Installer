<script lang="ts">
  import { convertFileSrc, invoke } from "@tauri-apps/api/core";
  import FontSelector from "../components/FontSelector.svelte";
  import GlassPanel from "../components/GlassPanel.svelte";
  import GlyphGrid from "../components/GlyphGrid.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { t } from "../lib/i18n";

  let selectedFont = "Arial";
  let fontFamily = "sans-serif";
  let chars: number[] = [];
  let isLoading = false;

  async function loadFontData(fontName: string) {
    if (!fontName) return;
    isLoading = true;
    chars = []; // Reset

    const path = `C:\\Windows\\Fonts\\${fontName}`; // Assumption

    try {
      // 1. Load Font Face for display
      const url = convertFileSrc(path);
      const fontId = `inspector_${fontName.replace(/[^a-zA-Z0-9]/g, "_")}`;
      const font = new FontFace(fontId, `url('${url}')`);
      await font.load();
      document.fonts.add(font);
      fontFamily = fontId;

      // 2. Fetch accessible chars from backend
      // We pass the full path. If FontSelector returns just filename 'Arial', we map it.
      // Ideally FontSelector should return path object, but for now we follow convention.
      chars = await invoke<number[]>("get_font_chars", { path });
    } catch (e) {
      console.error("Error loading inspector data", e);
    } finally {
      isLoading = false;
    }
  }

  $: loadFontData(selectedFont);
</script>

<div class="inspector-container">
  <div class="header">
    <VariableTitle text={$t("inspector.title")} />
    <p class="subtitle">{$t("inspector.subtitle")}</p>
  </div>

  <GlassPanel>
    <div class="toolbar">
      <FontSelector bind:selectedFont />
      {#if isLoading}
        <span class="loading">{$t("inspector.loading")}</span>
      {/if}
    </div>

    <div class="content-area">
      {#if chars.length > 0}
        <GlyphGrid {chars} {fontFamily} />
      {:else if !isLoading}
        <div class="empty">{$t("inspector.empty")}</div>
      {/if}
    </div>
  </GlassPanel>
</div>

<style>
  .inspector-container {
    padding: 40px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .header {
    margin-bottom: 20px;
  }

  .toolbar {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .loading {
    color: rgba(255, 255, 255, 0.5);
    font-style: italic;
  }

  .content-area {
    flex: 1;
    overflow: hidden;
    min-height: 400px;
  }

  .empty {
    text-align: center;
    padding: 40px;
    color: rgba(255, 255, 255, 0.3);
  }
</style>
