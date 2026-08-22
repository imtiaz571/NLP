/**
 * NPC Talk — Web Audio API Procedural Sound Engine
 * Provides ambient atmospheric background audio and dialogue/UI sound effects.
 * 100% self-contained without needing external audio MP3 files.
 */

class AudioEngine {
  constructor() {
    this.ctx = null;
    this.muted = true; // Default muted until player clicks unmute (browser autoplay policy)
    this.ambientGain = null;
    this.sfxGain = null;
    this.ambientNodes = [];
    this.ambientTimers = [];
    this.atmosphereToken = 0;
    this.noiseBuffer = null;
    this.currentAtmosphere = null;
    this.currentTrackPath = null;
    this.currentTrackVolume = 0.23;
    this.currentMood = "neutral";
    this.lastEnvironment = "village_square";
    this.lastTimeOfDay = "day";
    this.trackFadeHandles = new WeakMap();
    this.activeTrackSlot = 0;
    this.trackA = null;
    this.trackB = null;

    this.ambientTrackMap = {
      village_square: {
        dawn: "assets/audio/ambience/warm_evening_outdoors.ogg",
        day: "assets/audio/ambience/warm_evening_outdoors.ogg",
        dusk: "assets/audio/ambience/warm_evening_outdoors.ogg",
        night: "assets/audio/ambience/outside_night.ogg"
      },
      forest: {
        dawn: "assets/audio/ambience/spring_day_forest.ogg",
        day: "assets/audio/ambience/summer_forest.ogg",
        dusk: "assets/audio/ambience/warm_evening_outdoors.ogg",
        night: "assets/audio/ambience/outside_night.ogg"
      },
      tavern: {
        dawn: "assets/audio/ambience/coffee_shop.ogg",
        day: "assets/audio/ambience/coffee_shop.ogg",
        dusk: "assets/audio/ambience/coffee_shop.ogg",
        night: "assets/audio/ambience/coffee_shop.ogg"
      },
      market_stalls: {
        dawn: "assets/audio/ambience/small_outdoor_marketplace.ogg",
        day: "assets/audio/ambience/small_outdoor_marketplace.ogg",
        dusk: "assets/audio/ambience/small_outdoor_marketplace.ogg",
        night: "assets/audio/ambience/outside_night.ogg"
      },
      apothecary: {
        dawn: "assets/audio/ambience/fire.ogg",
        day: "assets/audio/ambience/fire.ogg",
        dusk: "assets/audio/ambience/fire.ogg",
        night: "assets/audio/ambience/fire.ogg"
      },
      blacksmith_forge: {
        dawn: "assets/audio/ambience/factory_background.ogg",
        day: "assets/audio/ambience/factory_background.ogg",
        dusk: "assets/audio/ambience/factory_background.ogg",
        night: "assets/audio/ambience/factory_background.ogg"
      },
      dungeon: {
        dawn: "assets/audio/ambience/water_drains_in_pipe.ogg",
        day: "assets/audio/ambience/storm_drain.ogg",
        dusk: "assets/audio/ambience/water_drains_in_pipe.ogg",
        night: "assets/audio/ambience/hallow_wind.ogg"
      },
      castle_ruins: {
        dawn: "assets/audio/ambience/room_tone_wind_blowing_long.ogg",
        day: "assets/audio/ambience/room_tone_wind_blowing_long.ogg",
        dusk: "assets/audio/ambience/hallow_wind.ogg",
        night: "assets/audio/ambience/hallow_wind.ogg"
      }
    };

    this.ambientVolumeByEnvironment = {
      village_square: 0.17,
      forest: 0.21,
      tavern: 0.24,
      market_stalls: 0.23,
      apothecary: 0.16,
      blacksmith_forge: 0.18,
      dungeon: 0.19,
      castle_ruins: 0.20
    };

    this.ambientTimeVolumeOffset = {
      dawn: -0.01,
      day: 0,
      dusk: -0.005,
      night: -0.02
    };

    // Mood intensity preset: medium (noticeable but not overpowering).
    this.moodProfiles = {
      neutral: { volumeMul: 1.0, playbackRate: 1.0, lowpassMul: 1.0, textureMul: 1.0, droneMul: 1.0 },
      happy: { volumeMul: 1.05, playbackRate: 1.015, lowpassMul: 1.05, textureMul: 1.06, droneMul: 0.97 },
      angry: { volumeMul: 1.08, playbackRate: 1.02, lowpassMul: 0.93, textureMul: 1.1, droneMul: 1.04 },
      sad: { volumeMul: 0.94, playbackRate: 0.985, lowpassMul: 0.9, textureMul: 0.9, droneMul: 0.97 },
      suspicious: { volumeMul: 0.98, playbackRate: 0.992, lowpassMul: 0.92, textureMul: 1.04, droneMul: 1.03 },
      surprised: { volumeMul: 1.03, playbackRate: 1.01, lowpassMul: 1.01, textureMul: 1.04, droneMul: 0.99 },
      thinking: { volumeMul: 0.97, playbackRate: 0.995, lowpassMul: 0.95, textureMul: 0.95, droneMul: 1.01 }
    };
  }

