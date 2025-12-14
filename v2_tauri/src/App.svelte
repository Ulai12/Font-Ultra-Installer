<script lang="ts">
  import GlassPanel from './components/GlassPanel.svelte';
  import LiquidBlob from './components/LiquidBlob.svelte';
  import VariableTitle from './components/VariableTitle.svelte';
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  let sysInfo = "";

  async function checkSystem() {
    try {
      // Example IPC call (implementation needed in backend)
      // sysInfo = await invoke('get_system_info');
      sysInfo = "System Ready (Simulated)";
    } catch (e) {
      console.error(e);
      sysInfo = "Backend not connected";
    }
  }

  onMount(() => {
    checkSystem();
  });
</script>

<main class="container">
  <div class="background-blobs">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
  </div>

  <GlassPanel className="main-panel">
    <VariableTitle text="Ultra Font" />

    <div class="content-grid">
      <div class="demo-section">
        <h2>Liquid Interface</h2>
        <GlassPanel className="inner-glass">
            <LiquidBlob />
            <p>Interactive Gooey Effect</p>
        </GlassPanel>
      </div>

      <div class="demo-section">
        <h2>System Status</h2>
        <p class="status">{sysInfo}</p>
        <button class="action-btn">Install Font</button>
      </div>
    </div>
  </GlassPanel>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #0f0c29;
    background: linear-gradient(to right, #24243e, #302b63, #0f0c29);
    font-family: 'Recursive Variable', sans-serif;
    color: white;
    height: 100vh;
    overflow: hidden;
  }

  .container {
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    z-index: 1;
  }

  .background-blobs {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
  }

  .blob {
    position: absolute;
    filter: blur(80px);
    opacity: 0.6;
    border-radius: 50%;
  }

  .blob-1 {
    top: -10%;
    left: -10%;
    width: 500px;
    height: 500px;
    background: purple;
    animation: float 20s infinite alternate;
  }

  .blob-2 {
    bottom: -10%;
    right: -10%;
    width: 600px;
    height: 600px;
    background: blue;
    animation: float 25s infinite alternate-reverse;
  }

  @keyframes float {
    from { transform: translate(0, 0); }
    to { transform: translate(50px, 50px); }
  }

  :global(.main-panel) {
    width: 800px;
    height: 600px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    width: 100%;
    margin-top: 2rem;
  }

  .demo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  :global(.inner-glass) {
    background: rgba(255, 255, 255, 0.05) !important;
    padding: 1rem !important;
  }

  .action-btn {
    background: linear-gradient(45deg, #ff00cc, #33ccff);
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .action-btn:hover {
    transform: scale(1.05);
  }
</style>
