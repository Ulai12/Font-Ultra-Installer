<script lang="ts">
  export let className = "";
</script>

<div class="glass-panel {className}">
  <slot />
</div>

<style>
  .glass-panel {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    border-radius: 16px;
    padding: 20px;
    transition: all 0.3s ease;
  }

  /* Fallback for systems without backdrop-filter support */
  @supports not (backdrop-filter: blur(1px)) {
    .glass-panel {
      background: rgba(255, 255, 255, 0.85); /* More opaque fallback */
    }
  }

  /* Dark mode support (optional, if app is dark by default) */
  :global(:root.dark) .glass-panel {
    background: rgba(18, 18, 18, 0.6);
    border-color: rgba(255, 255, 255, 0.1);
  }
</style>