  _normalizeMood(mood = "neutral") {
    const m = String(mood || "neutral").toLowerCase();
    return this.moodProfiles[m] ? m : "neutral";
  }

  init() {
    if (this.ctx) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();

      // Master Gain Nodes
      this.ambientGain = this.ctx.createGain();
      this.ambientGain.gain.setValueAtTime(this.muted ? 0 : 0.07, this.ctx.currentTime);
      this.ambientGain.connect(this.ctx.destination);

      this.sfxGain = this.ctx.createGain();
      this.sfxGain.gain.setValueAtTime(this.muted ? 0 : 0.15, this.ctx.currentTime);
      this.sfxGain.connect(this.ctx.destination);

      this.noiseBuffer = this._createNoiseBuffer();
      this._initTrackLayers();
    } catch (e) {
      console.warn("Web Audio API not supported on this browser:", e);
    }
  }

  _initTrackLayers() {
    if (this.trackA && this.trackB) return;

    const makeTrack = () => {
      const audio = new Audio();
      audio.loop = true;
      audio.preload = "auto";
      audio.volume = 0;
      return audio;
    };

    this.trackA = makeTrack();
    this.trackB = makeTrack();
  }

  _getActiveTrack() {
    return this.activeTrackSlot === 0 ? this.trackA : this.trackB;
  }

  _getInactiveTrack() {
    return this.activeTrackSlot === 0 ? this.trackB : this.trackA;
  }

  _resolveAmbientTrack(environment, timeOfDay) {
    const envPack = this.ambientTrackMap[environment] || this.ambientTrackMap.village_square;
    return envPack[timeOfDay] || envPack.day || null;
  }

  _resolveAmbientVolume(environment, timeOfDay) {
    const base = this.ambientVolumeByEnvironment[environment] ?? 0.2;
    const timeOffset = this.ambientTimeVolumeOffset[timeOfDay] ?? 0;
    const moodProfile = this.moodProfiles[this.currentMood] || this.moodProfiles.neutral;
    return Math.max(0.08, Math.min(0.3, (base + timeOffset) * moodProfile.volumeMul));
  }

  _resolveTrackPlaybackRate() {
    const moodProfile = this.moodProfiles[this.currentMood] || this.moodProfiles.neutral;
    return Math.max(0.9, Math.min(1.08, moodProfile.playbackRate));
  }

  _applyMoodToTrack(track) {
    if (!track) return;
    track.playbackRate = this._resolveTrackPlaybackRate();
  }

  _fadeTrackVolume(track, from, to, durationMs) {
    if (!track) return;

    const prevHandle = this.trackFadeHandles.get(track);
    if (prevHandle) {
      cancelAnimationFrame(prevHandle);
    }

    const start = performance.now();

    const step = (now) => {
      const t = Math.min(1, (now - start) / durationMs);
      track.volume = from + (to - from) * t;
      if (t < 1) {
        const handle = requestAnimationFrame(step);
        this.trackFadeHandles.set(track, handle);
      } else {
        this.trackFadeHandles.delete(track);
      }
    };

    const handle = requestAnimationFrame(step);
    this.trackFadeHandles.set(track, handle);
  }

  _crossfadeToTrack(trackPath, targetVolume) {
    if (!this.trackA || !this.trackB) this._initTrackLayers();

    const active = this._getActiveTrack();
    const next = this._getInactiveTrack();
    if (!next) return;

    next.pause();
    next.src = trackPath;
    next.currentTime = 0;
    next.volume = 0;
    this._applyMoodToTrack(next);

    const mixVolume = this.muted ? 0 : targetVolume;
    const playPromise = next.play();
    if (playPromise && typeof playPromise.catch === "function") {
      playPromise.catch(() => {
        // Autoplay can fail until user gesture; mute toggle resumes playback.
      });
    }

    this._fadeTrackVolume(next, 0, mixVolume, 1400);
    if (active && active.src) {
      this._applyMoodToTrack(active);
      const from = Math.max(0, active.volume || 0);
      this._fadeTrackVolume(active, from, 0, 1200);
      setTimeout(() => {
        try {
          active.pause();
          active.currentTime = 0;
        } catch (e) {}
      }, 1260);
    }

    this.activeTrackSlot = this.activeTrackSlot === 0 ? 1 : 0;
    this.currentTrackPath = trackPath;
    this.currentTrackVolume = targetVolume;
  }

  _applyTrackMuteState() {
    if (!this.trackA || !this.trackB) return;

    if (this.muted) {
      this.trackA.volume = 0;
      this.trackB.volume = 0;
      this.trackA.pause();
      this.trackB.pause();
      return;
    }

    const active = this._getActiveTrack();
    if (active && active.src) {
      this._applyMoodToTrack(active);
      const p = active.play();
      if (p && typeof p.catch === "function") {
        p.catch(() => {});
      }
      this._fadeTrackVolume(active, Math.max(0, active.volume || 0), this.currentTrackVolume, 500);
    }
  }

  setMood(mood = "neutral") {
    const normalizedMood = this._normalizeMood(mood);
    if (normalizedMood === this.currentMood) return;

    this.currentMood = normalizedMood;

    const active = this._getActiveTrack();
    if (active) {
      this._applyMoodToTrack(active);
      if (!this.muted && active.src) {
        const retarget = this._resolveAmbientVolume(this.lastEnvironment, this.lastTimeOfDay);
        this.currentTrackVolume = retarget;
        this._fadeTrackVolume(active, Math.max(0, active.volume || 0), retarget, 550);
      }
    }

    // Rebuild procedural layer with the updated mood timbre profile.
    if (this.ctx && !this.muted) {
      this.currentAtmosphere = null;
      this.setAtmosphere(this.lastEnvironment, this.lastTimeOfDay);
    }
  }

  toggleMute() {
    this.init();
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }

    this.muted = !this.muted;

    if (this.ambientGain && this.sfxGain) {
      const now = this.ctx.currentTime;
      this.ambientGain.gain.cancelScheduledValues(now);
      this.ambientGain.gain.linearRampToValueAtTime(this.muted ? 0 : 0.07, now + 0.3);

      this.sfxGain.gain.cancelScheduledValues(now);
      this.sfxGain.gain.linearRampToValueAtTime(this.muted ? 0 : 0.15, now + 0.1);
    }

    if (this.muted) {
      this.ambientTimers.forEach(timerId => clearTimeout(timerId));
      this.ambientTimers = [];
    } else {
      // Force event scheduler refresh when unmuting in the same scene.
      this.currentAtmosphere = null;
    }

    this._applyTrackMuteState();

    if (!this.muted && !this.currentAtmosphere) {
      this.setAtmosphere("village_square", "day");
    }

    return !this.muted;
  }

  /**
   * Procedural Typewriter Blip / Dialogue Character sound
   */
  playTypeBlip(char = "a") {
    if (this.muted || !this.ctx) return;

    // Pitch variation per character code for natural dialogue chime
    const baseFreq = 380;
    const charOffset = (char.charCodeAt(0) % 12) * 18;
    const freq = baseFreq + charOffset;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

    // Fast envelope (blip)
    gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.045);

    osc.connect(gain);
    gain.connect(this.sfxGain);

    osc.start();
    osc.stop(this.ctx.currentTime + 0.05);
  }

  /**
   * UI Click Sound
   */
  playClick() {
    if (this.muted || !this.ctx) return;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = "triangle";
    osc.frequency.setValueAtTime(520, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + 0.08);

    gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08);

    osc.connect(gain);
    gain.connect(this.sfxGain);

    osc.start();
    osc.stop(this.ctx.currentTime + 0.09);
  }

  /**
   * Quest / Reputation chime
   */
  playChime(isPositive = true) {
    if (this.muted || !this.ctx) return;

    const notes = isPositive ? [523.25, 659.25, 783.99, 1046.5] : [440, 415.3, 392, 349.2];
    notes.forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime + i * 0.08);

      const startTime = this.ctx.currentTime + i * 0.08;
      gain.gain.setValueAtTime(0.1, startTime);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.35);

      osc.connect(gain);
      gain.connect(this.sfxGain);

      osc.start(startTime);
      osc.stop(startTime + 0.36);
    });
  }

  _normalizeEnvironment(environment = "village_square") {
    const env = String(environment || "village_square").toLowerCase();

    if (env.includes("forest") || env.includes("woods")) return "forest";
    if (env.includes("tavern") || env.includes("inn")) return "tavern";
    if (env.includes("dungeon") || env.includes("crypt") || env.includes("cave")) return "dungeon";
    if (env.includes("castle") || env.includes("ruins")) return "castle_ruins";
    if (env.includes("forge") || env.includes("blacksmith")) return "blacksmith_forge";
    if (env.includes("apothecary") || env.includes("herbal")) return "apothecary";
    if (env.includes("market") || env.includes("stalls") || env.includes("bazaar")) return "market_stalls";
    if (env.includes("village") || env.includes("town") || env.includes("square")) return "village_square";

    return "village_square";
  }

  _normalizeTime(timeOfDay = "day") {
    const time = String(timeOfDay || "day").toLowerCase();
    if (time === "morning") return "dawn";
    if (time === "afternoon") return "day";
    if (time === "evening") return "dusk";
    if (["dawn", "day", "dusk", "night"].includes(time)) return time;
    return "day";
  }

  _createNoiseBuffer() {
    if (!this.ctx) return null;
    const sampleRate = this.ctx.sampleRate;
    const length = sampleRate * 2;
    const buffer = this.ctx.createBuffer(1, length, sampleRate);
    const channel = buffer.getChannelData(0);

    for (let i = 0; i < length; i++) {
      channel[i] = Math.random() * 2 - 1;
    }

    return buffer;
  }

  _makeNoiseLayer(type = "bandpass", freq = 800, q = 0.8, gainValue = 0.02) {
    if (!this.ctx || !this.noiseBuffer) return null;

    const source = this.ctx.createBufferSource();
    source.buffer = this.noiseBuffer;
    source.loop = true;

    const filter = this.ctx.createBiquadFilter();
    filter.type = type;
    filter.frequency.setValueAtTime(freq, this.ctx.currentTime);
    filter.Q.setValueAtTime(q, this.ctx.currentTime);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(gainValue, this.ctx.currentTime);

    source.connect(filter);
    filter.connect(gain);

    return { source, filter, gain };
  }

  _registerAmbientNode(node) {
    if (node) this.ambientNodes.push(node);
  }

  _clearAmbientLayer() {
    this.ambientTimers.forEach(timerId => clearTimeout(timerId));
    this.ambientTimers = [];

    const now = this.ctx ? this.ctx.currentTime : 0;
    this.ambientNodes.forEach(node => {
      try {
        if (node.gain && node.gain.gain) {
          node.gain.gain.cancelScheduledValues(now);
          const currentVal = Math.max(0.0001, node.gain.gain.value || 0.0001);
          node.gain.gain.setValueAtTime(currentVal, now);
          node.gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
        }
      } catch (e) {}

      setTimeout(() => {
        try {
          if (node.osc1) node.osc1.stop();
          if (node.osc2) node.osc2.stop();
          if (node.lfo) node.lfo.stop();
          if (node.source) node.source.stop();
        } catch (e) {}

        try {
          if (node.osc1) node.osc1.disconnect();
          if (node.osc2) node.osc2.disconnect();
          if (node.filter) node.filter.disconnect();
          if (node.lfo) node.lfo.disconnect();
          if (node.lfoGain) node.lfoGain.disconnect();
          if (node.source) node.source.disconnect();
          if (node.gain) node.gain.disconnect();
        } catch (e) {}
      }, 420);
    });

    this.ambientNodes = [];
  }

  _createDroneLayer(profile) {
    const now = this.ctx.currentTime;
    const layerGain = this.ctx.createGain();
    layerGain.gain.setValueAtTime(0.0001, now);
    layerGain.gain.exponentialRampToValueAtTime(profile.droneGain, now + 1.2);

    const filter = this.ctx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(profile.lowpass, now);

    const osc1 = this.ctx.createOscillator();
    osc1.type = profile.wave1;
    osc1.frequency.setValueAtTime(profile.freq1, now);

    const osc2 = this.ctx.createOscillator();
    osc2.type = profile.wave2;
    osc2.frequency.setValueAtTime(profile.freq2, now);

    const lfo = this.ctx.createOscillator();
    lfo.type = "sine";
    lfo.frequency.setValueAtTime(profile.motionRate, now);

    const lfoGain = this.ctx.createGain();
    lfoGain.gain.setValueAtTime(profile.motionDepth, now);

    lfo.connect(lfoGain);
    lfoGain.connect(filter.frequency);

    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(layerGain);
    layerGain.connect(this.ambientGain);

    osc1.start();
    osc2.start();
    lfo.start();

    this._registerAmbientNode({ osc1, osc2, filter, lfo, lfoGain, gain: layerGain });
  }

  _createTextureLayer(profile) {
    const noiseLayer = this._makeNoiseLayer("bandpass", profile.textureFreq, 0.8, profile.textureGain);
    if (!noiseLayer) return;

    noiseLayer.gain.connect(this.ambientGain);
    noiseLayer.source.start();

    this._registerAmbientNode(noiseLayer);
  }

  _playChirp() {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(2200 + Math.random() * 1400, now);

    osc.type = "triangle";
    const start = 1400 + Math.random() * 700;
    const end = 2600 + Math.random() * 800;
    osc.frequency.setValueAtTime(start, now);
    osc.frequency.exponentialRampToValueAtTime(end, now + 0.08);

    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.02, now + 0.015);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.11);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.ambientGain);

    osc.start();
    osc.stop(now + 0.12);

    setTimeout(() => {
      try {
        osc.disconnect();
        filter.disconnect();
        gain.disconnect();
      } catch (e) {}
    }, 180);
  }

  _playForgeClang() {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();
    filter.type = "highpass";
    filter.frequency.setValueAtTime(900, now);

    osc.type = "square";
    osc.frequency.setValueAtTime(420 + Math.random() * 80, now);
    osc.frequency.exponentialRampToValueAtTime(160, now + 0.22);

    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.018, now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.28);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.ambientGain);

    osc.start();
    osc.stop(now + 0.3);

    setTimeout(() => {
      try {
        osc.disconnect();
        filter.disconnect();
        gain.disconnect();
      } catch (e) {}
    }, 420);
  }

  _playDripEcho() {
    if (!this.ctx || this.muted) return;
    const now = this.ctx.currentTime;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const delay = this.ctx.createDelay();
    const feedback = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();

    filter.type = "lowpass";
    filter.frequency.setValueAtTime(1200, now);

    delay.delayTime.setValueAtTime(0.19, now);
    feedback.gain.setValueAtTime(0.34, now);

    osc.type = "sine";
    osc.frequency.setValueAtTime(520 + Math.random() * 90, now);
    osc.frequency.exponentialRampToValueAtTime(180, now + 0.16);

    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.012, now + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.17);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.ambientGain);

    gain.connect(delay);
    delay.connect(feedback);
    feedback.connect(delay);
    delay.connect(this.ambientGain);

    osc.start();
    osc.stop(now + 0.2);

    setTimeout(() => {
      try {
        osc.disconnect();
        gain.disconnect();
        delay.disconnect();
        feedback.disconnect();
        filter.disconnect();
      } catch (e) {}
    }, 700);
  }

  _scheduleRepeatingEvent(callback, minMs, maxMs, token) {
    const loop = () => {
      if (this.atmosphereToken !== token || this.muted) return;
      callback();
      const nextDelay = minMs + Math.random() * (maxMs - minMs);
      const timerId = setTimeout(loop, nextDelay);
      this.ambientTimers.push(timerId);
    };

    const firstDelay = minMs + Math.random() * (maxMs - minMs);
    const timerId = setTimeout(loop, firstDelay);
    this.ambientTimers.push(timerId);
  }

  _scheduleEnvironmentEvents(environment, timeOfDay, token) {
    const isNight = timeOfDay === "night";

    if (environment === "forest") {
      this._scheduleRepeatingEvent(() => this._playChirp(), isNight ? 1200 : 1800, isNight ? 2600 : 4200, token);
    }

    if (environment === "village_square" || environment === "market_stalls") {
      this._scheduleRepeatingEvent(() => this._playChirp(), isNight ? 2400 : 3800, isNight ? 5200 : 6400, token);
    }

    if (environment === "blacksmith_forge") {
      this._scheduleRepeatingEvent(() => this._playForgeClang(), 3200, 7800, token);
    }

    if (environment === "dungeon" || environment === "castle_ruins") {
      this._scheduleRepeatingEvent(() => this._playDripEcho(), 2500, 6200, token);
    }

    if (environment === "tavern") {
      this._scheduleRepeatingEvent(() => {
        if (!this.ctx || !this.noiseBuffer) return;
        const layer = this._makeNoiseLayer("bandpass", 520 + Math.random() * 260, 1.1, 0.008);
        if (!layer) return;
        layer.gain.connect(this.ambientGain);
        layer.source.start();
        const now = this.ctx.currentTime;
        layer.gain.gain.setValueAtTime(0.0001, now);
        layer.gain.gain.exponentialRampToValueAtTime(0.016, now + 0.08);
        layer.gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.6);
        layer.source.stop(now + 0.62);

        setTimeout(() => {
          try {
            layer.source.disconnect();
            layer.filter.disconnect();
            layer.gain.disconnect();
          } catch (e) {}
        }, 760);
      }, 1800, 3600, token);
    }
  }

  _buildAtmosphereProfile(environment, timeOfDay) {
    const isNight = timeOfDay === "night";
    const moodProfile = this.moodProfiles[this.currentMood] || this.moodProfiles.neutral;
    const baseProfiles = {
      village_square: { freq1: 160, freq2: 238, wave1: "sine", wave2: "triangle", lowpass: 980, textureFreq: 1400 },
      market_stalls: { freq1: 172, freq2: 256, wave1: "triangle", wave2: "sawtooth", lowpass: 1200, textureFreq: 1800 },
      forest: { freq1: 132, freq2: 198, wave1: "sine", wave2: "triangle", lowpass: 900, textureFreq: 1050 },
      tavern: { freq1: 196, freq2: 294, wave1: "triangle", wave2: "sawtooth", lowpass: 720, textureFreq: 620 },
      apothecary: { freq1: 146, freq2: 220, wave1: "sine", wave2: "triangle", lowpass: 800, textureFreq: 980 },
      blacksmith_forge: { freq1: 98, freq2: 147, wave1: "sawtooth", wave2: "square", lowpass: 640, textureFreq: 560 },
      dungeon: { freq1: 73, freq2: 109, wave1: "sine", wave2: "triangle", lowpass: 470, textureFreq: 430 },
      castle_ruins: { freq1: 84, freq2: 126, wave1: "triangle", wave2: "sine", lowpass: 520, textureFreq: 500 }
    };

    const base = baseProfiles[environment] || baseProfiles.village_square;
    const timeMul = isNight ? 0.86 : (timeOfDay === "dawn" ? 0.95 : 1.0);

    return {
      freq1: base.freq1 * timeMul,
      freq2: base.freq2 * timeMul,
      wave1: base.wave1,
      wave2: base.wave2,
      lowpass: (isNight ? base.lowpass * 0.82 : base.lowpass) * moodProfile.lowpassMul,
      textureFreq: isNight ? base.textureFreq * 0.72 : base.textureFreq,
      droneGain: (isNight ? 0.03 : 0.04) * moodProfile.droneMul,
      textureGain: (isNight ? 0.006 : 0.009) * moodProfile.textureMul,
      motionRate: isNight ? 0.035 : 0.05,
      motionDepth: isNight ? 80 : 110
    };
  }

  /**
   * Update procedural ambient atmosphere according to environment and time.
   */
  setAtmosphere(environment = "village_square", timeOfDay = "day") {
    if (!this.ctx) {
      this.init();
    }
    if (!this.ctx) return;

    const env = this._normalizeEnvironment(environment);
    const tod = this._normalizeTime(timeOfDay);
    this.lastEnvironment = env;
    this.lastTimeOfDay = tod;

    const atmosphereKey = `${env}_${tod}`;
    const ambientTrack = this._resolveAmbientTrack(env, tod);
    const targetTrackVolume = this._resolveAmbientVolume(env, tod);

    if (this.currentAtmosphere === atmosphereKey) return;

    this._clearAmbientLayer();

    if (ambientTrack && ambientTrack !== this.currentTrackPath) {
      this._crossfadeToTrack(ambientTrack, targetTrackVolume);
    } else {
      this.currentTrackVolume = targetTrackVolume;
      const active = this._getActiveTrack();
      if (active && active.src && !this.muted) {
        this._fadeTrackVolume(active, Math.max(0, active.volume || 0), targetTrackVolume, 600);
      }
    }

    const profile = this._buildAtmosphereProfile(env, tod);
    this._createDroneLayer(profile);
    this._createTextureLayer(profile);

    this.atmosphereToken += 1;
    this._scheduleEnvironmentEvents(env, tod, this.atmosphereToken);

    this.currentAtmosphere = atmosphereKey;
  }
}

// Global audio engine instance
window.audioEngine = new AudioEngine();
