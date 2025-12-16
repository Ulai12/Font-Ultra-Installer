<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { onMount } from "svelte";
  import FontCard from "./FontCard.svelte";

  export let initialFonts: string[] = []; // List of filenames

  let fonts: { name: string; path: string }[] = [];
  let filteredFonts: { name: string; path: string }[] = [];
  let displayFonts: { name: string; path: string }[] = [];
  let searchQuery = "";

  // Virtualization / Pagination state
  let itemsPerPage = 20;
  let currentPage = 1;
  let observer: IntersectionObserver;
  let loadTrigger: HTMLElement;

  onMount(() => {
    let observerInstance: IntersectionObserver;

    (async () => {
      // If not provided via props, fetch from system
      if (initialFonts.length === 0) {
        const result = await invoke<string[]>("get_installed_fonts");
        // Assume result is just filenames, we need to reconstruct path or rely on system knowelge
        // system.rs currently returns filenames from C:\Windows\Fonts
        // We'll construct the path here for now.
        fonts = result.map((f) => ({
          name: f,
          path: `C:\\Windows\\Fonts\\${f}`,
        }));
      } else {
        fonts = initialFonts.map((f) => ({
          name: f,
          path: `C:\\Windows\\Fonts\\${f}`,
        }));
      }

      filteredFonts = fonts;
      updateDisplay();

      // Setup infinite scroll observer
      observerInstance = new IntersectionObserver(handleIntersect, {
        root: null,
        rootMargin: "100px",
        threshold: 0.1,
      });

      if (loadTrigger) {
        observerInstance.observe(loadTrigger);
      }
      observer = observerInstance;
    })();

    return () => {
      if (observerInstance) observerInstance.disconnect();
    };
  });

  function handleIntersect(entries: IntersectionObserverEntry[]) {
    if (entries[0].isIntersecting) {
      currentPage++;
      updateDisplay();
    }
  }

  function handleSearch() {
    currentPage = 1;
    if (searchQuery.trim() === "") {
      filteredFonts = fonts;
    } else {
      const q = searchQuery.toLowerCase();
      filteredFonts = fonts.filter((f) => f.name.toLowerCase().includes(q));
    }
    updateDisplay();
  }

  function updateDisplay() {
    const end = currentPage * itemsPerPage;
    displayFonts = filteredFonts.slice(0, end);
  }

  $: searchQuery, handleSearch();
</script>

<div class="virtual-grid-container">
  <div class="search-bar">
    <input
      type="text"
      placeholder="Rechercher une police..."
      bind:value={searchQuery}
    />
  </div>

  <div class="grid">
    {#each displayFonts as font (font.name)}
      <FontCard fileName={font.name} fontPath={font.path} />
    {/each}
  </div>

  <div class="loader-trigger" bind:this={loadTrigger}>
    {#if displayFonts.length < filteredFonts.length}
      <span class="loading-text">Chargement...</span>
    {/if}
  </div>
</div>

<style>
  .virtual-grid-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    gap: 20px;
  }

  .search-bar input {
    width: 100%;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
  }

  .search-bar input:focus {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
    padding-bottom: 20px;
  }

  .loader-trigger {
    padding: 20px;
    text-align: center;
    color: rgba(255, 255, 255, 0.3);
    min-height: 50px;
  }
</style>
