// ==========================================================================
// Sous-Chef Cinematic Apple Music "Now Playing" Web Companion
// FastMCP 1.30.0 Streamable HTTP • Amazon Echo Live Sync • PWA Ready
// ==========================================================================

// --------------------------------------------------------------------------
// 1. Web Audio API Lo-Fi Ambience & Kitchen Sound Engine
// --------------------------------------------------------------------------
class CookingMusicEngine {
  constructor() {
    this.ctx = null;
    this.isPlaying = false;
    this.wasPlayingBeforeTimer = false;
    this.gainNode = null;
    this.intervalId = null;
    this.masterVolume = 0.30;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.gainNode = this.ctx.createGain();
      this.gainNode.gain.setValueAtTime(this.masterVolume, this.ctx.currentTime);
      this.gainNode.connect(this.ctx.destination);
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  setVolume(val) {
    this.masterVolume = Math.max(0, Math.min(1, val));
    if (this.gainNode && this.ctx && this.isPlaying) {
      this.gainNode.gain.linearRampToValueAtTime(this.masterVolume, this.ctx.currentTime + 0.1);
    }
  }

  play() {
    this.init();
    if (this.isPlaying) return;
    this.isPlaying = true;

    if (this.gainNode && this.ctx) {
      this.gainNode.gain.cancelScheduledValues(this.ctx.currentTime);
      this.gainNode.gain.linearRampToValueAtTime(this.masterVolume, this.ctx.currentTime + 0.5);
    }

    // Warm Lo-Fi Rhodes progression (Fmaj7 -> Em7 -> Dm7 -> Cmaj7)
    const chords = [
      [174.61, 220.00, 261.63, 329.63],
      [164.81, 196.00, 246.94, 293.66],
      [146.83, 174.61, 220.00, 261.63],
      [130.81, 164.81, 196.00, 246.94]
    ];
    let chordIdx = 0;

    const playChord = () => {
      if (!this.isPlaying || !this.ctx) return;
      const notes = chords[chordIdx % chords.length];
      chordIdx++;
      const now = this.ctx.currentTime;

      notes.forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const noteGain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);

        noteGain.gain.setValueAtTime(0, now + idx * 0.08);
        noteGain.gain.linearRampToValueAtTime(0.042, now + idx * 0.08 + 0.16);
        noteGain.gain.exponentialRampToValueAtTime(0.0001, now + 3.7);

        osc.connect(noteGain);
        noteGain.connect(this.gainNode);
        osc.start(now + idx * 0.08);
        osc.stop(now + 3.8);
      });
    };

    playChord();
    this.intervalId = setInterval(playChord, 3800);
    this.updateUI();
  }

  stop(fadeTime = 0.4) {
    if (!this.isPlaying) return;
    this.isPlaying = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    if (this.gainNode && this.ctx) {
      const now = this.ctx.currentTime;
      this.gainNode.gain.cancelScheduledValues(now);
      this.gainNode.gain.linearRampToValueAtTime(0.0001, now + fadeTime);
    }
    this.updateUI();
  }

  duck(fadeTime = 0.3) {
    if (!this.isPlaying || !this.ctx) return;
    const now = this.ctx.currentTime;
    this.gainNode.gain.cancelScheduledValues(now);
    this.gainNode.gain.linearRampToValueAtTime(0.02, now + fadeTime);
  }

  unduck(fadeTime = 0.5) {
    if (!this.isPlaying || !this.ctx) return;
    const now = this.ctx.currentTime;
    this.gainNode.gain.cancelScheduledValues(now);
    this.gainNode.gain.linearRampToValueAtTime(this.masterVolume, now + fadeTime);
  }

  playTimerChime() {
    this.init();
    if (!this.ctx) return;
    const tones = [880, 1174.66, 1760];
    const now = this.ctx.currentTime;
    tones.forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now + i * 0.18);
      gain.gain.setValueAtTime(0, now + i * 0.18);
      gain.gain.linearRampToValueAtTime(0.2, now + i * 0.18 + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.18 + 1.2);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now + i * 0.18);
      osc.stop(now + i * 0.18 + 1.25);
    });
  }

  playCheckChime() {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const now = this.ctx.currentTime;
    osc.type = 'sine';
    osc.frequency.setValueAtTime(659.25, now);
    osc.frequency.exponentialRampToValueAtTime(1318.51, now + 0.08);
    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.24);
  }

  updateUI() {
    const musicBtn = document.getElementById('music-btn');
    if (musicBtn) {
      if (this.isPlaying) {
        musicBtn.classList.add('playing');
        musicBtn.style.color = '#30d158';
      } else {
        musicBtn.classList.remove('playing');
        musicBtn.style.color = 'inherit';
      }
    }
  }
}

