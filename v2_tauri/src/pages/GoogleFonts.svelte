<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { onMount } from "svelte";
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import { t } from "../lib/i18n";

  // Hardcoded key as requested by USER (only accessible via this code)
  const API_KEY = "AIzaSyCBB7xqGzhXyOwx3785foT1445WZhq7gMY";

  let fonts: any[] = [];
  let isLoading = false;
  let statusMessage = "";
  let searchQuery = "";
  let sortOption = "popularity";
  let categoryOption = "";

  // Mockup used only if API fails or network issue
  const featuredMockup = [
    { family: "Roboto", category: "sans-serif" },
    { family: "Open Sans", category: "sans-serif" },
    { family: "Lato", category: "sans-serif" },
    { family: "Montserrat", category: "sans-serif" },
  ];

  // Watch sort option to re-fetch when it changes (but not category, handled client-side filter or API?)
  // Google Fonts API supports sorting. Category is client-side filter usually unless strict query.
  // Actually Google Fonts API doesn't filter category directly cleanly, it's safer to filter client side
  // OR fetch all and filter, but that's heavy.
  // Let's rely on sort param in API call, and client-side filter for category.

  $: if (sortOption) {
    if (API_KEY) fetchFonts();
  }

  onMount(() => {
    fetchFonts();
  });

  async function fetchFonts() {
    isLoading = true;

    try {
      // Construct URL with sort
      let url = `https://www.googleapis.com/webfonts/v1/webfonts?key=${API_KEY}&sort=${sortOption}`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.error) {
        statusMessage = $t("google_fonts.error") + " " + data.error.message;
        fonts = [];
      } else {
        fonts = data.items;
        statusMessage = "";
      }
    } catch (e) {
      statusMessage = $t("google_fonts.network_error") + " " + e;
    } finally {
      isLoading = false;
    }
  }

  // ... (downloadFont function remains same)

  async function downloadFont(font: any) {
    if (!font.files || !font.files.regular) {
      statusMessage = $t("google_fonts.no_regular");
      return;
    }

    const url: string = font.files.regular;
    const secureUrl = url.replace("http:", "https:");
    const filename = `${font.family.replace(/\s+/g, "_")}-Regular.ttf`;

    statusMessage = $t("google_fonts.downloading").replace(
      "{font}",
      font.family
    );

    try {
      const localPath = await invoke<string>("download_font", {
        url: secureUrl,
        filename,
      });
      statusMessage = $t("google_fonts.installing").replace(
        "{font}",
        font.family
      );

      await invoke("install_font", { path: localPath });

      statusMessage = $t("google_fonts.success").replace("{font}", font.family);
      setTimeout(() => (statusMessage = ""), 4000);
    } catch (e) {
      console.error(e);
      statusMessage = $t("google_fonts.error") + " " + e;
    }
  }

  // Filter Logic:
  // 1. Search Query
  // 2. Category
  $: filteredFonts = fonts
    .filter((f) => {
      let matchesSearch = f.family
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      let matchesCategory =
        categoryOption === "" || f.category === categoryOption;
      return matchesSearch && matchesCategory;
    })
    .slice(0, 50);

  $: showFeatured = fonts.length === 0 && !isLoading;
</script>

