<script lang="ts">
  import { convertFileSrc } from "@tauri-apps/api/core";
  import { onMount } from "svelte";

  export let fileName: string;
  export let fontPath: string; // Full path e.g. C:\Windows\Fonts\arial.ttf

  let fontName = fileName;
  let fontFaceName = `font_${fileName.replace(/\./g, "_")}`;
  let isLoaded = false;

  onMount(async () => {
    // Dynamically load the font
    try {
      const url = convertFileSrc(fontPath);
      const font = new FontFace(fontFaceName, `url('${url}')`);
      await font.load();
      document.fonts.add(font);
      isLoaded = true;
    } catch (e) {
      console.error(`Failed to load font ${fileName}`, e);
    }
  });
</script>

<div class="font-card">
  <div
    class="preview"
    style="font-family: {isLoaded ? fontFaceName : 'sans-serif'}"
  >
    The quick brown fox jumps over the lazy dog
  </div>
  <div class="info">
    <span class="name" title={fileName}>{fileName}</span>
    <span class="path">{fontPath}</span>
  </div>
</div>

<style>
  .font-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.2s ease;
  }

  .font-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }

  .preview {
    font-size: 24px;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .name {
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
  }

  .path {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style>
