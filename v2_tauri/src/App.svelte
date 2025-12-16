<script lang="ts">
  import Sidebar from "./components/Sidebar.svelte";
  import { theme } from "./lib/theme";
  import About from "./pages/About.svelte";
  import Comparer from "./pages/Comparer.svelte";
  import Dashboard from "./pages/Dashboard.svelte";
  import GoogleFonts from "./pages/GoogleFonts.svelte";
  import Inspector from "./pages/Inspector.svelte";
  import Library from "./pages/Library.svelte";
  import Pairing from "./pages/Pairing.svelte";
  import Settings from "./pages/Settings.svelte";
  import Typewriter from "./pages/Typewriter.svelte";

  let activePage = "dashboard";

  const pages = {
    dashboard: Dashboard,
    library: Library,
    google: GoogleFonts,
    comparer: Comparer,
    typewriter: Typewriter,
    inspector: Inspector,
    pairing: Pairing,
    settings: Settings,
    about: About,
  };

  function handleNavigate(event: CustomEvent<string>) {
    activePage = event.detail;
  }
</script>

<!-- The .app-container handles the rounded corners and background -->
<div class="app-container" data-theme={$theme}>
  <main class="app-layout">
    <Sidebar {activePage} on:navigate={handleNavigate} />

    <div class="content-area">
      <svelte:component this={pages[activePage as keyof typeof pages]} />
    </div>
  </main>
</div>

<style>
  .app-layout {
    display: flex;
    width: 100%;
    height: 100%;
    /* No bg here, handled by app-container */
  }

  .content-area {
    flex: 1;
    overflow-y: auto;
    position: relative;
  }
</style>
