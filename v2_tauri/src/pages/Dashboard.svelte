<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { listen } from "@tauri-apps/api/event";
  import { open } from "@tauri-apps/plugin-dialog";
  import { onMount } from "svelte";
  import { t } from "../lib/i18n";

  // Font Type Definition
  type FontItem = {
    path: string;
    name: string;
    status: "pending" | "success" | "error" | "installing";
  };

  let fonts: FontItem[] = [];
  let isInstalling = false;
  let progress = 0;

  // Drag & Drop State
  let isDragging = false;

  async function addFiles() {
    try {
      const selected = await open({
        multiple: true,
        filters: [{ name: "Fonts", extensions: ["ttf", "otf", "ttc", "woff"] }],
      });
      if (selected) {
        const paths = Array.isArray(selected) ? selected : [selected];
        for (const path of paths) {
          await analyzeAndAdd(path);
        }
      }
    } catch (err) {
      console.error("Failed to open dialog", err);
    }
  }

  async function addFolder() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
      });
      if (selected) {
        // Mock behavior for folder add as standard web API cannot walk easily without backend help
        // Ideally here invoke('scan_folder', { path: selected })
        console.log("Folder selected:", selected);
        // For now just alert that this feature requires backend implementation in full version
        await addFiles(); // Fallback to file picker for now to keep flow working
      }
    } catch (err) {
      console.error("Failed to open dialog", err);
    }
  }

  async function analyzeAndAdd(path: string) {
    if (fonts.find((f) => f.path === path)) return;

    try {
      // Invoke backend to get metadata
      const meta = (await invoke("analyze_font", { path })) as any;
      fonts = [
        ...fonts,
        { path, name: meta.name || "Unknown", status: "pending" },
      ];
    } catch (e) {
      console.error("Analysis failed", e);
      const name = path.split(/[\\/]/).pop() || "Unknown";
      fonts = [...fonts, { path, name, status: "error" }];
    }
  }

  function clearList() {
    if (isInstalling) return;
    fonts = [];
    progress = 0;
  }

  async function installAll() {
    if (fonts.length === 0) return;
    isInstalling = true;
    progress = 0;

    for (let i = 0; i < fonts.length; i++) {
      const font = fonts[i];
      if (font.status === "success") {
        continue;
      }

      fonts[i].status = "installing";
      fonts = [...fonts]; // Trigger reactivity

      try {
        await invoke("install_font", { path: font.path });
        fonts[i].status = "success";
      } catch (e) {
        console.error(e);
        fonts[i].status = "error";
      }
      progress = ((i + 1) / fonts.length) * 100;
    }

    isInstalling = false;
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    isDragging = true;
  }

  function handleDragLeave() {
    isDragging = false;
  }

  async function handleDrop(e: DragEvent) {
    e.preventDefault();
    isDragging = false;
    // Web Drag Drop might not give full path key in all OS/Browsers without special flags
    // We rely on Tauri global drag-drop event for better reliability
  }

  onMount(async () => {
    // Listen to Tauri global file drop (works better than HTML5 API for paths)
    const unlisten = await listen("tauri://drag-drop", (event: any) => {
      if (event.payload && event.payload.paths) {
        for (const path of event.payload.paths) {
          if (path.toLowerCase().match(/\.(ttf|otf|ttc)$/)) {
            analyzeAndAdd(path);
          }
        }
      }
    });

    return () => {
      unlisten();
    };
  });
</script>

