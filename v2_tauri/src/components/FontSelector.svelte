<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { createEventDispatcher, onMount } from "svelte";

  export let selectedFont = "Arial";

  const dispatch = createEventDispatcher();

  let fonts: string[] = [];
  let isOpen = false;
  let searchTerm = "";

  onMount(async () => {
    try {
      fonts = await invoke<string[]>("get_installed_fonts");
    } catch (e) {
      console.error("Failed to load fonts", e);
    }
  });

  function selectFont(font: string) {
    selectedFont = font;
    isOpen = false;
    dispatch("change", font);
  }

  $: filteredFonts = fonts.filter((f) =>
    f.toLowerCase().includes(searchTerm.toLowerCase())
  );
</script>

<div class="font-selector">
  <button class="selector-btn" on:click={() => (isOpen = !isOpen)}>
    <span class="current-font">{selectedFont}</span>
    <span class="chevron">▼</span>
  </button>

  {#if isOpen}
    <div class="dropdown">
      <input
        type="text"
        class="search-input"
        placeholder="Rechercher..."
        bind:value={searchTerm}
        on:click|stopPropagation
      />
      <div class="list">
        {#each filteredFonts as font}
          <button class="font-item" on:click={() => selectFont(font)}>
            {font}
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .font-selector {
    position: relative;
    width: 200px;
  }

  .selector-btn {
    width: 100%;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    font-size: 14px;
  }

  .dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    margin-top: 4px;
    background: #1a1a1a;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 6px;
    z-index: 100;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  }

  .search-input {
    width: 100%;
    padding: 8px;
    background: rgba(255, 255, 255, 0.05);
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    outline: none;
    box-sizing: border-box;
  }

  .list {
    max-height: 200px;
    overflow-y: auto;
  }

  .font-item {
    width: 100%;
    padding: 8px 12px;
    text-align: left;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.8);
    cursor: pointer;
  }

  .font-item:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
</style>
