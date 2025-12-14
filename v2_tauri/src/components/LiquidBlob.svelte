<script lang="ts">
  import { onMount } from 'svelte';
  import gsap from 'gsap';

  let circle1: SVGCircleElement;
  let circle2: SVGCircleElement;
  let container: HTMLDivElement;

  onMount(() => {
    // Random float animation
    gsap.to(circle1, {
      x: "random(-20, 20)",
      y: "random(-20, 20)",
      duration: 3,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut"
    });

    gsap.to(circle2, {
      x: "random(-30, 30)",
      y: "random(-30, 30)",
      duration: 4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      delay: 0.5
    });

    // Mouse follow effect on container
    const moveBlob = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      gsap.to([circle1, circle2], {
        x: `+=${x * 0.1}`,
        y: `+=${y * 0.1}`,
        duration: 1,
        ease: "power2.out",
        overwrite: "auto"
      });
    };

    // container.addEventListener('mousemove', moveBlob);

    // return () => container.removeEventListener('mousemove', moveBlob);
  });
</script>

<div class="blob-container" bind:this={container}>
  <svg viewBox="0 0 200 200">
    <defs>
      <filter id="goo">
        <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
        <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo" />
        <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
      </filter>
    </defs>
    <g style="filter: url(#goo)">
      <circle bind:this={circle1} cx="100" cy="100" r="40" fill="#ff00cc" />
      <circle bind:this={circle2} cx="120" cy="120" r="35" fill="#33ccff" />
    </g>
  </svg>
</div>

<style>
  .blob-container {
    width: 200px;
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  }

  svg {
    width: 100%;
    height: 100%;
    overflow: visible;
  }
</style>
