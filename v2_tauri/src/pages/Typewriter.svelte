<script lang="ts">
  import { convertFileSrc } from "@tauri-apps/api/core";
  import { onMount } from "svelte";
  import FontSelector from "../components/FontSelector.svelte";
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { t } from "../lib/i18n";

  let text = "";
  let selectedFont = "Courier New";
  let fontSize = 24;
  let align = "left"; // 'left' | 'center' | 'right'
  let soundEnabled = true;

  let audioContext: AudioContext;
  let fontRef: string = "monospace";

  onMount(() => {
    audioContext = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
    loadFont(selectedFont);
  });

  async function loadFont(fontName: string) {
    const path = `C:\\Windows\\Fonts\\${fontName}`; // Simple assumption, reliable logic should be robust
    try {
      const url = convertFileSrc(path);
      const fontId = `typewriter_${fontName.replace(/\s+/g, "_")}`;
      const font = new FontFace(fontId, `url('${url}')`);
      await font.load();
      document.fonts.add(font);
      fontRef = fontId;
    } catch (e) {
      console.error("Error loading font", e);
      fontRef = "monospace";
    }
  }

  function playKeySound() {
    if (!soundEnabled || !audioContext) return;

    // Simple mechanical click synthesis
    const t = audioContext.currentTime;
    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();

    osc.frequency.setValueAtTime(800, t);
    osc.frequency.exponentialRampToValueAtTime(100, t + 0.05);

    gain.gain.setValueAtTime(0.3, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.05);

    osc.connect(gain);
    gain.connect(audioContext.destination);

    osc.start(t);
    osc.stop(t + 0.05);
  }

  function handleInput(e: Event) {
    if ((e as InputEvent).inputType !== "deleteContentBackward") {
      playKeySound();
    }
  }

  $: loadFont(selectedFont);
</script>

<div class="typewriter-container">
  <div class="header">
    <VariableTitle text={$t("typewriter.title")} />
    <p class="subtitle">{$t("typewriter.subtitle")}</p>
  </div>

  <GlassPanel>
    <div class="toolbar">
      <div class="group">
        <FontSelector bind:selectedFont />
      </div>

      <label class="group">
        <span>{$t("typewriter.size")}: {fontSize}px</span>
        <input type="range" min="12" max="72" bind:value={fontSize} />
      </label>

      <div class="group toggle-group">
        <button
          class:active={align === "left"}
          on:click={() => (align = "left")}
        >
          {$t("typewriter.align_left")}
        </button>
        <button
          class:active={align === "center"}
          on:click={() => (align = "center")}
        >
          {$t("typewriter.align_center")}
        </button>
      </div>

      <div class="group">
        <label class="checkbox">
          <input type="checkbox" bind:checked={soundEnabled} />
          <span>{$t("typewriter.sound_toggle")}</span>
        </label>
      </div>
    </div>

    <textarea
      class="editor"
      spellcheck="false"
      placeholder={$t("typewriter.placeholder")}
      bind:value={text}
      on:input={handleInput}
      style="font-family: {fontRef}; font-size: {fontSize}px; text-align: {align};"
    ></textarea>
  </GlassPanel>
</div>

<style>
  .typewriter-container {
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
    display: flex;
    gap: 24px;
    align-items: center;
    margin-bottom: 20px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    flex-wrap: wrap;
  }

  .group {
    display: flex;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.8);
    font-size: 14px;
  }

  .editor {
    width: 100%;
    flex: 1;
    min-height: 400px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 30px;
    color: white;
    outline: none;
    resize: none;
    line-height: 1.6;
    transition: border-color 0.2s;
  }

  .editor:focus {
    border-color: rgba(255, 255, 255, 0.3);
  }

  input[type="range"] {
    width: 100px;
  }

  .toggle-group button {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
    padding: 6px 12px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s;
  }

  .toggle-group button:first-child {
    border-radius: 4px 0 0 4px;
  }
  .toggle-group button:last-child {
    border-radius: 0 4px 4px 0;
  }

  .toggle-group button.active {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border-color: rgba(255, 255, 255, 0.3);
  }

  .checkbox {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    user-select: none;
  }
</style>
