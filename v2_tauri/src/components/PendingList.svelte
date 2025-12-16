<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { createEventDispatcher } from "svelte";

  export let files: string[] = [];

  const dispatch = createEventDispatcher();
  let installing = false;
  let progress = 0;

  async function installAll() {
    installing = true;
    progress = 0;

    // Simuler l'analyse (on le fera pour de vrai avec le backend plu tard)
    // Pour l'instant on appelle le system install pour chaque fichier
    // TODO: implement batch install in Rust

    let count = 0;
    for (const file of files) {
      try {
        // Mock install for now until wired up completely
        await invoke("install_font", { path: file });
        count++;
        progress = (count / files.length) * 100;
      } catch (e) {
        console.error("Install failed for", file, e);
      }
    }

    installing = false;
    dispatch("installed", count);
  }

  function removeFile(index: number) {
    files = files.filter((_, i) => i !== index);
    if (files.length === 0) dispatch("empty");
  }

  function getName(path: string) {
    return path.split(/[\\/]/).pop();
  }
</script>

<div class="pending-list">
  <div class="header">
    <h3>Polices détectées ({files.length})</h3>
    <div class="actions">
      <button
        class="clear-btn"
        on:click={() => dispatch("clear")}
        disabled={installing}>Tout effacer</button
      >
      <button class="install-btn" on:click={installAll} disabled={installing}>
        {#if installing}
          Installation... {Math.round(progress)}%
        {:else}
          Installer Tout
        {/if}
      </button>
    </div>
  </div>

  <div class="list-container">
    {#each files as file, i}
      <div class="file-item">
        <span class="file-icon">Aa</span>
        <span class="file-name">{getName(file)}</span>
        <button
          class="remove-btn"
          on:click={() => removeFile(i)}
          disabled={installing}>×</button
        >
      </div>
    {/each}
  </div>
</div>

<style>
  .pending-list {
    margin-top: 20px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
  }

  .actions {
    display: flex;
    gap: 10px;
  }

  .clear-btn {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 8px 16px;
    color: rgba(255, 255, 255, 0.8);
  }

  .clear-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .install-btn {
    background: #00c2ff;
    color: white;
    border: none;
    padding: 8px 20px;
    font-weight: 600;
    min-width: 120px;
  }

  .install-btn:hover:not(:disabled) {
    box-shadow: 0 0 15px rgba(0, 194, 255, 0.4);
  }

  .install-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .list-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 300px;
    overflow-y: auto;
  }

  .file-item {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.05);
    padding: 10px;
    border-radius: 8px;
    gap: 12px;
  }

  .file-icon {
    width: 32px;
    height: 32px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 14px;
  }

  .file-name {
    flex: 1;
    font-size: 14px;
    opacity: 0.9;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
  }

  .remove-btn {
    background: transparent;
    width: 24px;
    height: 24px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: rgba(255, 255, 255, 0.5);
  }

  .remove-btn:hover {
    color: white;
    background: rgba(255, 0, 0, 0.2);
  }
</style>