// --------------------------------------------------------------------------
// 2. Main Sous-Chef Application Architecture
// --------------------------------------------------------------------------
class SousChefVoiceApp {
  constructor() {
    // Mode Switcher Elements
    this.modeCookingBtn = document.getElementById('mode-cooking-btn');
    this.modeStorageBtn = document.getElementById('mode-storage-btn');
    this.viewNowCooking = document.getElementById('view-now-cooking');
    this.viewStorage = document.getElementById('view-storage');

    // Ambient Backdrop
    this.ambientBackdrop = document.getElementById('ambient-backdrop');

    // Hero Column (Left)
    this.dishName = document.getElementById('dish-name');
    this.dishSub = document.getElementById('dish-sub');
    this.dishArtworkEmoji = document.getElementById('dish-artwork-emoji');
    this.dishCoverArtwork = document.getElementById('dish-cover-artwork');
    this.starRecipeBtn = document.getElementById('star-recipe-btn');
    this.customRecipeOpenBtn = document.getElementById('custom-recipe-open-btn');
    this.scrubberFill = document.getElementById('scrubber-fill');
    this.scrubElapsed = document.getElementById('scrub-elapsed');
    this.scrubRemaining = document.getElementById('scrub-remaining');
    this.prevStepBtn = document.getElementById('prev-step-btn');
    this.timerToggleBtn = document.getElementById('timer-toggle-btn');
    this.nextStepBtn = document.getElementById('next-step-btn');
    this.finishMealBtn = document.getElementById('finish-meal-btn');

    // Lyrics Column (Right)
    this.streamStatusLabel = document.getElementById('stream-status-label');
    this.tabShowSteps = document.getElementById('tab-show-steps');
    this.tabShowPrep = document.getElementById('tab-show-prep');
    this.prepReadyCount = document.getElementById('prep-ready-count');
    this.lyricsViewport = document.getElementById('lyrics-viewport');
    this.prepChecklistViewport = document.getElementById('prep-checklist-viewport');

    // Kitchen Storage View
    this.storageTotalNum = document.getElementById('storage-total-num');
    this.barFridge = document.getElementById('bar-fridge');
    this.barPantry = document.getElementById('bar-pantry');
    this.barFreezer = document.getElementById('bar-freezer');
    this.countFridge = document.getElementById('count-fridge');
    this.countPantry = document.getElementById('count-pantry');
    this.countFreezer = document.getElementById('count-freezer');
    this.countExpiring = document.getElementById('count-expiring');
    this.inventorySearchInput = document.getElementById('inventory-search-input');
    this.searchClearBtn = document.getElementById('search-clear-btn');
    this.storageItemsGrid = document.getElementById('storage-items-grid');

    // Floating Dock Bar & Voice Activity Pill
    this.voiceActivityPill = document.getElementById('voice-activity-pill');
    this.activeVoicePhrase = document.getElementById('active-voice-phrase');
    this.toggleChatDrawerBtn = document.getElementById('toggle-chat-drawer-btn');
    this.toggleMacroDrawerBtn = document.getElementById('toggle-macro-drawer-btn');
    this.toggleRecipesDrawerBtn = document.getElementById('toggle-recipes-drawer-btn');

    // Drawers
    this.chatSlideDrawer = document.getElementById('chat-slide-drawer');
    this.closeChatDrawerBtn = document.getElementById('close-chat-drawer-btn');
    this.drawerTranscriptBox = document.getElementById('drawer-transcript-box');
    this.drawerChatForm = document.getElementById('drawer-chat-form');
    this.drawerTextInput = document.getElementById('drawer-text-input');
    this.drawerMicBtn = document.getElementById('drawer-mic-btn');

    this.macroSlideDrawer = document.getElementById('macro-slide-drawer');
    this.closeMacroDrawerBtn = document.getElementById('close-macro-drawer-btn');
    this.ringKcal = document.getElementById('ring-kcal');
    this.ringProt = document.getElementById('ring-prot');
    this.todayKcal = document.getElementById('today-kcal');
    this.todayProtein = document.getElementById('today-protein');

    this.recipesSlideDrawer = document.getElementById('recipes-slide-drawer');
    this.closeRecipesDrawerBtn = document.getElementById('close-recipes-drawer-btn');
    this.drawerRecipesList = document.getElementById('drawer-recipes-list');

    // Emergency Rescue Sheet
    this.emergencyAlertSheet = document.getElementById('emergency-alert-sheet');
    this.alertRemedyTitle = document.getElementById('alert-remedy-title');
    this.alertRemedySubtitle = document.getElementById('alert-remedy-subtitle');
    this.alertRemedyBody = document.getElementById('alert-remedy-body');
    this.alertRemedyConfirmBtn = document.getElementById('alert-remedy-confirm-btn');

    // Music & Ambience Controls
    this.musicBtn = document.getElementById('music-btn');
    this.musicVol = document.getElementById('music-vol');

    // State Variables
    this.currentMode = 'cooking';
    this.lyricsMode = 'steps'; // 'steps' | 'prep'
    this.isListening = false;
    this.isSpeaking = false;
    this.recognition = null;
    this.selectedFemaleVoice = null;
    this.activeCooking = null;
    this.inventoryItems = [];
    this.activeFilter = 'all';
    this.searchQuery = '';
    this.allRecipes = [];

    // Step Timer State
    this.stepTimerTotal = 0;
    this.stepTimerRemaining = 0;
    this.stepTimerElapsed = 0;
    this.stepTimerInterval = null;
    this.isTimerRunning = false;

    // Lo-Fi Audio Engine
    this.musicEngine = new CookingMusicEngine();

    // Bootstrap
    this.initVoices();
    this.initSpeechRecognition();
    this.initEventListeners();
    this.initPWA();

    // Initial Data Fetch
    this.fetchCookingState();
    this.fetchInventory();
    this.fetchNutrition();
    this.fetchRecipes();

    // Periodic Live Sync with Echo Dot / Alexa+
    setInterval(() => {
      this.fetchCookingState();
      this.fetchInventory();
      this.fetchNutrition();
    }, 3000);
  }