<div class="dashboard-page">
  <div class="header">
    <h1 class="page-title">{$t("dashboard.title")}</h1>
    <p class="page-subtitle">{$t("dashboard.subtitle")}</p>
  </div>

  <!-- Drag & Drop Zone -->
  <div
    class="drop-zone"
    class:active={isDragging}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    on:drop={handleDrop}
    role="region"
    aria-label="File drop zone"
  >
    <div class="drop-content">
      <svg
        class="drop-icon"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      <p>{$t("dashboard.drop_text")}</p>
    </div>
  </div>

  <!-- Toolbar -->
  <div class="toolbar">
    <div class="group-left">
      <button class="btn" on:click={addFiles}>
        <svg
          class="btn-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"><path d="M12 4v16m-8-8h16" /></svg
        >
        {$t("dashboard.add_files")}
      </button>
      <button class="btn" on:click={addFolder}>
        <svg
          class="btn-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          ><path
            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
          /></svg
        >
        {$t("dashboard.add_folder")}
      </button>
      <button class="btn" on:click={clearList}>
        <svg
          class="btn-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          ><path
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          /></svg
        >
        {$t("dashboard.clear")}
      </button>
    </div>

    <div class="group-right">
      <button
        class="btn btn-primary"
        on:click={installAll}
        disabled={isInstalling || fonts.length === 0}
      >
        {#if isInstalling}
          {$t("dashboard.installing")} ({Math.round(progress)}%)
        {:else}
          <svg
            class="btn-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            ><path
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            /></svg
          >
          {$t("dashboard.install_all")}
        {/if}
      </button>
    </div>
  </div>

  <!-- Font List -->
  <div class="font-list-container">
    {#if fonts.length === 0}
      <div class="empty-state">
        <p>{$t("dashboard.empty_list")}</p>
      </div>
    {:else}
      <div class="font-list">
        {#each fonts as font (font.path)}
          <div class="font-item">
            <div class="font-info">
              <span class="font-name">{font.name}</span>
              <span class="font-path">{font.path}</span>
            </div>
            <div class="font-status status-{font.status}">
              {font.status === "success" ? "Installed" : font.status}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .dashboard-page {
    padding: 30px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .header {
    margin-bottom: 10px;
  }

  .page-title {
    font-size: 32px;
    margin: 0;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .page-subtitle {
    opacity: 0.7;
    margin: 5px 0 0 0;
  }

  /* Drop Zone */
  .drop-zone {
    border: 2px dashed var(--tile-border);
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    position: relative;
  }

  .drop-zone.active,
  .drop-zone:hover {
    border-color: var(--accent-color);
    background: rgba(0, 194, 255, 0.05);
  }

  .drop-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    color: var(--text-secondary);
  }

  .drop-icon {
    width: 40px;
    height: 40px;
    opacity: 0.8;
  }

  /* Toolbar */
  .toolbar {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }

  .group-left,
  .group-right {
    display: flex;
    gap: 10px;
  }

  .btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: 12px;
    border: 1px solid var(--tile-border);
    background: var(--tile-bg);
    color: var(--text-primary);
    cursor: pointer;
    font-family: inherit;
    font-weight: 500;
    transition: all 0.2s;
  }

  .btn:hover:not(:disabled) {
    background: var(--tile-hover);
    transform: translateY(-1px);
  }

  .btn-primary {
    background: var(--accent-gradient);
    color: white;
    border: none;
    box-shadow: 0 4px 15px rgba(0, 194, 255, 0.3);
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-icon {
    width: 18px;
    height: 18px;
  }

  /* List */
  .font-list-container {
    flex: 1;
    background: var(--tile-bg);
    border-radius: 16px;
    border: 1px solid var(--tile-border);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    font-style: italic;
  }

  .font-list {
    padding: 10px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .font-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 255, 255, 0.03);
    padding: 12px 16px;
    border-radius: 8px;
    transition: background 0.2s;
  }

  .font-item:hover {
    background: rgba(255, 255, 255, 0.06);
  }

  .font-info {
    display: flex;
    flex-direction: column;
  }

  .font-name {
    font-weight: 600;
  }

  .font-path {
    font-size: 12px;
    opacity: 0.5;
  }

  .font-status {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
  }

  .status-success {
    color: #00ff88;
    background: rgba(0, 255, 136, 0.1);
  }
  .status-error {
    color: #ff3e3e;
    background: rgba(255, 62, 62, 0.1);
  }
  .status-installing {
    color: var(--accent-color);
  }
</style>
