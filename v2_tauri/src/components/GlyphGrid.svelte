<script lang="ts">
  export let chars: number[] = [];
  export let fontFamily: string = "sans-serif";

  let page = 0;
  let pageSize = 200;

  $: totalPages = Math.ceil(chars.length / pageSize);
  $: displayedChars = chars.slice(page * pageSize, (page + 1) * pageSize);

  function nextPage() {
    if (page < totalPages - 1) page++;
  }

  function prevPage() {
    if (page > 0) page--;
  }
</script>

<div class="glyph-grid-container">
  <div class="controls" class:visible={totalPages > 1}>
    <button on:click={prevPage} disabled={page === 0}>&larr;</button>
    <span>Page {page + 1} / {totalPages || 1} ({chars.length} glyphes)</span>
    <button on:click={nextPage} disabled={page === totalPages - 1}
      >&rarr;</button
    >
  </div>

  <div class="grid" style="font-family: {fontFamily}">
    {#each displayedChars as char}
      <div class="glyph-item" title="U+{char.toString(16).toUpperCase()}">
        <span class="char">{String.fromCodePoint(char)}</span>
        <span class="code">{char.toString(16).toUpperCase()}</span>
      </div>
    {/each}
  </div>
</div>

<style>
  .glyph-grid-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
    height: 100%;
  }

  .controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
    color: white;
  }

  .controls.visible {
    opacity: 1;
    pointer-events: auto;
  }

  .controls button {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
  }

  .controls button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 12px;
    overflow-y: auto;
    padding-right: 10px;
  }

  .glyph-item {
    aspect-ratio: 1;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    cursor: default;
  }

  .glyph-item:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.05);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .char {
    font-size: 32px;
    color: white;
    margin-bottom: 4px;
  }

  .code {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.4);
    font-family: monospace;
  }
</style>
