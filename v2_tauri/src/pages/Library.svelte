<script lang="ts">
  import GlassPanel from "../components/GlassPanel.svelte";
  import VariableTitle from "../components/VariableTitle.svelte";
  import VirtualFontGrid from "../components/VirtualFontGrid.svelte";
  import { t } from "../lib/i18n";
</script>

<div class="library-container">
  <div class="header">
    <VariableTitle text={$t("library.title")} />
    <p class="subtitle">{$t("library.search_placeholder")}</p>
  </div>

  <div class="workspace">
    <GlassPanel>
      <VirtualFontGrid />
    </GlassPanel>
  </div>
</div>

<style>
  .library-container {
    padding: 40px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  }

  .header {
    margin-bottom: 30px;
  }

  .subtitle {
    color: rgba(255, 255, 255, 0.6);
    margin-top: 5px;
    font-size: 16px;
  }

  .workspace {
    flex: 1;
    overflow: hidden; /* Important for inner scroll in VirtualFontGrid */
  }
</style>
