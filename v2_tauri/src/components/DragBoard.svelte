<script lang="ts">
  import { listen } from "@tauri-apps/api/event";
  import { createEventDispatcher, onMount } from "svelte";

  const dispatch = createEventDispatcher();
  let isDragging = false;

  // Fonction pour écouter le file drop de Tauri
  onMount(() => {
    let unlisten: () => void;
    let unlistenHover: () => void;
    let unlistenCancel: () => void;

    (async () => {
      unlisten = await listen("tauri://file-drop", (event) => {
        const files = event.payload as string[];
        if (files && files.length > 0) {
          handleFiles(files);
        }
        isDragging = false;
      });

      unlistenHover = await listen("tauri://file-drop-hover", () => {
        isDragging = true;
      });

      unlistenCancel = await listen("tauri://file-drop-cancelled", () => {
        isDragging = false;
      });
    })();

    return () => {
      if (unlisten) unlisten();
      if (unlistenHover) unlistenHover();
      if (unlistenCancel) unlistenCancel();
    };
  });

  function handleFiles(files: string[]) {
    // Filtrer pour ne garder que les extensions de polices
    const fontFiles = files.filter((f) =>
      /\.(ttf|otf|woff|woff2|ttc)$/i.test(f)
    );
    if (fontFiles.length > 0) {
      dispatch("filesDropped", fontFiles);
    }
  }
</script>

<div class="drop-zone" class:active={isDragging}>
  <div class="content">
    <svg
      class="icon"
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
    <p class="title">Déposez vos polices ici</p>
    <p class="subtitle">.ttf, .otf, .woff supportés</p>
  </div>
</div>

<style>
  .drop-zone {
    width: 100%;
    height: 160px;
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.05);
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }

  .drop-zone.active {
    border-color: #00c2ff;
    background: rgba(0, 194, 255, 0.1);
    transform: scale(1.01);
  }

  .content {
    text-align: center;
    pointer-events: none;
  }

  .icon {
    width: 48px;
    height: 48px;
    margin-bottom: 12px;
    color: rgba(255, 255, 255, 0.7);
  }

  .drop-zone:hover .icon,
  .drop-zone.active .icon {
    color: #00c2ff;
  }

  .title {
    font-size: 18px;
    font-weight: 600;
    margin: 0;
    color: #fff;
  }

  .subtitle {
    margin: 4px 0 0;
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
  }
</style>
