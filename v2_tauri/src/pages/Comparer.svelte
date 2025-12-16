<script lang="ts">
  import { convertFileSrc } from "@tauri-apps/api/core";
  import FontSelector from "../components/FontSelector.svelte";
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { t } from "../lib/i18n";

  let leftFont = "Arial.ttf";
  let rightFont = "Times New Roman.ttf";
  let sampleText = "Portez ce vieux whisky au juge blond qui fume";

  // Font loading logic similar to FontCard
  async function loadFont(fontName: string, side: string) {
    const fontId = `compare_${side}`;
    const path = `C:\\Windows\\Fonts\\${fontName}`;
    try {
      const url = convertFileSrc(path);
      const font = new FontFace(fontId, `url('${url}')`);
      await font.load();
      document.fonts.add(font);
      return fontId; // Return the font-family name to use
    } catch (e) {
      console.error("Error loading font", e);
      return "sans-serif";
    }
  }

  let leftFontFamily = "sans-serif";
  let rightFontFamily = "sans-serif";

  $: {
    loadFont(leftFont, "left").then((f) => (leftFontFamily = f));
  }

  $: {
    loadFont(rightFont, "right").then((f) => (rightFontFamily = f));
  }
</script>

<div class="comparer-container">
  <div class="header">
    <VariableTitle text={$t("comparer.title")} />
    <p class="subtitle">{$t("comparer.subtitle")}</p>
  </div>

  <GlassPanel>
    <div class="controls">
      <input
        type="text"
        bind:value={sampleText}
        placeholder={$t("comparer.placeholder_text")}
        class="text-input"
      />
    </div>

    <div class="split-view">
      <div class="pane left">
        <FontSelector bind:selectedFont={leftFont} />
        <div class="preview-area" style="font-family: {leftFontFamily}">
          {sampleText}
        </div>
      </div>

      <div class="divider"></div>

      <div class="pane right">
        <FontSelector bind:selectedFont={rightFont} />
        <div class="preview-area" style="font-family: {rightFontFamily}">
          {sampleText}
        </div>
      </div>
    </div>
  </GlassPanel>
</div>

<style>
  .comparer-container {
    padding: 40px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .header {
    margin-bottom: 20px;
  }

  .controls {
    margin-bottom: 20px;
  }

  .text-input {
    width: 100%;
    padding: 12px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    font-size: 16px;
    outline: none;
  }

  .split-view {
    display: flex;
    height: 60vh;
    gap: 20px;
  }

  .pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .divider {
    width: 1px;
    background: rgba(255, 255, 255, 0.1);
  }

  .preview-area {
    flex: 1;
    font-size: 32px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 8px;
    overflow-y: auto;
    word-break: break-word;
    white-space: pre-wrap;
    line-height: 1.4;
  }
</style>
