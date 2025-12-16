<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { t } from "../lib/i18n";

  export let activePage = "dashboard";

  const dispatch = createEventDispatcher();

  function navigate(page: string) {
    dispatch("navigate", page);
  }

  $: menuItems = [
    {
      id: "dashboard",
      label: $t("sidebar.dashboard"),
      icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    },
    {
      id: "library",
      label: $t("sidebar.library"),
      icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    },
    {
      id: "google",
      label: $t("sidebar.google_fonts"),
      icon: "M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z",
    },
    {
      id: "comparer",
      label: $t("sidebar.comparer"),
      icon: "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4",
    },
    {
      id: "typewriter",
      label: $t("sidebar.typewriter"),
      icon: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z",
    },
    {
      id: "inspector",
      label: $t("sidebar.inspector"),
      icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
    },
    {
      id: "pairing",
      label: $t("sidebar.pairing"),
      icon: "M13 10V3L4 14h7v7l9-11h-7z",
    },
  ];

  $: bottomItems = [
    {
      id: "settings",
      label: $t("sidebar.settings"),
      icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
    },
    {
      id: "about",
      label: $t("sidebar.about"),
      icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    },
  ];
</script>

<aside class="sidebar">
  <div class="logo-area">
    <div class="logo-icon">UF</div>
  </div>

  <nav class="nav-group">
    {#each menuItems as item}
      <button
        class="nav-tile"
        class:active={activePage === item.id}
        on:click={() => navigate(item.id)}
        title={item.label}
      >
        <svg
          class="icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d={item.icon} />
        </svg>
      </button>
    {/each}
  </nav>

  <div class="nav-bottom">
    {#each bottomItems as item}
      <button
        class="nav-tile"
        class:active={activePage === item.id}
        on:click={() => navigate(item.id)}
        title={item.label}
      >
        <svg
          class="icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d={item.icon} />
        </svg>
      </button>
    {/each}
  </div>
</aside>

<style>
  .sidebar {
    width: var(--sidebar-width, 80px);
    height: 100%;
    /* Subtle separation instead of hard border */
    background: rgba(0, 0, 0, 0.02);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 10px;
    box-sizing: border-box;
    flex-shrink: 0;
  }

  .logo-area {
    margin-bottom: 30px;
  }

  .logo-icon {
    width: 48px;
    height: 48px;
    background: var(--accent-gradient);
    border-radius: 12px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-title);
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .nav-group,
  .nav-bottom {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
    align-items: center;
  }

  .nav-group {
    flex: 1;
    overflow-y: auto;
    /* Hide scrollbar */
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .nav-group::-webkit-scrollbar {
    display: none;
  }

  .nav-tile {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-tile);
    border: 1px solid var(--tile-border);
    background: var(--tile-bg);
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .nav-tile:hover {
    background: var(--tile-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    color: var(--text-primary);
  }

  .nav-tile.active {
    background: var(--accent-gradient);
    color: white;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 194, 255, 0.4);
  }

  .icon {
    width: 24px;
    height: 24px;
  }
</style>