<div class="google-fonts-container">
  <div class="header">
    <VariableTitle text={$t("google_fonts.title")} />
    <p class="subtitle">{$t("google_fonts.subtitle")}</p>
  </div>

  <GlassPanel>
    <div class="controls">
      <!-- Search Bar -->
      <div class="search-section">
        <input
          type="text"
          placeholder={$t("google_fonts.filter_placeholder")}
          bind:value={searchQuery}
          class="search-input"
        />
        <button on:click={fetchFonts} disabled={isLoading}>
          {isLoading
            ? $t("google_fonts.loading")
            : $t("google_fonts.search_btn")}
        </button>
      </div>

      <!-- Filters Row -->
      <div class="filters-row">
        <select bind:value={categoryOption} class="dropdown">
          <option value="">{$t("google_fonts.cat_all")}</option>
          <option value="serif">{$t("google_fonts.cat_serif")}</option>
          <option value="sans-serif">{$t("google_fonts.cat_sans")}</option>
          <option value="display">{$t("google_fonts.cat_display")}</option>
          <option value="handwriting"
            >{$t("google_fonts.cat_handwriting")}</option
          >
          <option value="monospace">{$t("google_fonts.cat_monospace")}</option>
        </select>

        <select bind:value={sortOption} class="dropdown">
          <option value="popularity"
            >{$t("google_fonts.sort_popularity")}</option
          >
          <option value="trending">{$t("google_fonts.sort_trending")}</option>
          <option value="date">{$t("google_fonts.sort_date")}</option>
          <option value="alpha">{$t("google_fonts.sort_alpha")}</option>
        </select>
      </div>

      {#if statusMessage}
        <div
          class="status-bar"
          class:error={statusMessage.includes("Erreur") ||
            statusMessage.includes("Error")}
        >
          {statusMessage}
        </div>
      {/if}
    </div>

    <div class="grid-container">
      {#if showFeatured}
        <div class="featured-banner">
          <h3>{$t("google_fonts.featured")} <span class="badge">Demo</span></h3>
          <p>{$t("google_fonts.enter_api")}</p>
        </div>
      {/if}

      <div class="grid">
        {#each filteredFonts as font}
          <div class="font-card">
            <div
              class="font-preview"
              style="font-family: '{font.family}', sans-serif;"
            >
              {font.family}
            </div>
            <div class="font-info-row">
              <span class="category">{font.category || "font"}</span>
            </div>
            <div class="font-actions">
              <span class="font-name">{font.family}</span>
              <button
                class="download-btn"
                on:click={() => downloadFont(font)}
                title={$t("google_fonts.download_btn")}
                disabled={showFeatured}
              >
                <svg
                  viewBox="0 0 24 24"
                  width="16"
                  height="16"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  ><path
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1M12 12l-4-4m4 4l4-4m-4 4V4"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  /></svg
                >
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </GlassPanel>
</div>

<style>
  .google-fonts-container {
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
    flex-direction: column;
    gap: 15px;
    margin-bottom: 20px;
    /* Sticky header for controls could be added */
  }

  .search-section {
    display: flex;
    gap: 10px;
  }

  .filters-row {
    display: flex;
    gap: 10px;
  }

  .search-input {
    flex: 2; /* more space for search */
    padding: 12px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    outline: none;
    font-size: 14px;
    transition: border-color 0.2s;
  }

  .dropdown {
    flex: 1;
    padding: 12px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: white;
    outline: none;
    font-size: 14px;
    cursor: pointer;
  }

  .dropdown option {
    background: #222;
    color: white;
  }

  .search-input:focus,
  .dropdown:focus {
    border-color: #00c2ff;
  }

  button {
    padding: 0 20px;
    background: var(--accent-gradient, #00c2ff);
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    font-weight: 600;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #555;
  }

  .status-bar {
    padding: 12px;
    background: rgba(0, 194, 255, 0.1);
    border-left: 4px solid #00c2ff;
    border-radius: 4px;
    color: white;
    font-size: 14px;
  }

  .status-bar.error {
    background: rgba(255, 62, 62, 0.1);
    border-color: #ff3e3e;
    color: #ffcccc;
  }

  .grid-container {
    flex: 1;
    overflow-y: auto;
    min-height: 400px;
    padding-right: 5px; /* space for scrollbar */
  }

  .featured-banner {
    background: rgba(255, 255, 255, 0.05);
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px dashed rgba(255, 255, 255, 0.2);
  }

  .featured-banner h3 {
    margin: 0 0 5px 0;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .badge {
    background: #ff3e9d;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .featured-banner p {
    margin: 0;
    font-size: 13px;
    opacity: 0.7;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
    padding-bottom: 20px;
  }

  .font-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition:
      transform 0.2s,
      background 0.2s;
  }

  .font-card:hover {
    transform: translateY(-2px);
    background: rgba(255, 255, 255, 0.07);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .font-preview {
    font-size: 28px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    height: 40px; /* fix height */
    line-height: 40px;
  }

  .font-info-row {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.4);
    text-transform: uppercase;
  }

  .font-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    margin-top: auto; /* Push to bottom */
  }

  .download-btn {
    background: rgba(255, 255, 255, 0.1);
    padding: 8px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .download-btn:hover:not(:disabled) {
    background: #00c2ff;
  }
</style>
