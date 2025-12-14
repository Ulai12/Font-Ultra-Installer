<script lang="ts">
  import gsap from 'gsap';
  import { onMount } from 'svelte';

  // Assumes @fontsource-variable/recursive is imported in global css or layout

  export let text = "Ultra Font";
  let titleElement: HTMLElement;

  onMount(() => {
    // Animate font variations loop
    const tl = gsap.timeline({ repeat: -1, yoyo: true });

    tl.to(titleElement, {
      fontVariationSettings: "'MONO' 0, 'CASL' 0, 'wght' 300, 'slnt' 0",
      duration: 1,
      ease: "power2.inOut"
    })
    .to(titleElement, {
      fontVariationSettings: "'MONO' 1, 'CASL' 1, 'wght' 1000, 'slnt' -15",
      color: "#ff00cc",
      duration: 2,
      ease: "elastic.out(1, 0.3)"
    })
    .to(titleElement, {
      fontVariationSettings: "'MONO' 0, 'CASL' 0.5, 'wght' 800, 'slnt' 0",
      color: "#33ccff",
      duration: 1,
      ease: "sine.in"
    });
  });
</script>

<h1 bind:this={titleElement} class="variable-title">
  {text}
</h1>

<style>
  .variable-title {
    font-family: 'Recursive Variable', sans-serif; /* Fallback */
    font-size: 4rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(45deg, #ff00cc, #33ccff);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    /* Initial settings */
    font-variation-settings: 'MONO' 0, 'CASL' 0, 'wght' 400, 'slnt' 0;
    margin: 0;
    user-select: none;
  }
</style>
