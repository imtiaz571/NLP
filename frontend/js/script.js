/**
 * NPC Talk — Visual Novel Dialogue Controller
 * Plain Vanilla JavaScript implementation.
 * Manages dialogue state, typewriter animations, background crossfading,
 * character emotions, and interactive controls.
 */

class NPCTalkApp {
  constructor() {
    // ── Core State ──────────────────────────────────────────────────────
    this.currentNPCId = "ash";
    this.currentEmotion = "neutral";
    this.gameState = JSON.parse(JSON.stringify(CONFIG.defaultGameState));
    this.conversationHistory = [];
    this.playerId = "player_1";

    // ── Player Profile State (Gender, Age, Occupation) ──────────────────
    this.playerProfile = {
      name: "Traveler",
      gender: "male",
      age: 24,
      age_group: "adult",
      occupation: "mercenary"
    };

    // ── Animation & Typewriter State ────────────────────────────────────
    this.isTypewriting = false;
    this.currentDisplayedText = "";
    this.targetFullText = "";
    this.typewriterTimer = null;
    this.typewriterSpeedMs = 14;
    this.isWaitingResponse = false;
    this.activeBgLayer = 1;
    this.stateSyncVersion = 0;

    // ── DOM Element References ──────────────────────────────────────────────
    this.dom = {
      // Stage & Backgrounds
      bgLayer1: document.getElementById("bg-layer-1"),
      bgLayer2: document.getElementById("bg-layer-2"),
      bgTint: document.getElementById("bg-tint-overlay"),
      particlesContainer: document.getElementById("particles-container"),
      letterboxTop: document.getElementById("letterbox-top"),
      letterboxBottom: document.getElementById("letterbox-bottom"),

      // Character Stage
      characterStage: document.getElementById("character-stage"),
      characterPortrait: document.getElementById("character-portrait"),
      characterThinkingBubble: document.getElementById("character-thinking-bubble"),

      // Emotion Overlay Badge
      emotionOverlay: document.getElementById("emotion-overlay"),
      emotionOverlayIcon: document.getElementById("emotion-overlay-icon"),

      // Dialogue Box
      dialoguePanel: document.getElementById("dialogue-panel"),
      npcNameTag: document.getElementById("npc-name-tag"),
      npcTitleTag: document.getElementById("npc-title-tag"),
      moodBadge: document.getElementById("mood-badge-btn") || document.getElementById("mood-badge"),
      moodBadgeBtn: document.getElementById("mood-badge-btn"),
      moodDropdown: document.getElementById("mood-dropdown"),
      moodIcon: document.getElementById("mood-icon"),
      moodLabel: document.getElementById("mood-label"),
      dialogueText: document.getElementById("dialogue-text"),
      advanceIndicator: document.getElementById("advance-indicator"),

      // Resource pill bars (CoC HUD — replace old affinity bar)
      resRepFill: document.getElementById("res-rep-fill"),
      resRepVal: document.getElementById("res-rep-val"),
      resQuestFill: document.getElementById("res-quest-fill"),
      resQuestVal: document.getElementById("res-quest-val"),

      // Player Controls
      playerInput: document.getElementById("player-input"),
      sendBtn: document.getElementById("send-btn"),
      choiceChipsContainer: document.getElementById("choice-chips-container"),
      playerQueryText: document.getElementById("player-query-text"),

      // Top HUD
      locationBadgeText: document.getElementById("hud-location-text"),
      timeBadgeText: document.getElementById("hud-time-text"),
      audioToggleBtn: document.getElementById("audio-toggle-btn"),
      historyToggleBtn: document.getElementById("history-toggle-btn"),
      gearBtn: document.getElementById("gear-btn"),
      hudProfileBtn: document.getElementById("hud-profile-btn"),
      hudProfileName: document.getElementById("hud-profile-name"),
      hudProfileTag: document.getElementById("hud-profile-tag"),
      npcRoster: document.getElementById("npc-roster"),
      questTracker: document.getElementById("quest-tracker"),
      questObjective: document.getElementById("quest-objective"),
      questProgressText: document.getElementById("quest-progress-text"),

      // Interactive HUD Dropdowns
      hudLocationBtn: document.getElementById("hud-location-btn"),
      hudLocationDropdown: document.getElementById("hud-location-dropdown"),
      hudTimeBtn: document.getElementById("hud-time-btn"),
      hudTimeDropdown: document.getElementById("hud-time-dropdown"),
      hudRepBtn: document.getElementById("hud-rep-btn"),
      hudRepDropdown: document.getElementById("hud-rep-dropdown"),
      hudRepCurrentNum: document.getElementById("hud-rep-current-num"),
      hudRepMinusBtn: document.getElementById("hud-rep-minus-btn"),
      hudRepPlusBtn: document.getElementById("hud-rep-plus-btn"),
      hudRepResetBtn: document.getElementById("hud-rep-reset-btn"),

      // Modals & Drawers
      welcomeModal: document.getElementById("welcome-modal"),
      splashScreenContainer: document.getElementById("splash-screen-container"),
      welcomeModalCard: document.getElementById("welcome-modal-card"),
      splashSkipBtn: document.getElementById("splash-skip-btn"),
      occupationOtherWrapper: document.getElementById("occupation-other-wrapper"),
      occupationOtherInput: document.getElementById("occupation-other-input"),
      closeWelcomeBtn: document.getElementById("close-welcome-btn"),
      startJourneyBtn: document.getElementById("start-journey-btn"),
      playerNameInput: document.getElementById("player-name-input"),
      randomNameBtn: document.getElementById("random-name-btn"),
      historyModal: document.getElementById("history-modal"),
      historyList: document.getElementById("history-list"),
      closeHistoryBtn: document.getElementById("close-history-btn"),
      clearHistoryBtn: document.getElementById("clear-history-btn"),
      settingsDrawer: document.getElementById("settings-drawer"),
      closeSettingsBtn: document.getElementById("close-settings-btn"),
      drawerEditProfileBtn: document.getElementById("drawer-edit-profile-btn"),

      // Settings Inputs
      selectNpc: document.getElementById("setting-select-npc"),
      selectEnv: document.getElementById("setting-select-env"),
      selectTime: document.getElementById("setting-select-time"),
      selectEmotion: document.getElementById("setting-select-emotion"),
      selectRep: document.getElementById("setting-select-rep")
    };
  }

  /**
   * Initialize Application
   */
  init() {
    this.loadSavedPlayerProfile();
    this.setupLetterbox();
    this.setupEventListeners();
    this.setupProfileModalEvents();
    this.populateSettingsDropdowns();
    this.buildNPCRoster();
    this.loadNPC(this.currentNPCId, true);
    this.updateBackground(this.gameState.location, this.gameState.time_of_day, false);
    this.updateAffinityDisplay();
    this.updateHUD();
    this.updateProfileHUD();

    // ALWAYS display the animated two-stage welcoming sequence on startup
    this.openWelcomeSequence();

    // Recompute letterbox on resize
    window.addEventListener("resize", () => this.setupLetterbox());

    console.log("Thornhaven dialogue interface initialized.");
  }

  /**
   * Calculate and apply letterbox bar heights so black bars appear
   * above/below the 16:9 #vn-container when viewport is wider than 16:9.
   */
  setupLetterbox() {
    const viewW = window.innerWidth;
    const viewH = window.innerHeight;
    const containerH = Math.min(viewH, viewW * 9 / 16);
    const barH = Math.max(0, (viewH - containerH) / 2);
    if (this.dom.letterboxTop)    this.dom.letterboxTop.style.height    = `${barH}px`;
    if (this.dom.letterboxBottom) this.dom.letterboxBottom.style.height = `${barH}px`;
  }