  // ------------------------------------------------------------------------
  // PWA Service Worker Registration
  // ------------------------------------------------------------------------
  initPWA() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(err => {
        console.warn('PWA ServiceWorker registration failed:', err);
      });
    }
  }

  // ------------------------------------------------------------------------
  // Natural Voice Selection
  // ------------------------------------------------------------------------
  initVoices() {
    if (!('speechSynthesis' in window)) return;
    const findVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      if (!voices || voices.length === 0) return;
      const preferred = ["Samantha", "Victoria", "Google US English", "Karen", "Zira", "Moira"];
      for (const name of preferred) {
        const found = voices.find(v => v.name.includes(name) || (v.lang.startsWith('en') && v.name.toLowerCase().includes('female')));
        if (found) {
          this.selectedFemaleVoice = found;
          break;
        }
      }
      if (!this.selectedFemaleVoice) {
        this.selectedFemaleVoice = voices.find(v => v.lang.startsWith('en'));
      }
    };
    findVoice();
    window.speechSynthesis.onvoiceschanged = findVoice;
  }

  // ------------------------------------------------------------------------
  // Web Speech API
  // ------------------------------------------------------------------------
  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        this.voiceActivityPill.classList.add('listening');
        this.drawerMicBtn.classList.add('active');
        this.activeVoicePhrase.textContent = 'Listening to your kitchen command...';
        this.musicEngine.duck(0.2);
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.activeVoicePhrase.textContent = `Heard: "${transcript}"`;
        this.handleUserUtterance(transcript);
      };

      this.recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        this.stopListening();
      };

      this.recognition.onend = () => {
        this.stopListening();
      };
    }
  }

  toggleListening() {
    if (!this.recognition) {
      this.openChatDrawer();
      this.appendTranscript('assistant', 'Microphone not supported on this device. Type your kitchen request here!');
      return;
    }
    if (this.isListening) {
      this.recognition.stop();
    } else {
      try {
        this.recognition.start();
      } catch (err) {
        console.error(err);
      }
    }
  }

  stopListening() {
    this.isListening = false;
    this.voiceActivityPill.classList.remove('listening');
    this.drawerMicBtn.classList.remove('active');
    this.musicEngine.unduck(0.3);
    setTimeout(() => {
      if (!this.isSpeaking) {
        this.activeVoicePhrase.innerHTML = 'Synced with Amazon Echo &bull; Speak to cook';
      }
    }, 2500);
  }

  speak(text, onComplete = null) {
    if (!('speechSynthesis' in window)) {
      if (onComplete) onComplete();
      return;
    }
    window.speechSynthesis.cancel();

    this.isSpeaking = true;
    this.voiceActivityPill.classList.add('listening');
    this.activeVoicePhrase.textContent = `Sous-Chef: "${text.slice(0, 60)}${text.length > 60 ? '...' : ''}"`;
    this.musicEngine.duck(0.2);

    const utterance = new SpeechSynthesisUtterance(text);
    if (this.selectedFemaleVoice) {
      utterance.voice = this.selectedFemaleVoice;
    }
    utterance.rate = 1.04;
    utterance.pitch = 1.02;

    const cleanup = () => {
      this.isSpeaking = false;
      this.voiceActivityPill.classList.remove('listening');
      this.musicEngine.unduck(0.4);
      this.activeVoicePhrase.innerHTML = 'Synced with Amazon Echo &bull; Speak to cook';
      if (onComplete) onComplete();
    };

    utterance.onend = cleanup;
    utterance.onerror = cleanup;
    window.speechSynthesis.speak(utterance);
  }

  appendTranscript(role, text) {
    const entry = document.createElement('div');
    entry.className = `transcript-entry ${role}`;
    entry.innerHTML = `
      <span class="entry-author">${role === 'user' ? 'You' : 'Sous-Chef'}</span>
      <p>${escapeHtml(text)}</p>
    `;
    this.drawerTranscriptBox.appendChild(entry);
    this.drawerTranscriptBox.scrollTop = this.drawerTranscriptBox.scrollHeight;
  }

  // ------------------------------------------------------------------------
  // Conversational API Dispatcher
  // ------------------------------------------------------------------------
  async handleUserUtterance(text) {
    if (!text || !text.trim()) return;
    const utterance = text.trim();
    this.appendTranscript('user', utterance);

    try {
      const response = await fetch('/api/converse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ utterance })
      });

      if (!response.ok) {
        throw new Error(`Server HTTP ${response.status}`);
      }

      const data = await response.json();
      const reply = data.spoken_message || data.message || "I've updated your kitchen.";

      // Music commands
      if (data.music_command === 'play') this.musicEngine.play();
      else if (data.music_command === 'stop') this.musicEngine.stop();

      // Timer commands
      if (data.timer_command === 'start') this.startStepTimer();
      else if (data.timer_command === 'stop') this.pauseStepTimer();

      // Active cooking state update
      if (data.active_cooking !== undefined) {
        this.activeCooking = data.active_cooking;
        this.renderCookingStage();
        this.switchMode('cooking');
      }

      // Culinary rescue remedy
      if (data.remedy) {
        this.showEmergencyRescue(data.remedy);
      } else {
        this.appendTranscript('assistant', reply);
      }

      this.speak(reply);

      // Refresh data
      await this.fetchInventory();
      await this.fetchNutrition();

    } catch (err) {
      console.error(err);
      const fallback = "Sorry, I had trouble reaching the kitchen server.";
      this.appendTranscript('assistant', fallback);
      this.speak(fallback);
    }
  }

  showEmergencyRescue(remedy) {
    this.alertRemedyTitle.textContent = `Rescue: ${remedy.category || 'Culinary Fix'}`;
    this.alertRemedySubtitle.textContent = remedy.quip || "Stay calm, we can fix this!";
    
    const stepsHtml = (remedy.remedy_steps || [])
      .map((s, i) => `<p style="margin: 6px 0;"><strong>${i + 1}.</strong> ${escapeHtml(s)}</p>`)
      .join('');

    this.alertRemedyBody.innerHTML = `
      <div style="margin-bottom: 12px;">${stepsHtml}</div>
      ${remedy.pro_tip ? `<div style="font-size: 0.85rem; color: #ff9f0a; margin-top: 10px;"><strong>💡 Pro Tip:</strong> ${escapeHtml(remedy.pro_tip)}</div>` : ''}
    `;

    this.emergencyAlertSheet.classList.remove('hidden');
    this.appendTranscript('assistant', `Culinary Rescue for ${remedy.category}: ${remedy.quip}`);
  }

  // ------------------------------------------------------------------------
  // View Switcher (Cooking <-> Storage)
  // ------------------------------------------------------------------------
  switchMode(mode) {
    this.currentMode = mode;
    if (mode === 'cooking') {
      this.modeCookingBtn.classList.add('active');
      this.modeStorageBtn.classList.remove('active');
      this.viewNowCooking.classList.remove('hidden');
      this.viewStorage.classList.add('hidden');
    } else {
      this.modeStorageBtn.classList.add('active');
      this.modeCookingBtn.classList.remove('active');
      this.viewStorage.classList.remove('hidden');
      this.viewNowCooking.classList.add('hidden');
    }
  }

  // ------------------------------------------------------------------------
  // Guided Cooking Station & Apple Music Synchronized Lyrics
  // ------------------------------------------------------------------------
  async fetchCookingState() {
    try {
      const res = await fetch('/api/cooking');
      if (res.ok) {
        const data = await res.json();
        const incomingStr = JSON.stringify(data.active_cooking || null);
        const currentStr = JSON.stringify(this.activeCooking || null);
        if (incomingStr !== currentStr) {
          this.activeCooking = data.active_cooking;
          this.renderCookingStage();
        }
      }
    } catch (err) {
      console.warn('Could not fetch cooking state:', err);
    }
  }

  renderCookingStage() {
    if (!this.activeCooking || !this.activeCooking.recipe) {
      // Default placeholder view
      this.dishName.textContent = "Spinach & Cheddar Scramble";
      this.dishSub.textContent = "10 min · 2 servings · ~320 kcal";
      this.dishArtworkEmoji.textContent = "🍳";
      this.streamStatusLabel.textContent = "READY TO COOK";
      this.lyricsViewport.innerHTML = `
        <div class="lyric-line active" data-step-index="0">
          <div class="lyric-badge">Welcome</div>
          <div class="lyric-text">Say "Alexa, ask Sous-Chef what can I cook" or pick a recipe below to begin!</div>
        </div>
      `;
      this.resetStepTimer();
      return;
    }

    const { recipe, step, checked_prep, servings } = this.activeCooking;
    const currentServings = servings || recipe.servings || 2;
    const multiplier = currentServings / (recipe.servings || 2);
    const steps = recipe.steps || [];
    const totalSteps = steps.length || 1;
    const activeStepIdx = Math.max(1, Math.min(step || 1, totalSteps));
    const activeStepObj = steps[activeStepIdx - 1] || {};

    // 1. Hero Left Column
    this.dishName.textContent = recipe.name;
    this.dishSub.textContent = `${recipe.prep_minutes || 15} min · ${currentServings} servings · ~${Math.round((recipe.kcal_per_serving || 320) * multiplier)} kcal`;
    this.dishArtworkEmoji.textContent = this.getItemEmoji(recipe.name);

    // Update active scale chip
    document.querySelectorAll('.scale-chip').forEach(chip => {
      const s = parseFloat(chip.dataset.scale);
      chip.classList.toggle('active', Math.abs(s - currentServings) < 0.1);
    });

    // 2. Lyrics Viewport (Apple Music Synchronized Stream)
    this.streamStatusLabel.textContent = `STEP ${activeStepIdx} OF ${totalSteps}`;
    this.lyricsViewport.innerHTML = '';

    steps.forEach((st, idx) => {
      const stepNum = idx + 1;
      const isCurrent = stepNum === activeStepIdx;
      const isPast = stepNum < activeStepIdx;

      const line = document.createElement('div');
      line.className = `lyric-line ${isCurrent ? 'active' : (isPast ? 'past' : 'future')}`;
      line.dataset.stepIndex = idx;

      const timerTag = st.timer_seconds && st.timer_seconds > 0 
        ? `<div class="lyric-timer-tag">⏱️ ${Math.round(st.timer_seconds / 60)} min</div>` 
        : '';
      const tipBox = st.tip 
        ? `<div class="lyric-tip">💡 ${escapeHtml(st.tip)}</div>` 
        : '';

      line.innerHTML = `
        <div class="lyric-badge">Step ${stepNum}</div>
        <div class="lyric-text">${escapeHtml(st.instruction || '')}</div>
        ${tipBox}
        ${timerTag}
      `;

      // Clicking any lyric line jumps directly to that step!
      line.addEventListener('click', () => {
        this.setCookingStep(stepNum);
      });

      this.lyricsViewport.appendChild(line);
    });

    // Auto-scroll the active lyric line to center of view
    requestAnimationFrame(() => {
      const activeElement = this.lyricsViewport.querySelector('.lyric-line.active');
      if (activeElement) {
        activeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });

    // 3. Prep Checklist Viewport
    this.prepChecklistViewport.innerHTML = '';
    const ingredients = recipe.ingredients || [];
    let checkedCount = 0;

    ingredients.forEach(ing => {
      const isChecked = (checked_prep || []).includes(ing.item);
      if (isChecked) checkedCount++;

      const scaledQty = (ing.qty || 1) * multiplier;
      const row = document.createElement('div');
      row.className = `prep-item-row ${isChecked ? 'checked' : ''}`;
      row.innerHTML = `
        <div class="prep-checkbox">${isChecked ? '✓' : ''}</div>
        <div class="prep-item-title">${escapeHtml(ing.item)}</div>
        <div class="item-qty-badge">${formatDisplayQty(scaledQty, ing.unit)}</div>
      `;

      row.addEventListener('click', async () => {
        this.musicEngine.playCheckChime();
        await fetch('/api/cooking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'check_prep', item: ing.item })
        });
        await this.fetchCookingState();
      });

      this.prepChecklistViewport.appendChild(row);
    });

    this.prepReadyCount.textContent = `${checkedCount}/${ingredients.length}`;

    // 4. Timer Setup for current step
    if (activeStepObj.timer_seconds && activeStepObj.timer_seconds > 0) {
      if (this.stepTimerTotal !== activeStepObj.timer_seconds) {
        this.stepTimerTotal = activeStepObj.timer_seconds;
        this.stepTimerRemaining = activeStepObj.timer_seconds;
        this.stepTimerElapsed = 0;
        this.updateScrubberDisplay();
      }
    } else {
      this.stepTimerTotal = 0;
      this.stepTimerRemaining = 0;
      this.stepTimerElapsed = 0;
      this.pauseStepTimer();
      this.updateScrubberDisplay();
    }
  }

  async setCookingStep(stepNum) {
    this.musicEngine.playCheckChime();
    this.pauseStepTimer();
    try {
      const res = await fetch('/api/cooking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'set_step', step: stepNum })
      });
      if (res.ok) {
        const data = await res.json();
        this.activeCooking = data.active_cooking;
        this.renderCookingStage();
      }
    } catch (err) {
      console.error(err);
    }
  }

  // ------------------------------------------------------------------------
  // Apple-Style Progress Scrubber & Timer
  // ------------------------------------------------------------------------
  startStepTimer() {
    if (this.isTimerRunning) return;
    this.isTimerRunning = true;
    this.updateTransportPlayState(true);

    this.musicEngine.wasPlayingBeforeTimer = this.musicEngine.isPlaying;
    if (!this.musicEngine.isPlaying) {
      this.musicEngine.play();
    }

    this.stepTimerInterval = setInterval(() => {
      if (this.stepTimerRemaining > 0) {
        this.stepTimerRemaining--;
        this.stepTimerElapsed++;
        this.updateScrubberDisplay();
      } else {
        this.handleTimerFinished();
      }
    }, 1000);
  }

  pauseStepTimer() {
    this.isTimerRunning = false;
    this.updateTransportPlayState(false);
    if (this.stepTimerInterval) {
      clearInterval(this.stepTimerInterval);
      this.stepTimerInterval = null;
    }
  }

  resetStepTimer() {
    this.pauseStepTimer();
    this.stepTimerRemaining = this.stepTimerTotal;
    this.stepTimerElapsed = 0;
    this.updateScrubberDisplay();
  }

  updateTransportPlayState(isPlaying) {
    const playIcon = this.timerToggleBtn.querySelector('.play-icon');
    const pauseIcon = this.timerToggleBtn.querySelector('.pause-icon');
    if (isPlaying) {
      playIcon.classList.add('hidden');
      pauseIcon.classList.remove('hidden');
    } else {
      playIcon.classList.remove('hidden');
      pauseIcon.classList.add('hidden');
    }
  }

  updateScrubberDisplay() {
    const elapsedMins = Math.floor(this.stepTimerElapsed / 60);
    const elapsedSecs = this.stepTimerElapsed % 60;
    this.scrubElapsed.textContent = `${String(elapsedMins).padStart(2, '0')}:${String(elapsedSecs).padStart(2, '0')}`;

    const remMins = Math.floor(this.stepTimerRemaining / 60);
    const remSecs = this.stepTimerRemaining % 60;
    this.scrubRemaining.textContent = `-${String(remMins).padStart(2, '0')}:${String(remSecs).padStart(2, '0')}`;

    const pct = this.stepTimerTotal > 0 ? (this.stepTimerElapsed / this.stepTimerTotal) * 100 : 0;
    this.scrubberFill.style.width = `${Math.min(100, Math.max(0, pct))}%`;
  }

  handleTimerFinished() {
    this.pauseStepTimer();
    this.musicEngine.stop(0.2);
    this.musicEngine.playTimerChime();

    let alertMsg = "Timer's up! Turn down the heat and check your food.";
    if (this.activeCooking && this.activeCooking.recipe) {
      const steps = this.activeCooking.recipe.steps || [];
      const curr = steps[this.activeCooking.step - 1];
      if (curr && curr.timer_alert) {
        alertMsg = curr.timer_alert;
      }
    }

    this.showEmergencyRescue({
      category: "Timer Finished",
      quip: "Ding! Kitchen timer completed.",
      remedy_steps: [alertMsg, "Check consistency and stir gently."],
      pro_tip: "Letting food rest off the heat retains moisture."
    });

    this.speak(alertMsg);
  }

  // ------------------------------------------------------------------------
  // Kitchen Storage & Grocery View
  // ------------------------------------------------------------------------
  async fetchInventory() {
    try {
      const res = await fetch('/api/inventory');
      if (res.ok) {
        const data = await res.json();
        this.inventoryItems = data.items || [];
        this.renderStorageGrid();
      }
    } catch (err) {
      console.warn('Could not fetch inventory:', err);
    }
  }

  renderStorageGrid() {
    const now = new Date();
    const urgentCutoff = new Date(now.getTime() + 48 * 60 * 60 * 1000);

    let fridgeCount = 0;
    let pantryCount = 0;
    let freezerCount = 0;
    let expiringCount = 0;

    this.inventoryItems.forEach(item => {
      const z = (item.zone || 'pantry').toLowerCase();
      if (z.includes('fridge') || z.includes('refrigerator')) fridgeCount++;
      else if (z.includes('freezer')) freezerCount++;
      else pantryCount++;

      if (item.expires_at && new Date(item.expires_at) <= urgentCutoff) {
        expiringCount++;
      }
    });

    const total = this.inventoryItems.length;
    this.storageTotalNum.textContent = total;
    this.countFridge.textContent = fridgeCount;
    this.countPantry.textContent = pantryCount;
    this.countFreezer.textContent = freezerCount;
    this.countExpiring.textContent = expiringCount;

    // Segmented Allocation Bar
    if (total > 0) {
      const fPct = Math.round((fridgeCount / total) * 100);
      const pPct = Math.round((pantryCount / total) * 100);
      const zPct = Math.max(0, 100 - fPct - pPct);
      this.barFridge.style.width = `${fPct}%`;
      this.barPantry.style.width = `${pPct}%`;
      this.barFreezer.style.width = `${zPct}%`;
    }

    // Filter Items
    const q = this.searchQuery;
    const items = this.inventoryItems.filter(item => {
      if (q && !item.item.toLowerCase().includes(q)) return false;
      const z = (item.zone || 'pantry').toLowerCase();
      if (this.activeFilter === 'fridge') return z.includes('fridge') || z.includes('refrigerator');
      if (this.activeFilter === 'pantry') return z.includes('pantry');
      if (this.activeFilter === 'freezer') return z.includes('freezer');
      if (this.activeFilter === 'expiring') return item.expires_at && new Date(item.expires_at) <= urgentCutoff;
      return true;
    });

    this.storageItemsGrid.innerHTML = '';
    if (items.length === 0) {
      this.storageItemsGrid.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 48px; text-align: center; color: rgba(255,255,255,0.4);">
          No items found in this section.
        </div>
      `;
      return;
    }

    items.forEach(item => {
      const isExpiring = item.expires_at && new Date(item.expires_at) <= urgentCutoff;
      const card = document.createElement('div');
      card.className = `storage-item-card ${isExpiring ? 'expiring' : ''}`;

      const zoneRaw = (item.zone || 'Pantry').toLowerCase();
      let zoneLabel = 'Pantry';
      if (zoneRaw.includes('fridge') || zoneRaw.includes('refrigerator')) zoneLabel = 'Fridge';
      else if (zoneRaw.includes('freezer')) zoneLabel = 'Freezer';

      const perishables = ['milk', 'chicken', 'beef', 'yogurt', 'spinach', 'cream', 'fish', 'salmon', 'berries', 'turkey', 'pork'];
      const isPerishable = perishables.some(p => item.item.toLowerCase().includes(p));
      const isOutside = zoneLabel === 'Pantry';
      const isPerishableOutside = isPerishable && isOutside;

      if (isPerishableOutside) {
        card.classList.add('perishable-outside');
      }

      let expiryText = isExpiring ? '⚠️ Expires within 48h' : 'Fresh & ready';
      if (isPerishableOutside) {
        expiryText = '⚠️ Left outside! High spoilage risk (<24h)';
      }

      const moveAction = isPerishableOutside ? `
        <button type="button" class="move-fridge-btn" title="Move to refrigerator">
          ❄️ Move to Fridge
        </button>
      ` : '';

      card.innerHTML = `
        <div class="item-card-top">
          <span class="item-emoji">${this.getItemEmoji(item.item)}</span>
          <span class="item-location-badge ${isPerishableOutside ? 'urgent' : ''}">${isPerishableOutside ? '⚠️ OUTSIDE' : zoneLabel}</span>
        </div>
        <div class="item-card-body">
          <h4>${escapeHtml(item.item)}</h4>
          <p class="item-expiry-text ${isPerishableOutside ? 'danger' : (isExpiring ? 'urgent' : '')}">
            ${expiryText}
          </p>
          ${moveAction}
        </div>
        <div class="item-card-footer">
          <span class="item-qty-badge">${formatDisplayQty(item.qty, item.unit)}</span>
          <div class="item-qty-actions">
            <button class="qty-btn dec-btn" title="Use 1">-</button>
            <button class="qty-btn inc-btn" title="Add 1">+</button>
          </div>
        </div>
      `;

      if (isPerishableOutside) {
        const moveBtn = card.querySelector('.move-fridge-btn');
        if (moveBtn) {
          moveBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
              const res = await fetch('/api/inventory/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item: item.item, zone: 'fridge' })
              });
              if (res.ok) {
                this.musicEngine.playCheckChime();
                const ack = `Moved your ${item.item} to the refrigerator. Freshness extended!`;
                this.appendTranscript('assistant', ack);
                this.speak(ack);
                await this.fetchInventory();
              }
            } catch (err) {
              console.error(err);
            }
          });
        }
      }

      card.querySelector('.dec-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.handleUserUtterance(`I used 1 ${item.item}`);
      });

      card.querySelector('.inc-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.handleUserUtterance(`I bought 1 ${item.item}`);
      });

      this.storageItemsGrid.appendChild(card);
    });
  }

  // ------------------------------------------------------------------------
  // Nutrition & Daily Goals
  // ------------------------------------------------------------------------
  async fetchNutrition() {
    try {
      const res = await fetch('/api/nutrition');
      if (res.ok) {
        const data = await res.json();
        const kcal = Math.round(data.total_kcal || 0);
        const prot = Math.round(data.total_protein_g || 0);
        this.todayKcal.textContent = kcal;
        this.todayProtein.textContent = `${prot}g`;

        // Kinetic Rings Animation
        const kcalCircum = 351.85;
        const protCircum = 263.89;
        const kcalRatio = Math.min(1.0, kcal / 2000);
        const protRatio = Math.min(1.0, prot / 120);

        this.ringKcal.style.strokeDashoffset = kcalCircum * (1 - kcalRatio);
        this.ringProt.style.strokeDashoffset = protCircum * (1 - protRatio);
      }
    } catch (err) {
      console.warn('Could not fetch nutrition:', err);
    }
  }

  // ------------------------------------------------------------------------
  // Recipe Discovery Catalog
  // ------------------------------------------------------------------------
  async fetchRecipes() {
    try {
      const res = await fetch('/api/recipes');
      if (res.ok) {
        const data = await res.json();
        this.allRecipes = data.recipes || [];
        this.renderRecipesList();
      }
    } catch (err) {
      console.warn('Could not fetch recipes:', err);
    }
  }

  renderRecipesList() {
    this.drawerRecipesList.innerHTML = '';
    this.allRecipes.forEach(rec => {
      const card = document.createElement('div');
      card.className = 'recipe-book-card';
      card.innerHTML = `
        <div>
          <div class="recipe-book-title">${escapeHtml(rec.name)}</div>
          <div class="recipe-book-meta">⏱️ ${rec.prep_minutes} min · 🍽️ ${rec.servings} serv · ~${Math.round(rec.kcal_per_serving || 300)} kcal</div>
        </div>
        <button class="recipe-book-btn">Cook</button>
      `;
      card.addEventListener('click', () => {
        this.startRecipe(rec.id);
        this.closeAllDrawers();
      });
      this.drawerRecipesList.appendChild(card);
    });
  }

  async startRecipe(recipeId) {
    try {
      const res = await fetch('/api/cooking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'start', recipe_id: recipeId })
      });
      if (res.ok) {
        const data = await res.json();
        this.activeCooking = data.active_cooking;
        this.renderCookingStage();
        this.switchMode('cooking');
        this.musicEngine.play();
        const startMsg = `Starting ${this.activeCooking.recipe.name}. Ambient cooking music is on! Check off your prep or say 'Next step'.`;
        this.appendTranscript('assistant', startMsg);
        this.speak(startMsg);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // ------------------------------------------------------------------------
  // Drawer Management (Progressive Disclosure)
  // ------------------------------------------------------------------------
  closeAllDrawers() {
    this.chatSlideDrawer.classList.remove('active-drawer');
    this.macroSlideDrawer.classList.remove('active-drawer');
    this.recipesSlideDrawer.classList.remove('active-drawer');
    this.toggleChatDrawerBtn.classList.remove('active');
    this.toggleMacroDrawerBtn.classList.remove('active');
    this.toggleRecipesDrawerBtn.classList.remove('active');
  }

  openChatDrawer() {
    const isCurrentlyOpen = this.chatSlideDrawer.classList.contains('active-drawer');
    this.closeAllDrawers();
    if (!isCurrentlyOpen) {
      this.chatSlideDrawer.classList.add('active-drawer');
      this.toggleChatDrawerBtn.classList.add('active');
      setTimeout(() => this.drawerTextInput.focus(), 150);
    }
  }

  openMacroDrawer() {
    const isCurrentlyOpen = this.macroSlideDrawer.classList.contains('active-drawer');
    this.closeAllDrawers();
    if (!isCurrentlyOpen) {
      this.macroSlideDrawer.classList.add('active-drawer');
      this.toggleMacroDrawerBtn.classList.add('active');
    }
  }

  openRecipesDrawer() {
    const isCurrentlyOpen = this.recipesSlideDrawer.classList.contains('active-drawer');
    this.closeAllDrawers();
    if (!isCurrentlyOpen) {
      this.recipesSlideDrawer.classList.add('active-drawer');
      this.toggleRecipesDrawerBtn.classList.add('active');
    }
  }

  // ------------------------------------------------------------------------
  // Event Listeners
  // ------------------------------------------------------------------------
  initEventListeners() {
    // Top Chrome Mode Switcher
    this.modeCookingBtn.addEventListener('click', () => this.switchMode('cooking'));
    this.modeStorageBtn.addEventListener('click', () => this.switchMode('storage'));

    // Audio Ambience
    this.musicBtn.addEventListener('click', () => {
      if (this.musicEngine.isPlaying) this.musicEngine.stop();
      else this.musicEngine.play();
    });
    this.musicVol.addEventListener('input', (e) => {
      this.musicEngine.setVolume(Number(e.target.value) / 100);
    });

    // Servings Scale Chips
    document.querySelectorAll('.scale-chip').forEach(chip => {
      chip.addEventListener('click', async () => {
        if (!this.activeCooking) return;
        const scale = parseFloat(chip.dataset.scale);
        this.activeCooking.servings = scale;
        this.renderCookingStage();
        try {
          await fetch('/api/cooking', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'set_servings', servings: scale })
          });
        } catch (e) {
          console.warn(e);
        }
      });
    });

    // Transport Playback Controls
    this.timerToggleBtn.addEventListener('click', () => {
      if (this.isTimerRunning) this.pauseStepTimer();
      else this.startStepTimer();
    });

    this.prevStepBtn.addEventListener('click', async () => {
      this.pauseStepTimer();
      try {
        const res = await fetch('/api/cooking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'prev_step' })
        });
        if (res.ok) {
          const data = await res.json();
          this.activeCooking = data.active_cooking;
          this.renderCookingStage();
        }
      } catch (err) {
        console.error(err);
      }
    });

    this.nextStepBtn.addEventListener('click', async () => {
      this.pauseStepTimer();
      try {
        const res = await fetch('/api/cooking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'next_step' })
        });
        if (res.ok) {
          const data = await res.json();
          this.activeCooking = data.active_cooking;
          this.renderCookingStage();
        }
      } catch (err) {
        console.error(err);
      }
    });

    this.finishMealBtn.addEventListener('click', async () => {
      this.pauseStepTimer();
      this.musicEngine.playCheckChime();
      try {
        const res = await fetch('/api/cooking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'finish' })
        });
        if (res.ok) {
          const data = await res.json();
          this.activeCooking = null;
          this.renderCookingStage();
          const celebrationMsg = data.spoken_message || "Delicious! I've deducted your ingredients and logged your meal nutrition.";
          this.appendTranscript('assistant', celebrationMsg);
          this.speak(celebrationMsg);
          await this.fetchInventory();
          await this.fetchNutrition();
        }
      } catch (e) {
        console.error(e);
      }
    });

    // Star Recipe
    this.starRecipeBtn.addEventListener('click', () => {
      this.starRecipeBtn.classList.toggle('starred');
    });

    // Lyrics vs Prep Tab Toggle
    this.tabShowSteps.addEventListener('click', () => {
      this.tabShowSteps.classList.add('active');
      this.tabShowPrep.classList.remove('active');
      this.lyricsViewport.classList.remove('hidden');
      this.prepChecklistViewport.classList.add('hidden');
    });

    this.tabShowPrep.addEventListener('click', () => {
      this.tabShowPrep.classList.add('active');
      this.tabShowSteps.classList.remove('active');
      this.prepChecklistViewport.classList.remove('hidden');
      this.lyricsViewport.classList.add('hidden');
    });

    // Floating Dock Buttons
    this.voiceActivityPill.addEventListener('click', () => this.toggleListening());
    this.toggleChatDrawerBtn.addEventListener('click', () => this.openChatDrawer());
    this.toggleMacroDrawerBtn.addEventListener('click', () => this.openMacroDrawer());
    this.toggleRecipesDrawerBtn.addEventListener('click', () => this.openRecipesDrawer());

    // Drawer Close Buttons
    this.closeChatDrawerBtn.addEventListener('click', () => this.closeAllDrawers());
    this.closeMacroDrawerBtn.addEventListener('click', () => this.closeAllDrawers());
    this.closeRecipesDrawerBtn.addEventListener('click', () => this.closeAllDrawers());

    // Chat Drawer Input
    this.drawerMicBtn.addEventListener('click', () => this.toggleListening());
    this.drawerChatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = this.drawerTextInput.value.trim();
      if (!val) return;
      this.drawerTextInput.value = '';
      this.handleUserUtterance(val);
    });

    // Emergency Rescue Chips
    document.querySelectorAll('.rescue-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        this.handleUserUtterance(chip.dataset.phrase);
      });
    });

    // Emergency Alert Sheet Confirm
    this.alertRemedyConfirmBtn.addEventListener('click', () => {
      this.emergencyAlertSheet.classList.add('hidden');
      if (this.musicEngine.wasPlayingBeforeTimer) {
        this.musicEngine.play();
      }
    });

    // Storage Search & Segment Filters
    this.inventorySearchInput.addEventListener('input', (e) => {
      this.searchQuery = e.target.value.trim().toLowerCase();
      this.searchClearBtn.classList.toggle('hidden', this.searchQuery.length === 0);
      this.renderStorageGrid();
    });

    this.searchClearBtn.addEventListener('click', () => {
      this.inventorySearchInput.value = '';
      this.searchQuery = '';
      this.searchClearBtn.classList.add('hidden');
      this.renderStorageGrid();
    });

    document.querySelectorAll('.seg-filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.seg-filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.activeFilter = e.target.dataset.filter;
        this.renderStorageGrid();
      });
    });

    // Apple Keyboard Navigation Shortcuts
    window.addEventListener('keydown', (e) => {
      // Don't trigger shortcuts if user is typing in an input
      if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
        if (e.key === 'Escape') {
          document.activeElement.blur();
          this.closeAllDrawers();
        }
        return;
      }

      if (e.code === 'Space') {
        e.preventDefault();
        if (this.isTimerRunning) this.pauseStepTimer();
        else this.startStepTimer();
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        this.nextStepBtn.click();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        this.prevStepBtn.click();
      } else if (e.key === '/') {
        e.preventDefault();
        this.openChatDrawer();
      } else if (e.key === 'Escape') {
        this.closeAllDrawers();
        this.emergencyAlertSheet.classList.add('hidden');
      }
    });
  }

  getItemEmoji(name) {
    const n = (name || '').toLowerCase();
    if (n.includes('milk') || n.includes('dairy')) return '🥛';
    if (n.includes('egg')) return '🥚';
    if (n.includes('cheese') || n.includes('cheddar')) return '🧀';
    if (n.includes('spinach') || n.includes('kale') || n.includes('salad')) return '🥬';
    if (n.includes('chicken') || n.includes('meat') || n.includes('beef')) return '🍗';
    if (n.includes('oil') || n.includes('olive')) return '🫒';
    if (n.includes('bread') || n.includes('toast')) return '🍞';
    if (n.includes('berry') || n.includes('fruit')) return '🫐';
    if (n.includes('garlic') || n.includes('onion')) return '🧄';
    if (n.includes('pasta') || n.includes('noodle')) return '🍝';
    if (n.includes('butter')) return '🧈';
    return '🍳';
  }
}

// --------------------------------------------------------------------------
// Helpers
// --------------------------------------------------------------------------
function escapeHtml(str) {
  return str ? String(str).replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]) : '';
}

function formatDisplayQty(qty, unit) {
  if (unit === 'ml') {
    if (Math.abs(qty - 7570.82) < 100) return '2 gallons';
    if (Math.abs(qty - 3785.41) < 50) return '1 gallon';
    if (Math.abs(qty - 946.35) < 30) return '1 quart';
    if (Math.abs(qty - 236.59) < 15) return '1 cup';
    return `${Math.round(qty)} ml`;
  }
  if (unit === 'g') {
    if (Math.abs(qty - 453.59) < 20) return '1 lb';
    if (qty >= 1000) return `${(qty/1000).toFixed(1)} kg`;
    return `${Math.round(qty)} g`;
  }
  return `${qty % 1 === 0 ? Math.round(qty) : qty} ${unit || ''}`.trim();
}

// Mount on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new SousChefVoiceApp();
});
