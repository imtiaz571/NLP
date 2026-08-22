/**
 * NPC Talk — Dynamic Environment Particle System
 * Pure JavaScript & CSS particle controller.
 * Generates floating fireflies, drifting leaves, glowing embers, and dust motes.
 */

class ParticleEngine {
  constructor(containerId = "particles-container") {
    this.container = document.getElementById(containerId);
    this.currentEffect = null;
    this.particles = [];
    this.active = true;
    this.maxParticles = 30;
  }

  /**
   * Update active particle system based on environment and time of day
   */
  update(environment = "village_square", timeOfDay = "day") {
    if (!this.container) return;

    let targetEffect = "motes";

    if (timeOfDay === "night") {
      targetEffect = "fireflies";
    } else if (environment.includes("forest") || environment.includes("woods")) {
      targetEffect = "leaves";
    } else if (environment.includes("forge") || environment.includes("blacksmith") || timeOfDay === "dusk") {
      targetEffect = "embers";
    } else if (timeOfDay === "dawn" || timeOfDay === "morning") {
      targetEffect = "shimmer";
    } else {
      targetEffect = "motes";
    }

    if (this.currentEffect === targetEffect) return;

    this.clear();
    this.currentEffect = targetEffect;
    this.spawnPreset(targetEffect);
  }

  clear() {
    if (!this.container) return;
    this.container.innerHTML = "";
    this.particles = [];
  }

  spawnPreset(effect) {
    if (!this.container || !this.active) return;

    // Reduced particle density (~40% less) so particles don't obscure portrait or parchment dialogue
    const count = effect === "fireflies" ? 12 : effect === "leaves" ? 10 : effect === "embers" ? 15 : 12;

    for (let i = 0; i < count; i++) {
      const p = document.createElement("div");
      p.className = `particle particle-${effect}`;

      // Random starting coordinates & animation properties
      const left = Math.random() * 100;
      const top = Math.random() * 100;
      const size = effect === "fireflies" ? 4 + Math.random() * 4 : effect === "leaves" ? 8 + Math.random() * 8 : 3 + Math.random() * 5;
      const duration = 6 + Math.random() * 8;
      const delay = Math.random() * 5;
      const drift = (Math.random() - 0.5) * 120;

      p.style.setProperty("--left", `${left}%`);
      p.style.setProperty("--top", `${top}%`);
      p.style.setProperty("--size", `${size}px`);
      p.style.setProperty("--duration", `${duration}s`);
      p.style.setProperty("--delay", `${delay}s`);
      p.style.setProperty("--drift", `${drift}px`);

      if (effect === "leaves") {
        const rot = Math.random() * 360;
        p.style.setProperty("--rot", `${rot}deg`);
      }

      this.container.appendChild(p);
      this.particles.push(p);
    }
  }

  toggle() {
    this.active = !this.active;
    if (!this.active) {
      this.clear();
    } else if (this.currentEffect) {
      this.spawnPreset(this.currentEffect);
    }
    return this.active;
  }
}

// Global particle engine instance
window.particleEngine = new ParticleEngine();