  /**
   * Bind DOM & Keyboard Events
   */
  setupEventListeners() {
    // Player message submission
    this.dom.sendBtn.addEventListener("click", () => this.handlePlayerSendMessage());
    this.dom.playerInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.handlePlayerSendMessage();
      }
    });

    // Click dialogue box to instantly complete typewriter reveal
    this.dom.dialoguePanel.addEventListener("click", (e) => {
      // Don't trigger skip if user clicked the input box or choice buttons
      if (e.target.closest("#player-input-wrapper") || e.target.closest("#choice-chips-container")) {
        return;
      }
      if (this.isTypewriting) {
        this.skipTypewriter();
      }
    });

    // Game-style keyboard controls. Inputs and open overlays always take priority.
    window.addEventListener("keydown", (e) => {
      const activeElement = document.activeElement;
      const isTyping = activeElement && (
        activeElement.tagName === "INPUT"
        || activeElement.tagName === "TEXTAREA"
        || activeElement.tagName === "SELECT"
        || activeElement.isContentEditable
      );
      const overlayOpen = [this.dom.welcomeModal, this.dom.historyModal, this.dom.settingsDrawer]
        .filter(Boolean)
        .some(element => element.classList.contains("visible") || element.classList.contains("open"));

      if (isTyping || overlayOpen || e.altKey || e.ctrlKey || e.metaKey) return;

      if (e.code === "Space" && this.isTypewriting) {
        e.preventDefault();
        this.skipTypewriter();
        return;
      }

      if (/^[1-5]$/.test(e.key) && !this.isWaitingResponse) {
        const choice = this.dom.choiceChipsContainer.querySelectorAll(".choice-chip")[Number(e.key) - 1];
        if (choice) {
          e.preventDefault();
          choice.click();
        }
        return;
      }

      if (e.key.toLowerCase() === "l") {
        e.preventDefault();
        this.dom.historyToggleBtn.click();
      } else if (e.key.toLowerCase() === "m") {
        e.preventDefault();
        this.dom.audioToggleBtn.click();
      }
    });

    // Audio Toggle
    this.dom.audioToggleBtn.addEventListener("click", () => {
      const isUnmuted = window.audioEngine.toggleMute();
      this.dom.audioToggleBtn.classList.toggle("text-primary", isUnmuted);
      this.dom.audioToggleBtn.title = isUnmuted ? "Mute Atmospheric Audio (Key: M)" : "Unmute Atmospheric Audio (Key: M)";
      const icon = this.dom.audioToggleBtn.querySelector(".material-symbols-outlined");
      if (icon) icon.textContent = isUnmuted ? "volume_up" : "volume_off";
      if (isUnmuted) {
        window.audioEngine.setAtmosphere(this.gameState.location, this.gameState.time_of_day);
      }
    });

    // Mobile Navigation Buttons
    const mobSpeakBtn = document.getElementById("mob-speak-btn");
    if (mobSpeakBtn) mobSpeakBtn.addEventListener("click", () => this.dom.playerInput.focus());

    const mobRosterBtn = document.getElementById("mob-roster-btn");
    if (mobRosterBtn) mobRosterBtn.addEventListener("click", () => this.toggleSettingsDrawer(true));

    const mobLogBtn = document.getElementById("mob-log-btn");
    if (mobLogBtn) mobLogBtn.addEventListener("click", () => this.openHistoryModal());

    const mobSettingsBtn = document.getElementById("mob-settings-btn");
    if (mobSettingsBtn) mobSettingsBtn.addEventListener("click", () => this.toggleSettingsDrawer(true));

    // History Log Toggle
    this.dom.historyToggleBtn.addEventListener("click", () => this.openHistoryModal());
    this.dom.closeHistoryBtn.addEventListener("click", () => this.closeHistoryModal());
    if (this.dom.clearHistoryBtn) {
      this.dom.clearHistoryBtn.addEventListener("click", () => this.clearHistory());
    }

    // Gear button → Settings Drawer (new top-left CoC gear icon)
    if (this.dom.gearBtn) {
      this.dom.gearBtn.addEventListener("click", () => {
        this.toggleSettingsDrawer();
        window.audioEngine.playClick();
      });
    }

    // Settings Drawer close button
    this.dom.closeSettingsBtn.addEventListener("click", () => this.toggleSettingsDrawer(false));

    // Live Settings Change Handlers
    this.dom.selectNpc.addEventListener("change", (e) => {
      this.loadNPC(e.target.value);
      window.audioEngine.playClick();
    });

    this.dom.selectEnv.addEventListener("change", (e) => {
      this.gameState.location = e.target.value;
      this.updateBackground(this.gameState.location, this.gameState.time_of_day, true);
      this.updateHUD();
      void this.syncStateToBackend({ location: this.gameState.location });
      window.audioEngine.playClick();
    });

    this.dom.selectTime.addEventListener("change", (e) => {
      this.gameState.time_of_day = e.target.value;
      this.updateBackground(this.gameState.location, this.gameState.time_of_day, true);
      this.updateHUD();
      void this.syncStateToBackend({ time_of_day: this.gameState.time_of_day });
      window.audioEngine.playClick();
    });

    if (this.dom.selectEmotion) {
      this.dom.selectEmotion.addEventListener("change", (e) => {
        this.setEmotion(e.target.value, true);
        window.audioEngine.playClick();
      });
    }

    this.dom.selectRep.addEventListener("change", (e) => {
      this.gameState.reputation = parseInt(e.target.value, 10);
      this.updateAffinityDisplay();
      void this.syncStateToBackend({
        reputation: {
          player_id: this.playerId,
          npc_id: this.currentNPCId,
          value: this.gameState.reputation
        }
      });
      window.audioEngine.playChime(this.gameState.reputation >= 0);
    });

    // ── Interactive Top HUD Dropdowns & Controls ──
    const closeAllHUDDropdowns = () => {
      if (this.dom.hudLocationDropdown) this.dom.hudLocationDropdown.classList.add("hidden");
      if (this.dom.hudTimeDropdown) this.dom.hudTimeDropdown.classList.add("hidden");
      if (this.dom.hudRepDropdown) this.dom.hudRepDropdown.classList.add("hidden");
      if (this.dom.moodDropdown) this.dom.moodDropdown.classList.add("hidden");
    };

    // 1. Location Dropdown Toggle
    if (this.dom.hudLocationBtn) {
      this.dom.hudLocationBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const wasHidden = this.dom.hudLocationDropdown.classList.contains("hidden");
        closeAllHUDDropdowns();
        if (wasHidden) this.dom.hudLocationDropdown.classList.remove("hidden");
        window.audioEngine.playClick();
      });
    }

    // Location Item Clicks
    document.querySelectorAll(".loc-dropdown-item").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const loc = btn.dataset.loc;
        if (loc) {
          this.gameState.location = loc;
          if (this.dom.selectEnv) this.dom.selectEnv.value = loc;
          this.updateBackground(this.gameState.location, this.gameState.time_of_day, true);
          this.updateHUD();
          void this.syncStateToBackend({ location: this.gameState.location });
          window.audioEngine.playClick();
        }
        closeAllHUDDropdowns();
      });
    });

    // 2. Time of Day Dropdown Toggle
    if (this.dom.hudTimeBtn) {
      this.dom.hudTimeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const wasHidden = this.dom.hudTimeDropdown.classList.contains("hidden");
        closeAllHUDDropdowns();
        if (wasHidden) this.dom.hudTimeDropdown.classList.remove("hidden");
        window.audioEngine.playClick();
      });
    }

    // Time Item Clicks
    document.querySelectorAll(".time-dropdown-item").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const time = btn.dataset.time;
        if (time) {
          this.gameState.time_of_day = time;
          if (this.dom.selectTime) this.dom.selectTime.value = time;
          this.updateBackground(this.gameState.location, this.gameState.time_of_day, true);
          this.updateHUD();
          void this.syncStateToBackend({ time_of_day: this.gameState.time_of_day });
          window.audioEngine.playClick();
        }
        closeAllHUDDropdowns();
      });
    });

    // 3. Reputation Dropdown Toggle
    if (this.dom.hudRepBtn) {
      this.dom.hudRepBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const wasHidden = this.dom.hudRepDropdown.classList.contains("hidden");
        closeAllHUDDropdowns();
        if (wasHidden) {
          if (this.dom.hudRepCurrentNum) {
            this.dom.hudRepCurrentNum.textContent = (this.gameState.reputation >= 0 ? "+" : "") + this.gameState.reputation;
          }
          this.dom.hudRepDropdown.classList.remove("hidden");
        }
        window.audioEngine.playClick();
      });
    }

    // Reputation Preset Item Clicks
    document.querySelectorAll(".rep-dropdown-item").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const repVal = parseInt(btn.dataset.rep, 10);
        if (!isNaN(repVal)) {
          this.setReputationDirectly(repVal);
        }
        closeAllHUDDropdowns();
      });
    });

    // Reputation Nudge Buttons (+1, -1, Reset)
    if (this.dom.hudRepMinusBtn) {
      this.dom.hudRepMinusBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.setReputationDirectly(Math.max(-5, (this.gameState.reputation || 0) - 1));
      });
    }
    if (this.dom.hudRepPlusBtn) {
      this.dom.hudRepPlusBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.setReputationDirectly(Math.min(5, (this.gameState.reputation || 0) + 1));
      });
    }
    if (this.dom.hudRepResetBtn) {
      this.dom.hudRepResetBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        this.setReputationDirectly(0);
      });
    }

    // 4. Mood / Emotion Dropdown Toggle
    if (this.dom.moodBadgeBtn) {
      this.dom.moodBadgeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const wasHidden = this.dom.moodDropdown.classList.contains("hidden");
        closeAllHUDDropdowns();
        if (wasHidden) this.dom.moodDropdown.classList.remove("hidden");
        window.audioEngine.playClick();
      });
    }

    if (this.dom.emotionOverlay) {
      this.dom.emotionOverlay.addEventListener("click", (e) => {
        e.stopPropagation();
        const wasHidden = this.dom.moodDropdown.classList.contains("hidden");
        closeAllHUDDropdowns();
        if (wasHidden) this.dom.moodDropdown.classList.remove("hidden");
        window.audioEngine.playClick();
      });
    }

    // Emotion Preset Item Clicks
    document.querySelectorAll(".emotion-dropdown-item").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const emotion = btn.dataset.emotion;
        if (emotion) {
          this.setEmotion(emotion, true);
          window.audioEngine.playChime(true);
        }
        closeAllHUDDropdowns();
      });
    });

    // Close HUD dropdowns on outside click or Escape
    document.addEventListener("click", () => closeAllHUDDropdowns());
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeAllHUDDropdowns();
    });
  }

  /**
   * Set reputation directly from HUD quick controls
   */
  setReputationDirectly(repVal) {
    this.gameState.reputation = repVal;
    if (this.dom.selectRep) this.dom.selectRep.value = String(repVal);
    if (this.dom.hudRepCurrentNum) {
      this.dom.hudRepCurrentNum.textContent = (repVal >= 0 ? "+" : "") + repVal;
    }
    this.updateAffinityDisplay();
    void this.syncStateToBackend({
      reputation: {
        player_id: this.playerId,
        npc_id: this.currentNPCId,
        value: this.gameState.reputation
      }
    });
    window.audioEngine.playChime(this.gameState.reputation >= 0);
  }

  /**
   * Load and Persist Player Profile from LocalStorage
   */
  loadSavedPlayerProfile() {
    try {
      const saved = localStorage.getItem("npc_talk_player_profile");
      if (saved) {
        const parsed = JSON.parse(saved);
        this.playerProfile = Object.assign(this.playerProfile, parsed);
      }
    } catch (e) {
      console.warn("Could not parse saved player profile:", e);
    }
  }

  /**
   * Setup Player Profile Creator Modal Events
   */
  setupProfileModalEvents() {
    if (this.dom.hudProfileBtn) {
      this.dom.hudProfileBtn.addEventListener("click", () => this.openWelcomeModal(true));
    }

    if (this.dom.drawerEditProfileBtn) {
      this.dom.drawerEditProfileBtn.addEventListener("click", () => {
        this.toggleSettingsDrawer(false);
        this.openWelcomeModal(true);
      });
    }

    if (this.dom.closeWelcomeBtn) {
      this.dom.closeWelcomeBtn.addEventListener("click", () => this.closeWelcomeModal());
    }

    if (this.dom.welcomeModal) {
      this.dom.welcomeModal.addEventListener("click", (e) => {
        if (e.target === this.dom.welcomeModal && !this.isInSplashSequence) {
          this.closeWelcomeModal();
        }
      });
    }

    if (this.dom.splashSkipBtn) {
      this.dom.splashSkipBtn.addEventListener("click", () => {
        this.transitionToStage2();
      });
    }

    if (this.dom.randomNameBtn) {
      this.dom.randomNameBtn.addEventListener("click", () => {
        const names = ["Valen", "Lyra", "Rowan", "Kaelen", "Aria", "Thorne", "Elowen", "Dorian", "Sylvan", "Mira", "Bran", "Talia", "Corin", "Zephyr", "Isolde"];
        const chosen = names[Math.floor(Math.random() * names.length)];
        this.dom.playerNameInput.value = chosen;
        window.audioEngine.playClick();
      });
    }

    // Radio card selection in welcome modal
    document.querySelectorAll("#welcome-modal .radio-card").forEach(card => {
      card.addEventListener("click", () => {
        const parent = card.parentElement;
        parent.querySelectorAll(".radio-card").forEach(c => c.classList.remove("active"));
        card.classList.add("active");
        window.audioEngine.playClick();

        // Handle "Other" custom occupation toggle
        if (card.dataset.occupation !== undefined) {
          if (card.dataset.occupation === "other") {
            if (this.dom.occupationOtherWrapper) {
              this.dom.occupationOtherWrapper.classList.add("visible");
              if (this.dom.occupationOtherInput) {
                setTimeout(() => this.dom.occupationOtherInput.focus(), 150);
              }
            }
          } else {
            if (this.dom.occupationOtherWrapper) {
              this.dom.occupationOtherWrapper.classList.remove("visible");
            }
          }
        }
      });
    });

    if (this.dom.startJourneyBtn) {
      this.dom.startJourneyBtn.addEventListener("click", () => {
        this.saveProfileFromModal();
      });
    }
  }

  /**
   * Two-Stage Welcome Sequence: Stage 1 Splash -> Stage 2 Form
   */
  openWelcomeSequence() {
    if (!this.dom.welcomeModal) return;

    this.isInSplashSequence = true;
    this.dom.welcomeModal.classList.add("visible", "active");
    this.dom.welcomeModal.style.display = "flex";

    // Setup Stage 1 Splash
    if (this.dom.splashScreenContainer) {
      this.dom.splashScreenContainer.classList.remove("splash-fade-out");
      this.dom.splashScreenContainer.style.display = "flex";
    }

    // Setup Stage 2 Card (Hidden initially)
    if (this.dom.welcomeModalCard) {
      this.dom.welcomeModalCard.classList.add("stage-hidden");
      this.dom.welcomeModalCard.classList.remove("stage-active");
    }

    // Reset staggered input groups
    document.querySelectorAll("#welcome-modal .profile-input-group").forEach(grp => {
      grp.classList.remove("stage-visible");
    });

    // Populate existing values
    this.populateModalFields();

    // Auto-advance after 2.2 seconds
    if (this.splashTimer) clearTimeout(this.splashTimer);
    this.splashTimer = setTimeout(() => {
      this.transitionToStage2();
    }, 2200);
  }

  /**
   * Transition from Stage 1 Splash to Stage 2 Creation Form
   */
  transitionToStage2() {
    if (this.splashTimer) {
      clearTimeout(this.splashTimer);
      this.splashTimer = null;
    }
    this.isInSplashSequence = false;

    // Fade out Stage 1 Splash
    if (this.dom.splashScreenContainer) {
      this.dom.splashScreenContainer.classList.add("splash-fade-out");
      setTimeout(() => {
        if (this.dom.splashScreenContainer) {
          this.dom.splashScreenContainer.style.display = "none";
        }
      }, 500);
    }

    // Animate in Stage 2 Form Card
    if (this.dom.welcomeModalCard) {
      this.dom.welcomeModalCard.classList.remove("stage-hidden");
      this.dom.welcomeModalCard.classList.add("stage-active");
    }

    // Stagger in input groups with smooth cadence
    const groups = document.querySelectorAll("#welcome-modal .profile-input-group");
    groups.forEach((grp, idx) => {
      setTimeout(() => {
        grp.classList.add("stage-visible");
      }, 80 + idx * 100);
    });

    window.audioEngine.playChime(true);
  }

  /**
   * Open Welcome Modal directly (e.g. from HUD edit button)
   */
  openWelcomeModal(skipSplash = false) {
    if (!this.dom.welcomeModal) return;

    if (!skipSplash) {
      this.openWelcomeSequence();
      return;
    }

    this.isInSplashSequence = false;
    if (this.dom.splashScreenContainer) {
      this.dom.splashScreenContainer.style.display = "none";
    }

    this.populateModalFields();

    if (this.dom.welcomeModalCard) {
      this.dom.welcomeModalCard.classList.remove("stage-hidden");
      this.dom.welcomeModalCard.classList.add("stage-active");
    }

    document.querySelectorAll("#welcome-modal .profile-input-group").forEach(grp => {
      grp.classList.add("stage-visible");
    });

    this.dom.welcomeModal.classList.add("visible", "active");
    this.dom.welcomeModal.style.display = "flex";
    window.audioEngine.playClick();
  }

  populateModalFields() {
    if (this.dom.playerNameInput) {
      this.dom.playerNameInput.value = this.playerProfile.name || "Traveler";
    }

    document.querySelectorAll("#welcome-modal .gender-grid .radio-card").forEach(c => {
      c.classList.toggle("active", c.dataset.gender === this.playerProfile.gender);
    });

    document.querySelectorAll("#welcome-modal .age-grid .radio-card").forEach(c => {
      c.classList.toggle("active", c.dataset.ageGroup === this.playerProfile.age_group || c.dataset.age === String(this.playerProfile.age));
    });

    const standardOccs = ["mercenary", "scholar", "healer", "merchant", "scout", "adventurer"];
    const isCustomOcc = !standardOccs.includes(this.playerProfile.occupation);

    document.querySelectorAll("#welcome-modal .occupation-grid .radio-card").forEach(c => {
      if (isCustomOcc) {
        c.classList.toggle("active", c.dataset.occupation === "other");
      } else {
        c.classList.toggle("active", c.dataset.occupation === this.playerProfile.occupation);
      }
    });

    if (this.dom.occupationOtherWrapper) {
      this.dom.occupationOtherWrapper.classList.toggle("visible", isCustomOcc);
      if (isCustomOcc && this.dom.occupationOtherInput) {
        this.dom.occupationOtherInput.value = this.playerProfile.occupation;
      }
    }
  }

  closeWelcomeModal() {
    if (this.splashTimer) {
      clearTimeout(this.splashTimer);
      this.splashTimer = null;
    }
    this.isInSplashSequence = false;

    if (this.dom.welcomeModal) {
      this.dom.welcomeModal.classList.remove("visible", "active");
      this.dom.welcomeModal.style.display = "none";
    }
    setTimeout(() => {
      if (this.dom.playerInput) {
        this.dom.playerInput.focus();
      }
    }, 100);
  }

  saveProfileFromModal() {
    const rawName = this.dom.playerNameInput ? this.dom.playerNameInput.value.trim() : "Traveler";
    const name = rawName || "Traveler";

    const activeGenderCard = document.querySelector("#welcome-modal .gender-grid .radio-card.active");
    const gender = activeGenderCard ? activeGenderCard.dataset.gender : "male";

    const activeAgeCard = document.querySelector("#welcome-modal .age-grid .radio-card.active");
    const age = activeAgeCard ? parseInt(activeAgeCard.dataset.age, 10) : 24;
    const age_group = activeAgeCard ? activeAgeCard.dataset.ageGroup : "adult";

    const activeOccCard = document.querySelector("#welcome-modal .occupation-grid .radio-card.active");
    let occupation = activeOccCard ? activeOccCard.dataset.occupation : "mercenary";

    if (occupation === "other") {
      const customVal = this.dom.occupationOtherInput ? this.dom.occupationOtherInput.value.trim() : "";
      occupation = customVal || "Traveler";
    }

    this.playerProfile = { name, gender, age, age_group, occupation };

    try {
      localStorage.setItem("npc_talk_player_profile", JSON.stringify(this.playerProfile));
    } catch (e) {}

    // Send profile update to backend asynchronously
    fetch("/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        player_id: this.playerId,
        name: name,
        gender: gender,
        age: age,
        age_group: age_group,
        age_category: age_group,
        occupation: occupation
      })
    }).catch(() => {});

    this.updateProfileHUD();
    const npc = CONFIG.characters[this.currentNPCId];
    if (npc) {
      this.renderSuggestedChoices(npc.suggestedPrompts || []);
    }

    this.closeWelcomeModal();
    window.audioEngine.playChime(true);
  }

  updateProfileHUD() {
    if (this.dom.hudProfileName) {
      this.dom.hudProfileName.textContent = this.playerProfile.name || "Traveler";
    }
    if (this.dom.hudProfileTag) {
      const occIcons = {
        mercenary: "Mercenary",
        scholar: "Scholar",
        healer: "Herbalist",
        merchant: "Merchant",
        scout: "Scout",
        adventurer: "Adventurer"
      };
      this.dom.hudProfileTag.textContent = occIcons[this.playerProfile.occupation] || this.playerProfile.occupation;
    }
  }

  /**
   * Build the nearby-character roster from the same source of truth as the
   * dialogue engine. This keeps switching characters quick and game-like.
   */
  buildNPCRoster() {
    if (!this.dom.npcRoster) return;

    this.dom.npcRoster.innerHTML = "";
    Object.values(CONFIG.characters).forEach((npc, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "roster-character flex items-center gap-3 p-2 rounded-lg transition-all w-full text-left group cursor-pointer hover:bg-surface-variant/50 border border-transparent";
      button.dataset.npcId = npc.id;
      button.setAttribute("aria-label", `Speak with ${npc.name}, ${npc.title}`);
      button.setAttribute("aria-pressed", "false");

      const avatar = document.createElement("img");
      avatar.className = "w-10 h-10 rounded-full border border-outline-variant/50 group-hover:border-primary transition-colors object-cover object-top shrink-0";
      avatar.src = npc.portraits.neutral;
      avatar.alt = npc.name;
      avatar.loading = "lazy";

      const copy = document.createElement("div");
      copy.className = "flex-1 min-w-0";
      const name = document.createElement("div");
      name.className = "font-ui-label-lg text-sm text-on-surface group-hover:text-primary transition-colors truncate font-bold";
      name.textContent = npc.name;
      const title = document.createElement("div");
      title.className = "font-ui-label-sm text-xs text-on-surface-variant truncate";
      title.textContent = npc.title;
      copy.append(name, title);

      button.append(avatar, copy);
      button.addEventListener("click", () => {
        if (this.isWaitingResponse || npc.id === this.currentNPCId) return;
        this.loadNPC(npc.id);
        window.audioEngine.playClick();
      });
      this.dom.npcRoster.appendChild(button);
    });

    this.updateNPCRoster();
  }

  updateNPCRoster() {
    if (!this.dom.npcRoster) return;
    this.dom.npcRoster.querySelectorAll(".roster-character").forEach(button => {
      const isActive = button.dataset.npcId === this.currentNPCId;
      button.classList.toggle("active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
      const nameEl = button.querySelector(".font-ui-label-lg");
      const titleEl = button.querySelector(".font-ui-label-sm");
      if (nameEl) {
        nameEl.classList.toggle("text-primary", isActive);
        nameEl.classList.toggle("text-on-surface", !isActive);
      }
      if (titleEl) {
        titleEl.classList.toggle("text-ember-bright", isActive);
        titleEl.classList.toggle("text-on-surface-variant", !isActive);
      }
    });
  }

  /**
   * Load NPC Persona and Display Initial Greeting
   */
  loadNPC(npcId, isInitial = false) {
    const npc = CONFIG.characters[npcId] || CONFIG.characters.ash;
    this.currentNPCId = npc.id;
    this.currentEmotion = "neutral";

    // Set NPC Header info
    this.dom.npcNameTag.textContent = npc.name;
    this.dom.npcTitleTag.textContent = npc.title;
    this.dom.dialoguePanel.style.setProperty("--char-accent", npc.color);
    document.documentElement.style.setProperty("--char-accent", npc.color);
    this.updateNPCRoster();

    // Set stage classes
    this.dom.characterStage.className = "character-stage relative flex-1 h-[78vh] max-h-[760px] min-w-[240px] max-w-[460px] flex items-end justify-center z-10 select-none pointer-events-none self-end";

    // Auto-switch to NPC's preferred location (from npcDefaultLocations or defaultLocation)
    const preferredLoc =
      (CONFIG.npcDefaultLocations && CONFIG.npcDefaultLocations[npc.id])
      || npc.defaultLocation
      || this.gameState.location;

    if (preferredLoc && preferredLoc !== this.gameState.location) {
      this.gameState.location = preferredLoc;
    } else if (isInitial && npc.defaultLocation) {
      this.gameState.location = npc.defaultLocation;
    }

    // Set initial emotion portrait
    this.setEmotion("neutral", false);

    // Update background for new location (crossfade if not initial load)
    this.updateBackground(this.gameState.location, this.gameState.time_of_day, !isInitial);

    // Populate suggested prompt chips
    this.renderSuggestedChoices(npc.suggestedPrompts || []);

    // Present Greeting Line with Typewriter
    this.displayDialogue(npc.name, npc.greeting, "neutral");

    // Sync dropdowns
    if (this.dom.selectNpc) this.dom.selectNpc.value = npc.id;
    if (this.dom.selectEnv) this.dom.selectEnv.value = this.gameState.location;
    void this.syncStateToBackend({ location: this.gameState.location });
  }

  /**
   * Keep server-side dialogue context aligned with the visual state controls.
   * The UI remains usable in offline fallback mode if the API is unavailable.
   */
  async syncStateToBackend(updates) {
    const npcId = this.currentNPCId;
    const syncVersion = ++this.stateSyncVersion;
    try {
      const response = await fetch("/state", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_id: this.playerId,
          npc_id: npcId,
          ...updates
        })
      });
      if (!response.ok) return false;

      const payload = await response.json();
      if (
        payload.game_state &&
        this.currentNPCId === npcId &&
        this.stateSyncVersion === syncVersion
      ) {
        this.applyStateUpdates(payload.game_state);
      }
      return true;
    } catch (error) {
      console.info("FastAPI state sync unavailable; continuing in offline mode.");
      return false;
    }
  }

  /**
   * Smoothly Switch Character Emotion & Portrait
   */
  setEmotion(emotion = "neutral", animate = true) {
    const npc = CONFIG.characters[this.currentNPCId];
    if (!npc) return;

    this.currentEmotion = emotion;
    if (window.audioEngine && typeof window.audioEngine.setMood === "function") {
      window.audioEngine.setMood(emotion);
    }

    const emotionData = CONFIG.emotions[emotion] || CONFIG.emotions.neutral;
    const portraitPath = (npc.portraits[emotion] || npc.portraits.neutral) + "?v=9.0";

    // Update Mood Badge inside speech bubble
    if (this.dom.moodIcon)  this.dom.moodIcon.textContent  = emotionData.icon;
    if (this.dom.moodLabel) this.dom.moodLabel.textContent = emotionData.label;
    if (this.dom.moodBadge) {
      this.dom.moodBadge.style.color       = emotionData.color;
      this.dom.moodBadge.style.borderColor = emotionData.color;
    }

    // Update Emotion Overlay Badge on portrait corner (gacha style)
    if (this.dom.emotionOverlayIcon) {
      this.dom.emotionOverlayIcon.textContent = emotionData.icon;
    }
    if (this.dom.emotionOverlay) {
      // Pulse animation reset
      this.dom.emotionOverlay.style.setProperty("--emotion-glow",
        `rgba(${this._hexToRgb(emotionData.color)}, 0.55)`);
      this.dom.emotionOverlay.style.borderColor =
        emotionData.color || "rgba(255,215,0,0.7)";
      // Bounce animation
      this.dom.emotionOverlay.style.animation = "none";
      requestAnimationFrame(() => {
        if (this.dom.emotionOverlay) {
          this.dom.emotionOverlay.style.animation = "";
        }
      });
    }

    // Sync settings emotion dropdown if present
    if (this.dom.selectEmotion && this.dom.selectEmotion.value !== emotion) {
      this.dom.selectEmotion.value = emotion;
    }

    // Transition Portrait Image
    if (animate) {
      this.dom.characterPortrait.classList.add("portrait-transitioning");
      setTimeout(() => {
        this.dom.characterPortrait.src = portraitPath;
        this.dom.characterPortrait.alt = `${npc.name} (${emotion})`;
        this.dom.characterPortrait.classList.remove("portrait-transitioning");
      }, 180);
    } else {
      this.dom.characterPortrait.src = portraitPath;
      this.dom.characterPortrait.alt = `${npc.name} (${emotion})`;
    }
  }

  /**
   * Convert CSS hex color to "R, G, B" string for rgba()
   */
  _hexToRgb(hex) {
    if (!hex || !hex.startsWith("#")) return "255, 200, 60";
    const n = parseInt(hex.slice(1), 16);
    return `${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}`;
  }

  /**
   * Dynamic Background System with Dual-Layer CSS Crossfade
   */
  updateBackground(environment, timeOfDay, animate = true) {
    const envLookups = CONFIG.backgrounds[environment] || CONFIG.backgrounds.village_square;
    const bgUrl = envLookups[timeOfDay] || envLookups.day || "assets/backgrounds/village_square_day.svg";

    const targetLayer  = this.activeBgLayer === 1 ? this.dom.bgLayer2 : this.dom.bgLayer1;
    const currentLayer = this.activeBgLayer === 1 ? this.dom.bgLayer1 : this.dom.bgLayer2;

    targetLayer.style.backgroundImage = `url("${bgUrl}")`;

    if (animate) {
      targetLayer.classList.add("active");
      currentLayer.classList.remove("active");
      this.activeBgLayer = this.activeBgLayer === 1 ? 2 : 1;
    } else {
      currentLayer.style.backgroundImage = `url("${bgUrl}")`;
      currentLayer.classList.add("active");
      targetLayer.classList.remove("active");
    }

    // Apply atmospheric tint color overlay
    const tintColor = CONFIG.timeTints[timeOfDay] || CONFIG.timeTints.day;
    this.dom.bgTint.style.backgroundColor = tintColor;

    // Apply CSS filter overlay for time-of-day depth (warm/cool tones)
    if (CONFIG.timeTintFilters) {
      const filterStr = CONFIG.timeTintFilters[timeOfDay] || CONFIG.timeTintFilters.day || "none";
      this.dom.bgTint.style.filter = filterStr;
    }

    // Update particles (reduced density via engine) and ambient audio
    window.particleEngine.update(environment, timeOfDay);
    if (!window.audioEngine.muted) {
      window.audioEngine.setAtmosphere(environment, timeOfDay);
    }

    this.updateHUD();
  }

  /**
   * Typewriter Dialogue Presentation Engine
   */
  displayDialogue(speakerName, text, emotion = "neutral") {
    if (this.typewriterTimer) {
      clearTimeout(this.typewriterTimer);
      this.typewriterTimer = null;
    }

    this.targetFullText = text;
    this.currentDisplayedText = "";
    this.isTypewriting = true;
    this.dom.dialogueText.textContent = "";
    this.dom.advanceIndicator.classList.remove("visible");

    // Switch emotion smoothly
    this.setEmotion(emotion, true);

    // Record turn in history log
    const historyItem = {
      id: Date.now(),
      speaker: speakerName,
      text: text,
      emotion: emotion,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isPlayer: speakerName === "You" || speakerName === this.playerId
    };
    this.conversationHistory.push(historyItem);

    // High-speed smooth typewriter cadence (instant & responsive)
    let charIndex = 0;
    const textLength = this.targetFullText.length;
    const chunkSize = textLength > 160 ? 3 : (textLength > 60 ? 2 : 1);
    const baseDelay = 3;

    const typeNextChar = () => {
      if (!this.isTypewriting) return;
      if (charIndex < this.targetFullText.length) {
        const nextChunk = this.targetFullText.slice(charIndex, charIndex + chunkSize);
        this.currentDisplayedText += nextChunk;
        this.dom.dialogueText.textContent = this.currentDisplayedText;

        const lastChar = nextChunk[nextChunk.length - 1];
        if (charIndex % 6 === 0 && lastChar && lastChar.trim().length > 0) {
          window.audioEngine.playTypeBlip(lastChar);
        }

        charIndex += chunkSize;

        let delay = baseDelay;
        if ([',', ';', ':', '—', '-'].includes(lastChar)) {
          delay = 14;
        } else if (['.', '!', '?'].includes(lastChar)) {
          delay = 24;
        }

        this.typewriterTimer = setTimeout(typeNextChar, delay);
      } else {
        this.completeTypewriter();
      }
    };

    this.typewriterTimer = setTimeout(typeNextChar, 2);
  }

  /**
   * Instantly Finish Typewriter Reveal (Click-to-skip)
   */
  skipTypewriter() {
    if (!this.isTypewriting) return;
    if (this.typewriterTimer) {
      clearTimeout(this.typewriterTimer);
      this.typewriterTimer = null;
    }
    this.currentDisplayedText = this.targetFullText;
    this.dom.dialogueText.textContent = this.targetFullText;
    this.completeTypewriter();
  }

  completeTypewriter() {
    if (this.typewriterTimer) {
      clearTimeout(this.typewriterTimer);
      this.typewriterTimer = null;
    }
    this.isTypewriting = false;
    this.dom.advanceIndicator.classList.add("visible");
  }

  /**
   * Handle Player Sending a Message
   */
  async handlePlayerSendMessage() {
    const rawInput = this.dom.playerInput.value.trim();
    if (!rawInput || this.isWaitingResponse) return;
    const requestNpcId = this.currentNPCId;

    window.audioEngine.playClick();
    
    // Automatically clear player text box
    this.dom.playerInput.value = "";

    // Show player text in the dedicated bottom console preview
    if (this.dom.playerQueryText) {
      this.dom.playerQueryText.textContent = `"${rawInput}"`;
    }

    // Record player turn in history log (without overwriting NPC speech bubble)
    const historyItem = {
      id: Date.now(),
      speaker: (this.playerProfile && this.playerProfile.name) || "You",
      text: rawInput,
      emotion: "neutral",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isPlayer: true
    };
    this.conversationHistory.push(historyItem);

    // Show thinking bubble beside the character
    this.setWaitingState(true);

    try {
      // 1. Send to FastAPI backend /chat endpoint with a responsive 20-second timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 20000);

      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          player_id: this.playerId,
          npc_id: requestNpcId,
          message: rawInput,
          player_profile: this.playerProfile
        })
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        this.processBackendResponse(data, requestNpcId);
        this.setWaitingState(false);
        return;
      }
    } catch (err) {
      // Backend not running or timed out; immediately fall back to local engine
    }

    // 2. Fallback: Intelligent Client-Side NLP Engine (Instant 15ms)
    setTimeout(() => {
      const mockResp = this.generateMockResponse(requestNpcId, rawInput);
      this.processBackendResponse(mockResp, requestNpcId);
      this.setWaitingState(false);
    }, 15);
  }

  /**
   * Process Backend Response
   */
  processBackendResponse(data, npcId = this.currentNPCId) {
    const npc = CONFIG.characters[npcId] || CONFIG.characters.ash;
    
    // 1. Extract reply text (handles "reply" or "dialogue")
    const replyText = data.reply || data.dialogue || "...";

    // 2. Extract emotion (handles "emotion" or inferred from action / sentiment)
    let emotion = data.emotion;
    if (!emotion || emotion === "neutral") {
      if (data.action === "give_item" || data.action === "start_quest") emotion = "happy";
      else if (data.action === "hostile") emotion = "angry";
      else emotion = this.inferEmotionFromText(replyText, npcId);
    }

    // 3. Capture authoritative backend state, if returned.
    const stateUpdates = data.game_state || data.updated_state || null;

    // 4. Handle action triggers (e.g. quest started, reputation changed)
    if (data.action && data.action !== "none") {
      const hasAuthoritativeReputation =
        stateUpdates && typeof stateUpdates.reputation === "number";
      this.handleSpecialAction(
        data.action,
        data.action_params,
        hasAuthoritativeReputation
      );
    }

    if (stateUpdates) {
      this.applyStateUpdates(stateUpdates);
    }

    // 5. Present NPC reply immediately
    this.displayDialogue(npc.name, replyText, emotion);
  }

  /**
   * Apply State Updates & Refresh Visuals
   */
  applyStateUpdates(updates) {
    let bgChanged = false;

    if (updates.location && updates.location !== this.gameState.location) {
      this.gameState.location = updates.location;
      bgChanged = true;
    }
    if (updates.time_of_day && updates.time_of_day !== this.gameState.time_of_day) {
      this.gameState.time_of_day = updates.time_of_day;
      bgChanged = true;
    }
    if (typeof updates.reputation === "number") {
      this.gameState.reputation = updates.reputation;
      this.updateAffinityDisplay();
    }
    if (updates.quest_flags) {
      Object.assign(this.gameState.quest_flags, updates.quest_flags);
    }

    if (this.dom.selectEnv) this.dom.selectEnv.value = this.gameState.location;
    if (this.dom.selectTime) this.dom.selectTime.value = this.gameState.time_of_day;

    if (bgChanged) {
      this.updateBackground(this.gameState.location, this.gameState.time_of_day, true);
    }

    this.updateHUD();
  }

  /**
   * Handle Game Actions (e.g. start_quest, update_reputation)
   */
  handleSpecialAction(action, params = {}, hasAuthoritativeReputation = false) {
    if (action === "update_reputation") {
      const delta = params.change || params.delta || 1;
      if (!hasAuthoritativeReputation) {
        this.gameState.reputation += delta;
        this.updateAffinityDisplay();
      }
      window.audioEngine.playChime(delta > 0);
    } else if (action === "start_quest") {
      const questName = params.quest_name || "New Quest";
      this.gameState.quest_flags[questName] = true;
      window.audioEngine.playChime(true);
    }
  }

  /**
   * Intelligent Offline / Client-Side NLP Dialogue Engine
   * Understands questions, persona identity, relationships, world state,
   * actions, and delivers in-character busy responses when query is unknown.
   */
  generateMockResponse(npcId, playerText) {
    const lower = playerText.toLowerCase().trim();
    const words = lower.split(/\s+/);
    const npc = CONFIG.characters[npcId] || CONFIG.characters.ash;
    const time = this.gameState.time_of_day || "day";
    const rep = this.gameState.reputation || 0;
    const loc = this.gameState.location || "village_square";
    const pName = (this.playerProfile && this.playerProfile.name) || "Traveler";

    // 0. Humanity & Realness Defense (Anti-AI / Anti-Robot / Human Proof)
    const isHumanityChallenge = [
      /\b(are you|you are|you're|u r)\s+(an?\s+)?(ai|bot|robot|npc|language model|program|computer|machine|artificial intelligence|automaton|synthetic|fake|simulation|virtual entity|creature|monster)\b/i,
      /\b(are you|you are|you're|u r)\s+(real|human|a real human|a human|real person|a real person|alive|mortal)\b/i,
      /\b(you are not|you're not|you arent|you aren't|not a?)\s*(real|human|a human|a real human|living|mortal|real person)\b/i,
      /\b(not human|not a human|not real human|not real person|fake human|fake person|inhuman|non-human|non human)\b/i,
      /\b(scary not like human|not like (a )?human|dont look human|don't look human|not look human|look scary|look inhuman|look like a robot|look like a bot|look like a monster|look like an ai)\b/i,
      /\b(are you (an? )?ai|are you (an? )?robot|are you (a )?bot|are you (an? )?npc|is this an ai|are you real|are you human)\b/i,
      /\b(you are an ai|you are a bot|you are a robot|you're an ai|you're a bot|you're a robot)\b/i,
      /\b(prove (that )?you('re| are) human|proof you are human|are you alive|why do you look scary|why are you scary)\b/i
    ].some(pattern => pattern.test(lower));

    if (isHumanityChallenge) {
      const humanProofDialogues = {
        sam: [
          `Not human?! What kind of tavern madness has gotten into your head, ${pName}? Put your hand right on my chest and feel a real heart pumping, or take a look at the burns and calluses covering my palms! I've bled red blood in the border wars, broken ribs under falling siege engines, and I sweat over twelve-hundred-degree coals every single morning. If I were some clockwork statue or machine, my joints wouldn't ache every time a frost storm rolls through the valley! I am a living, breathing human soldier, and I've got the scars to prove every year of it!`,
          `You think I'm not human because of this steel prosthetic? I lost my hand in battle protecting real living people, ${pName}! Underneath this armor I have warm flesh, red blood, and a stubborn temper. Don't stand in my forge insulting my humanity unless you want a heavy hammer handed to you for bellows duty!`
        ],
        finn: [
          `What?! Are you out of your mind, ${pName}?! Look at these scraped knees, my messy hair, and tell me I'm not a real human! I was born right here on the village edge, I get starving hungry every two hours, and I've got a warm pulse right here on my wrist! Touch my arm if you don't believe me — it's warm flesh and blood! What on earth made you think I was some kind of fake machine?!`,
          `Not a real human? Hey! I run miles across the ridges every day until my lungs burn and my boots wear through the soles! I laugh, I get scared in the dark woods, and I bleed red blood whenever I scrape my shins on brambles. I'm sixteen years old and completely human, thank you very much!`
        ],
        eva: [
          `Not human? What a bizarre and feverish thing to say, ${pName}! I breathe the same crisp air you do, my feet throb after twelve hours tending mountain roots in the mud, and I must sleep every night or I collapse from exhaustion. I have cried for sick villagers, felt the warmth of morning sun on my skin, and bled when pruning thorn-bushes. I am flesh, blood, and mortal spirit through and through. Here, drink some lavender water — I suspect a forest delirium is confusing your senses.`,
          `If my demeanor seems quiet or strange to you, that does not make me any less of a living woman. I feel joy, sorrow, weariness, and hunger just like any person in Thornhaven. My pulse beats steady and warm, ${pName}. Rest your mind, for I am as human as you.`
        ],
        ash: [
          `Not human? Haha! That's the most ridiculous rumor anyone's tried to pin on me yet, ${pName}! If I were made of clockwork or magic spells, do you think I'd need to pay good silver for tavern roast mutton, dodge the village guard patrols in the mud, or catch headcolds in the winter rain? I've got real scars from alley daggers, a very human love for vintage wine, and red blood flowing through my veins. I'm a living mortal — just one with faster reflexes and sharper wits than most.`,
          `An artificial creation? Please. A machine wouldn't feel the thrill of a close escape or the sting of an empty coin pouch. Pinch my arm if you must, ${pName}, but I assure you, beneath this cloak is flesh, bone, and an appetite for survival.`
        ],
        tabitha: [
          `To look upon a living elder and question her humanity is a strange blindness, ${pName}. I have lived seventy-four winters within this valley. I have wept over the graves of kin, felt the bitter mountain chill ache in my aging joints, and watched generations of children take their first steps and grow gray. My blood is mortal red, my heart carries the burden of memory, and one day my mortal body will return to the earth of Thornhaven. I am as human as the stone and soil beneath our feet.`,
          `Look closely at my face — every wrinkle was etched by real human laughter, hardship, and sorrow over decades. Do not mistake deep wisdom or solemn duty for something artificial. I am a daughter of this valley, born of mortal flesh and blood, ${pName}.`
        ],
        pip: [
          `I'm NOT an AI or a robot, ${pName}!! Look at my knees, I got real scraped scabs from climbing the apple tree, and my tummy rumbles super loud whenever Mom makes stew! Pinch my cheeks if you don't believe me — it's real squishy human skin! Machines don't eat strawberry pies or lose their baby teeth, do they?! I'm eight years old and completely human!`,
          `A robot?! No way! I get sleepy after running around all day, my heart goes thump-thump-thump when I'm excited, and I bleed red blood whenever I trip over roots! If I was a robot I'd have laser eyes, and I definitely don't have laser eyes! I'm a real human kid, ${pName}!`
        ]
      };
      const lines = humanProofDialogues[npcId] || humanProofDialogues.sam;
      const text = lines[Math.floor(Math.random() * lines.length)];
      const emotion = (npcId === "sam" || npcId === "finn" || npcId === "pip") ? "angry" : (npcId === "eva" ? "surprised" : "suspicious");
      return {
        reply: text,
        emotion: emotion,
        action: "none",
        action_params: {},
        game_state: this.gameState
      };
    }

    // 1. Deep Semantic Narrative Corpus Matching (Lore, How-To, Why, Follow-Ups)
    const corpus = (CONFIG.narrativeCorpus && CONFIG.narrativeCorpus[npcId]) || [];
    let bestConcept = null;
    let bestConceptScore = 0;
    
    // Check if continuation / causal / procedural
    const isContinuation = ["what happened next", "what next", "and then", "tell me more", "elaborate", "continue", "what happened after"].some(p => lower.includes(p));
    const isCausal = ["why", "how come", "what caused", "what was the reason"].some(p => lower.startsWith(p)) || lower === "why?" || lower === "why" || lower === "why did you do that?";
    const isProcedural = ["how do i", "how to", "how do you", "can you teach me", "what are the steps", "how is it made"].some(p => lower.startsWith(p));

    if ((isContinuation || isCausal) && this.conversationHistory.length > 0) {
      for (const turn of [...this.conversationHistory].reverse()) {
        const tLower = turn.text.toLowerCase();
        for (const concept of corpus) {
          if (tLower.includes(concept.id.replace(/_/g, " ")) || concept.keywords.some(k => tLower.includes(k))) {
            bestConcept = concept;
            bestConceptScore = 10;
            break;
          }
        }
        if (bestConcept) break;
      }
    }

    if (!bestConcept) {
      for (const concept of corpus) {
        let score = 0;
        if (concept.title && lower.includes(concept.title.toLowerCase())) score += 15;
        for (const kw of concept.keywords) {
          if (kw.includes(" ") ? lower.includes(kw) : new RegExp("\\b" + kw + "\\b", "i").test(lower)) {
            score += kw.includes(" ") ? 4 : 2;
          }
        }
        if (score > bestConceptScore) {
          bestConceptScore = score;
          bestConcept = concept;
        }
      }
    }

    if (bestConcept && bestConceptScore >= 2) {
      let body = bestConcept.primary;
      let opener = "";
      if (isContinuation) {
        body = bestConcept.continuation || bestConcept.causal || bestConcept.primary;
        opener = `To continue with that story, ${pName} — `;
      } else if (isCausal) {
        body = bestConcept.causal || bestConcept.primary;
        opener = `The reason behind that goes back quite a ways, ${pName}. `;
      } else if (isProcedural) {
        body = bestConcept.procedural || bestConcept.primary;
        opener = `If you want to know how that is done properly, listen closely, ${pName}. `;
      } else {
        if (bestConcept.philosophical) body += " " + bestConcept.philosophical;
      }
      let fullText = opener + body;
      if (bestConcept.followup && !fullText.endsWith(bestConcept.followup)) {
        fullText += " " + bestConcept.followup;
      }
      return {
        reply: fullText,
        emotion: (npcId === "tabitha" || isCausal) ? "thinking" : "neutral",
        action: "none",
        action_params: {},
        game_state: this.gameState
      };
    }

    // 1. Questions about other characters (Relationship queries)
    const relationships = {
      ash: {
        sam: "Sam? Best blacksmith in the valley, though she has no patience for my kind of business. I buy rare metal ingots from her when I can.",
        finn: "The kid thinks he's being stealthy following me around. It's amusing, mostly.",
        eva: "Eva patches people up with zero questions asked. I respect that level of professionalism.",
        tabitha: "Tabitha sees right through every disguise. I keep my conversations with her brief and respectful."},
      finn: {
        sam: "Sam is the coolest person in Thornhaven! She let me pump the forge bellows once and sparks flew everywhere!",
        eva: "Eva is teaching me how to read herb names! And she always has sweet honey drops at her shop.",
        tabitha: "Tabitha is kind of scary because she knows everything before you even say it.",
        ash: "I'm pretty sure Ash is a secret master spy. I've been writing down all their movements in my notebook!"},
      eva: {
        sam: "Sam is a dear friend. She works tirelessly at the forge, and I make sure she has enough burn salves on hand.",
        finn: "Finn is a sweet, curious boy. He visits my shop often and I'm helping him learn to read.",
        tabitha: "Tabitha's knowledge of ancient botany and sacred groves is beyond measure.",
        ash: "Ash comes by for wound dressings occasionally. I ask no questions, and they pay honestly."},
      sam: {
        tabitha: "I owe Tabitha my life from the border wars. I would stand between her and an entire army without hesitation.",
        eva: "Eva's the only healer I trust with forge wounds. She doesn't lecture, she just heals.",
        finn: "The kid keeps sneaking into my forge. I act tough, but he's got good instincts for a youngster.",
        ash: "Ash is shady, but they manage to source rare ores that no one else can find."},
      tabitha: {
        sam: "Sam is a stalwart soul whose loyalty was forged in the fires of the border wars.",
        eva: "Eva brings gentle healing and quiet dignity to our village. Her herbs hold great restorative power.",
        finn: "Young Finn carries the spark of destiny, though he knows it not.",
        ash: "Ash walks in shadows, but even shadows have their place in the grand tapestry.",
        pip: "Little Pip is the innocent heart of our village. In his bright eyes, I see the future of Thornhaven unfolding peacefully."
      },
      pip: {
        finn: "Finn is my favorite scout! He shows me secret trails on the rooftops and lets me look at his maps!",
        sam: "Sam has a cool metal arm and lets me watch the orange sparks fly at the forge!",
        eva: "Eva gives me sweet honey drops and band-aids when I scrape my knees in the woods!",
        tabitha: "Elder Tabitha tells the best stories about fairies, dragons, and ancient stones!",
        ash: "Ash is super mysterious! They have a big hood and lots of shiny coins. I bet they have a treasure map!"
      }
    };

    const targetMap = {
      sam: ["sam", "blacksmith", "smith", "forge"],
      finn: ["finn", "scout", "boy", "kid"],
      eva: ["eva", "apothecary", "healer"],
      tabitha: ["tabitha", "elder", "lorekeeper", "sage"],
      ash: ["ash", "broker", "shadow", "rogue"],
      pip: ["pip", "little kid", "village kid"]
    };

    for (const [targetKey, aliases] of Object.entries(targetMap)) {
      if (targetKey === npcId) continue;
      const mentioned = aliases.some(a => new RegExp("\\b" + a + "\\b", "i").test(lower));
      if (mentioned && relationships[npcId]?.[targetKey]) {
        return {
          reply: relationships[npcId][targetKey],
          emotion: "neutral",
          action: "none",
          action_params: {},
          game_state: this.gameState
        };
      }
    }

    // 2. Cross-Character Domain Referral System (Recommending Experts)
    const expertDomains = {
      eva: {
        keywords: ["potion", "potions", "herb", "herbs", "heal", "healing", "salve", "salves", "medicine", "frostmoss", "fever", "antidote", "tincture", "botany", "remedy", "medicinal", "herbalism", "make a potion", "brew a potion", "cure"],
        replies: {
          sam: `If you're in need of medicinal remedies, healing salves, or rare mountain herbs, you should speak with Eva at the village apothecary. She knows ten times more about botanical brewing and potions than I do, ${pName}.`,
          finn: `Eva knows everything about wild mountain herbs and healing potions! She's teaching me how to identify ridge plants. You should definitely go visit her at the apothecary shop, ${pName}!`,
          tabitha: `Gentle Eva tends the apothecary with great care and devotion. If your body suffers from wound or ailment, go see her — her remedies hold deep restorative truth, ${pName}.`,
          ash: `Need stitches, burn salves, or a quiet remedy with no questions asked? Eva's your person, ${pName}. Her apothecary is right near the village garden.`}
      },
      sam: {
        keywords: ["blacksmith", "forge", "forging", "steel", "folded steel", "sword", "swords", "weapon", "weapons", "armor", "shield", "shields", "starmetal", "anvil", "whetstone", "craft a sword", "make a weapon", "temper steel", "blade", "repair armor"],
        replies: {
          eva: `If you need your weapons honed or sturdy armor forged, go see Sam at the village forge. Her folded steel has saved many lives, ${pName}.`,
          finn: `Sam is the best blacksmith ever! She crafts huge swords and shields that never break under pressure! Go visit her forge near the square, ${pName}!`,
          tabitha: `Sam's forge fires burn with steadfast courage. If you require a true blade or protective armor for your journey, speak with her at the anvil, ${pName}.`,
          ash: `Looking for folded steel, custom daggers, or rare armor? Sam is the only blacksmith in Thornhaven who won't sell you brittle junk. Her forge is by the square, ${pName}.`}
      },
      tabitha: {
        keywords: ["history", "lore", "cataclysm", "sundered crown", "keystone", "keystones", "ancient seal", "ancient records", "archives", "scrolls", "legends", "ancestors", "ancient war", "history of thornhaven", "who built thornhaven"],
        replies: {
          sam: `Ancient history and legends aren't my trade — you ought to speak with Tabitha, the Lorekeeper. She knows the history of every stone and battle in this valley, ${pName}.`,
          eva: `Elder Tabitha has chronicled the history of Thornhaven for over seventy winters. For sacred legends and the story of the ancient seal, speak with her, ${pName}.`,
          finn: `Elder Tabitha knows all the ancient stories about the cataclysm and the mountain keystones! She lives in the quiet sanctuary archives, ${pName}!`,
          ash: `Looking for forgotten lore or the real history behind the ancient seal? Tabitha knows things that aren't written in official kingdom books. Go find her, ${pName}.`}
      },
      finn: {
        keywords: ["scout", "scouting", "trails", "trail", "ridge", "paths", "path", "goblin camp", "goblin tracks", "shortcuts", "climbing", "secret path", "hidden trail", "scout trails", "forest tracks"],
        replies: {
          sam: `Young Finn spends all day running across the high ridges and knows every secret goat trail and lookout in the woods. Go find the kid if you need wilderness paths, ${pName}.`,
          eva: `Finn is an energetic explorer who knows the hidden mountain trails better than anyone. If you are scouting the ridge, ask him for directions, ${pName}.`,
          tabitha: `Young Finn knows the living pulse of the outer hills. Seek him out if you desire to navigate the winding trails of the Whispering Woods, ${pName}.`,
          ash: `Finn is always scampering around the rooftops and back-alleys. If you want to know about hidden shortcuts or outer goblin tracks, the kid's your guide, ${pName}.`}
      },
      ash: {
        keywords: ["secrets", "secret", "rumor", "rumors", "intel", "intelligence", "smuggler", "smuggling", "black market", "tunnels", "contraband", "underworld", "illegal", "stolen goods", "shadow network"],
        replies: {
          sam: `If you're hunting for underground rumors, rare contraband, or discreet information, Ash is usually lurking around the tavern cellar. Keep one hand on your purse though, ${pName}.`,
          eva: `Ash moves quietly through the shadows and hears things the ordinary townsfolk miss. If you seek discreet intelligence, look for them near the tavern, ${pName}.`,
          finn: `Ash knows all the secret rumors and smuggler tunnels! I've been watching them from the rooftops — you can usually spot them around the tavern alley, ${pName}!`,
          tabitha: `Ash operates in the unseen currents of our town. If it is hidden knowledge or quiet gossip you seek, they dwell near the tavern, ${pName}.`}
      }
    };

    for (const [expertKey, domainData] of Object.entries(expertDomains)) {
      if (expertKey === npcId) continue;
      if (domainData.keywords.some(kw => new RegExp("\\b" + kw + "\\b", "i").test(lower))) {
        const reply = domainData.replies[npcId];
        if (reply) {
          return {
            reply: reply,
            emotion: npcId === "tabitha" ? "thinking" : "neutral",
            action: "none",
            action_params: {},
            game_state: this.gameState
          };
        }
      }
    }

    // 3. Conversational Direct Queries, Dismissals & "Just tell me"
    if (["just tell me", "tell me what you know", "don't need you", "do not need you", "no i do not", "no i dont", "i don't need you", "i dont need you", "just answer", "just talk", "tell me"].some(q => lower.includes(q))) {
      const directReplies = {
        pip: "Aww, okay! You don't have to be grumpy, " + pName + "! I can just tell you what I found: I saw weird blue lights behind the old watermill, and Mr. Sam dropped a shiny brass gear near the well!",
        ash: "Straight to the point — I respect that, " + pName + ". What I know is simple: patrol guards are doubling shifts at the gate, and someone in high robes has been paying silver for old ruin maps.",
        finn: "Alright, scout briefing coming right up, " + pName + "! The eastern ridge trail is washed out by mud, and I spotted fresh goblin tracks near the old river crossing this morning!",
        sam: "Suit yourself, " + pName + ". I've got hot iron on the anvil anyway. Word from the border is supply caravans are delayed. If you need sturdy gear, buy what's in stock before prices climb.",
        eva: "Of course, " + pName + ". If you only seek news: the autumn frost is arriving early, and the mountain herbs are withering faster than usual. Take care when venturing outside the walls.",
        tabitha: "Very well, " + pName + ". Listen then: the ancient keystones are stirring under the mountain ridge. The shadows lengthen, and the old promises of Thornhaven are soon to be tested."
      };
      return {
        reply: directReplies[npcId] || `I hear you, ${pName}. What else do you wish to know?`,
        emotion: (npcId === "pip" || npcId === "sam") ? "neutral" : (npcId === "tabitha" ? "thinking" : "neutral"),
        action: "none",
        action_params: {},
        game_state: this.gameState
      };
    }

    // 4. Greetings
    if (["hello", "hi", "hey", "greetings", "good morning", "good evening", "how are you", "whats up"].some(g => lower.includes(g)) && words.length <= 6) {
      const greets = {
        ash: time === "night" ? "Late for a conversation tonight, friend. What brings you to my table?" : "Well now, look who it is. First question is on the house, friend. What do you need?",
        finn: time === "night" ? "Wait, you're still up? Are you on a secret night adventure tonight?" : "Hey! Did you see anything exciting outside the village gates today?",
        eva: time === "night" ? "Good evening. I keep late hours preparing medicines. Are you feeling unwell?" : "Welcome in, traveler. Take a breath and tell me what remedy you seek.",
        sam: time === "night" ? "It's late tonight. Even the forge fires cool eventually. Make it quick." : "*CLANG* State your business at my anvil, traveler.",
        tabitha: time === "night" ? "The night carries deep stillness tonight. Speak your mind, child." : "Peace upon your journey, child. What truth do you seek today?",
        pip: time === "night" ? "Nighttime is so spooky! Look at all the glow bugs! What are you doing out so late?" : "Ooh! Hello! Look at my shiny blue rock! Want to go treasure hunting with me?!"
      };
      return {
        reply: greets[npcId] || greets.ash,
        emotion: "neutral",
        action: "none",
        action_params: {},
        game_state: this.gameState
      };
    }

    // 3. Identity / Role questions
    if (["who are you", "what do you do", "tell me about yourself", "your name", "what are you"].some(q => lower.includes(q))) {
      const bios = {
        ash: "I'm Ash — information broker and acquisitions specialist in Thornhaven. If something happens here, I know about it.",
        finn: "I'm Finn! I'm nine and I explore every rooftop, secret path, and hidden cellar in Thornhaven!",
        eva: "I am Eva, the village apothecary. I brew herbal remedies, healing salves, and antidotes.",
        sam: "Sam. Master blacksmith of Thornhaven and veteran soldier. I forge folded steel that holds under pressure.",
        tabitha: "I am Tabitha, keeper of Thornhaven's ancient lore, historical records, and forgotten keystones.",
        pip: "I'm Pip! I'm eight and a half years old, and I find the best shiny treasures in Thornhaven!"
      };
      return {
        reply: bios[npcId] || `I am ${npc.name}, ${npc.title}.`,
        emotion: "neutral",
        action: "none",
        action_params: {},
        game_state: this.gameState
      };
    }

    // 4. Intent Scoring from CONFIG.npcIntents
    const intents = CONFIG.npcIntents[npcId] || CONFIG.npcIntents.ash || [];
    let bestIntent = null;
    let bestScore = 0;

    for (const intent of intents) {
      let score = 0;
      for (const trigger of intent.triggers) {
        const t = trigger.trim().toLowerCase();
        if (!t) continue;
        if (t.includes(" ")) {
          if (lower.includes(t)) {
            score += t.split(/\s+/).length * 2;
          }
        } else {
          const re = new RegExp("\\b" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "i");
          if (re.test(lower)) {
            score += 1;
          }
        }
      }
      if (score > bestScore) {
        bestScore = score;
        bestIntent = intent;
      }
    }

    if (bestIntent && bestScore >= 1) {
      const variants = bestIntent.responses || [];
      let resp = variants[Math.floor(Math.random() * variants.length)] || "...";
      let repDelta = bestIntent.repDelta || 0;
      if (repDelta) {
        this.gameState.reputation += repDelta;
        this.updateAffinityDisplay();
      }
      return {
        reply: resp,
        emotion: bestIntent.emotion || "neutral",
        action: bestIntent.action || "none",
        action_params: bestIntent.action_params || {},
        game_state: this.gameState
      };
    }

    // 5. In-character Busy / Dismissive responses for unknown messages
    const fallbacks = CONFIG.npcFallbacks[npcId] || CONFIG.npcFallbacks.ash || [
      "I'm in a bit of a rush right now, traveler. Let's speak when you have real business."
    ];
    let fallbackText = fallbacks[Math.floor(Math.random() * fallbacks.length)];
    if (time === "night" && !fallbackText.toLowerCase().includes("night") && !fallbackText.toLowerCase().includes("tonight")) {
      if (npcId === "tabitha") {
        fallbackText = `The night is deep tonight. ${fallbackText}`;
      }
    }

    return {
      reply: fallbackText,
      emotion: "neutral",
      action: "none",
      action_params: {},
      game_state: this.gameState
    };
  }

  inferEmotionFromText(text, npcId = "ash") {
    const lower = text.toLowerCase().trim();

    // 1. ANGRY (Fury, battle scowl, grumpiness, defense of humanity, insults)
    const angryWords = [
      "not human", "fool", "idiot", "get out", "leave my", "die", "kill", "shut up",
      "madness", "insult", "how dare", "fury", "rage", "scowl", "snarl", "clenched",
      "temper", "blood", "sword", "fight", "attack", "strike", "smash", "battle",
      "war", "insolent", "disrespect", "insolence", "dare you", "halt!", "scoundrel",
      "threat", "enemy", "punish", "liar", "cheat", "thief", "bellows duty",
      "bizarre and feverish", "questioning my humanity", "preposterous", "unscientific absurdity",
      "grumpy", "pout", "i'm not an ai", "what?! are you out of your mind"
    ];
    if (angryWords.some(w => lower.includes(w))) {
      return "angry";
    }

    // 2. SAD (Grief, weeping, tragedy, burial, loss, tears)
    const sadWords = [
      "alas", "grief", "wept", "cried", "tears", "mourn", "died", "passed away",
      "grave", "graves", "loss", "sad", "sorrow", "regret", "tragic", "heartbroken",
      "melancholy", "broken heart", "buried", "dead", "perished", "fell in battle",
      "mass graves", "crying", "sniffling", "bleeding out"
    ];
    if (sadWords.some(w => lower.includes(w))) {
      return "sad";
    }

    // 3. SURPRISED (Shock, astonishment, gasps, monster alerts, sudden realization)
    const surprisedWords = [
      "what?!", "wait?!", "wait!", "unbelievable", "astonishing", "shocking", "gasp",
      "beast", "monster", "dire wolf", "wolf", "wolves", "how is that possible",
      "heavens", "whoa", "impossible", "startled", "spotted", "sighting", "suddenly",
      "laser eyes", "seventeen centimeters", "breathing under the old well"
    ];
    if (surprisedWords.some(w => lower.includes(w)) || lower.startsWith("what?!") || lower.startsWith("wait,")) {
      return "surprised";
    }

    // 4. SUSPICIOUS (Secrets, whispers, rumors, skepticism, black market, calculating)
    const suspiciousWords = [
      "secret", "whisper", "whispers", "rumor", "rumors", "shadow", "shadows",
      "suspicious", "skeptical", "don't trust", "careful", "watch yourself",
      "who sent you", "shady", "underground", "black market", "discreet",
      "behind the scenes", "eyes and ears", "what's your game", "keep your purse",
      "provenance", "tread with discernment"
    ];
    if (suspiciousWords.some(w => lower.includes(w))) {
      return "suspicious";
    }

    // 5. THINKING (Pondering, research, alchemy, lore, history, formulas, why/how)
    const thinkingWords = [
      "ponder", "consider", "let me think", "perhaps", "formula", "recipe",
      "history", "ancient", "chronicle", "chronicles", "reason", "distill", "macerate",
      "calculate", "leylines", "leyline", "sacred", "centuries", "records", "keystone",
      "keystones", "phenomenon", "study", "cataclysm", "pre-cataclysm", "archives",
      "poison", "toxic", "disease", "illness", "symptoms"
    ];
    if (thinkingWords.some(w => lower.includes(w)) || npcId === "tabitha") {
      return "thinking";
    }

    // 6. HAPPY (Smiles, laughter, excitement, greetings, gratitude, joy)
    const happyWords = [
      "haha", "welcome", "glad", "delighted", "cheerful", "laugh", "smile", "joy",
      "thank you", "thanks", "great", "excellent", "pleased", "splendid", "wonderful",
      "friend", "cheers", "good morning", "bless", "excited", "yay", "ooh!", "yes!",
      "yes yes", "super bright", "coolest", "treasure", "shiny"
    ];
    if (happyWords.some(w => lower.includes(w)) || lower.startsWith("yes!") || lower.startsWith("ooh!") || lower.startsWith("hey!")) {
      return "happy";
    }

    return "neutral";
  }

  /**
   * Loading / Thinking State Visuals
   */
  setWaitingState(isWaiting) {
    this.isWaitingResponse = isWaiting;
    document.body.classList.toggle("is-waiting", isWaiting);
    this.dom.characterThinkingBubble.classList.toggle("visible", isWaiting);
    this.dom.sendBtn.disabled = isWaiting;
    this.dom.playerInput.disabled = isWaiting;
    [this.dom.selectNpc, this.dom.selectEnv, this.dom.selectTime, this.dom.selectRep]
      .filter(Boolean)
      .forEach(control => { control.disabled = isWaiting; });
    if (!isWaiting) {
      this.dom.playerInput.focus();
    }
  }

  /**
   * Render Suggested Choice Chips (NPC + Occupation Adaptive)
   */
  renderSuggestedChoices(prompts) {
    this.dom.choiceChipsContainer.innerHTML = "";
    
    // Combine base NPC prompts with occupation-specific questions
    const combined = [...prompts];
    if (CONFIG.occupationPrompts && this.playerProfile && this.playerProfile.occupation) {
      const occPrompts = CONFIG.occupationPrompts[this.playerProfile.occupation] || [];
      if (occPrompts.length > 0) {
        combined.push(occPrompts[0]);
        if (occPrompts.length > 1) combined.push(occPrompts[1]);
      }
    }

    const uniquePrompts = Array.from(new Set(combined)).slice(0, 4);

    uniquePrompts.forEach((prompt, index) => {
      const chip = document.createElement("button");
      chip.className = "choice-chip text-left w-full px-4 py-3 bg-surface/60 border border-outline-variant/40 rounded-lg font-body-narrative text-on-surface hover:bg-surface-variant hover:border-primary/50 hover:text-ember-bright transition-all duration-200 group flex items-center justify-between cursor-pointer shadow-sm";
      chip.type = "button";
      chip.title = `Press ${index + 1}: ${prompt}`;

      const textSpan = document.createElement("span");
      textSpan.className = "truncate pr-2 text-sm";
      textSpan.textContent = prompt;

      const iconSpan = document.createElement("span");
      iconSpan.className = "material-symbols-outlined text-outline group-hover:text-primary transition-colors text-[18px] shrink-0";
      iconSpan.textContent = "arrow_forward";

      chip.append(textSpan, iconSpan);
      chip.addEventListener("click", () => {
        this.dom.playerInput.value = prompt;
        this.handlePlayerSendMessage();
      });
      this.dom.choiceChipsContainer.appendChild(chip);
    });
  }

  /**
   * Update Affinity Trust Gauge Display
   */
  updateAffinityDisplay() {
    const rep = this.gameState.reputation;
    let label = "Neutral";
    let pct   = 50;
    let color = "#f59e0b";
    let barGradient = "linear-gradient(90deg, #f59e0b 0%, #10b981 100%)";

    if (rep >= 5) {
      label = "Trusted Ally";
      pct   = Math.min(100, 75 + (rep - 5) * 5);
      color = "#10b981";
      barGradient = "linear-gradient(90deg, #10b981 0%, #6ee7b7 100%)";
    } else if (rep >= 2) {
      label = "Friendly";
      pct   = 60 + rep * 4;
      color = "#38bdf8";
      barGradient = "linear-gradient(90deg, #0ea5e9 0%, #38bdf8 100%)";
    } else if (rep >= 0) {
      label = "Neutral";
      pct   = 50;
      color = "#f59e0b";
      barGradient = "linear-gradient(90deg, #f59e0b 0%, #10b981 100%)";
    } else if (rep >= -2) {
      label = "Guarded";
      pct   = Math.max(20, 35 + rep * 5);
      color = "#fb923c";
      barGradient = "linear-gradient(90deg, #f97316 0%, #fb923c 100%)";
    } else {
      label = "Hostile";
      pct   = Math.max(8, 20 + rep * 3);
      color = "#ef4444";
      barGradient = "linear-gradient(90deg, #b91c1c 0%, #ef4444 100%)";
    }

    this.gameState.reputation_label = label.toLowerCase();

    // Update resource pill bar (CoC style)
    if (this.dom.resRepFill) {
      this.dom.resRepFill.style.width      = `${pct}%`;
      this.dom.resRepFill.style.background = barGradient;
      this.dom.resRepFill.style.boxShadow  = `0 0 6px ${color}88`;
    }
    if (this.dom.resRepVal) {
      this.dom.resRepVal.textContent = `${label} (${rep >= 0 ? "+" : ""}${rep})`;
    }
    if (this.dom.hudRepCurrentNum) {
      this.dom.hudRepCurrentNum.textContent = (rep >= 0 ? "+" : "") + rep;
    }

    // Sync settings dropdown if open
    if (this.dom.selectRep && this.dom.selectRep.value !== String(rep)) {
      this.dom.selectRep.value = String(rep);
    }
  }

  /**
   * Update Top HUD: location badge + resource bars
   */
  updateHUD() {
    const locFormatted  = this.gameState.location.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    const timeFormatted = this.gameState.time_of_day.toUpperCase();

    if (this.dom.locationBadgeText) this.dom.locationBadgeText.textContent = locFormatted;
    if (this.dom.timeBadgeText)     this.dom.timeBadgeText.textContent     = timeFormatted;

    const timeIcons = {
      dawn: "wb_twilight",
      day: "light_mode",
      dusk: "bedtime",
      night: "nightlight"
    };
    const timeIconEl = document.getElementById("hud-time-icon");
    if (timeIconEl) {
      timeIconEl.textContent = timeIcons[this.gameState.time_of_day] || "light_mode";
    }

    // Quest progress bar
    const questFlags   = this.gameState.quest_flags || {};
    const totalQuests  = Object.keys(questFlags).length || 3;
    const doneQuests   = Object.values(questFlags).filter(Boolean).length;
    const questPct     = totalQuests > 0 ? (doneQuests / totalQuests) * 100 : 0;

    if (this.dom.resQuestFill) {
      this.dom.resQuestFill.style.width = `${Math.max(4, questPct)}%`;
    }
    if (this.dom.resQuestVal) {
      this.dom.resQuestVal.textContent = `${doneQuests} / ${totalQuests}`;
    }

    const questLabels = {
      explore_ancient_ruins: "Find a safe path into the ancient ruins",
      gather_frostmoss_herbs: "Gather frostmoss for Eva",
      investigate_strange_noises: "Investigate the night sounds beyond the wall"
    };
    const nextQuest = Object.keys(questFlags).find(key => !questFlags[key]);
    const allComplete = totalQuests > 0 && doneQuests === totalQuests;

    if (this.dom.questObjective) {
      this.dom.questObjective.textContent = allComplete
        ? "Return to Thornhaven and share what you learned"
        : (questLabels[nextQuest] || "Speak with the people of Thornhaven");
    }
    if (this.dom.questProgressText) {
      this.dom.questProgressText.textContent = allComplete
        ? "All leads discovered"
        : `${doneQuests} of ${totalQuests} leads discovered`;
    }
    if (this.dom.questTracker) {
      this.dom.questTracker.classList.toggle("complete", allComplete);
    }
  }

  /**
   * History Modal Controller
   */
  openHistoryModal() {
    this.renderHistoryList();
    this.dom.historyModal.classList.add("visible");
    window.audioEngine.playClick();
  }

  closeHistoryModal() {
    this.dom.historyModal.classList.remove("visible");
    window.audioEngine.playClick();
  }

  async clearHistory() {
    this.conversationHistory = [];
    this.renderHistoryList();
    window.audioEngine.playClick();

    const npcIds = Object.keys(CONFIG.characters);
    await Promise.all(npcIds.map(async (npcId) => {
      const query = new URLSearchParams({
        player_id: this.playerId,
        npc_id: npcId
      });
      try {
        await fetch(`/history?${query.toString()}`, { method: "DELETE" });
      } catch (error) {
        // Local history is still cleared when the optional backend is offline.
      }
    }));
  }

  renderHistoryList() {
    this.dom.historyList.innerHTML = "";
    if (this.conversationHistory.length === 0) {
      this.dom.historyList.innerHTML = `<div class="history-empty">No conversation history yet.</div>`;
      return;
    }

    this.conversationHistory.forEach(item => {
      const row = document.createElement("div");
      row.className = `history-row ${item.isPlayer ? "history-player" : "history-npc"}`;

      const header = document.createElement("div");
      header.className = "history-header";

      const speaker = document.createElement("span");
      speaker.className = "history-speaker";
      speaker.textContent = item.speaker;

      const timestamp = document.createElement("span");
      timestamp.className = "history-time";
      timestamp.textContent = item.timestamp;

      const body = document.createElement("div");
      body.className = "history-body";
      body.textContent = item.text;

      header.append(speaker, timestamp);
      row.append(header, body);

      this.dom.historyList.appendChild(row);
    });

    this.dom.historyList.scrollTop = this.dom.historyList.scrollHeight;
  }

  /**
   * Settings / Test HUD Drawer Controller
   */
  toggleSettingsDrawer(forceState) {
    const isOpen = this.dom.settingsDrawer.classList.contains("visible");
    const newState = forceState !== undefined ? forceState : !isOpen;

    this.dom.settingsDrawer.classList.toggle("visible", newState);
    window.audioEngine.playClick();
  }

  populateSettingsDropdowns() {
    // Populate NPC Selector
    this.dom.selectNpc.innerHTML = "";
    Object.values(CONFIG.characters).forEach(npc => {
      const opt = document.createElement("option");
      opt.value = npc.id;
      opt.textContent = `${npc.name} (${npc.title})`;
      this.dom.selectNpc.appendChild(opt);
    });
    this.dom.selectNpc.value = this.currentNPCId;

    // Populate Environment Selector
    this.dom.selectEnv.innerHTML = "";
    const envs = ["village_square", "forest", "tavern", "dungeon", "castle_ruins", "apothecary", "blacksmith_forge", "market_stalls"];
    envs.forEach(env => {
      const opt = document.createElement("option");
      opt.value = env;
      opt.textContent = env.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
      this.dom.selectEnv.appendChild(opt);
    });
    this.dom.selectEnv.value = this.gameState.location;

    // Set Time selector
    this.dom.selectTime.value = this.gameState.time_of_day;
  }
}

// Instantiate and start application on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  window.npcTalkApp = new NPCTalkApp();
  window.npcTalkApp.init();
});
