// ==========================================================================
// Sous-Chef Smart Alexa+ Kitchen Assistant Companion
// FastMCP 1.30.0 Streamable HTTP • Amazon Echo Live Sync • Amazon Polly Neural
// ==========================================================================

// --------------------------------------------------------------------------
// 1. Alexa Speech & Audio Synthesis Engine (Amazon Polly Neural + Web Fallback)
// --------------------------------------------------------------------------
class AlexaVoiceEngine {
  constructor() {
    this.audioElement = document.getElementById('alexa-polly-audio');
    this.soundwaveAnim = document.getElementById('alexa-soundwave-anim');
    this.spokenBannerText = document.getElementById('alexa-spoken-text');
    this.isPlaying = false;
    this.selectedFemaleVoice = null;
    this.initBrowserVoices();

    if (this.audioElement) {
      this.audioElement.addEventListener('ended', () => this.handleSpeechEnd());
      this.audioElement.addEventListener('pause', () => this.handleSpeechEnd());
      this.audioElement.addEventListener('error', (e) => {
        console.warn('Polly audio playback error, falling back:', e);
        this.handleSpeechEnd();
      });
    }
  }

  initBrowserVoices() {
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

  setBannerText(text) {
    if (this.spokenBannerText && text) {
      this.spokenBannerText.textContent = `"${text}"`;
    }
  }

  async speak(text, audioUrl = null, onComplete = null) {
    if (!text || !text.trim()) {
      if (onComplete) onComplete();
      return;
    }

    const cleanText = text.trim();
    this.setBannerText(cleanText);

    // Update voice activity pill in dock
    const phrasePill = document.getElementById('active-voice-phrase');
    if (phrasePill) {
      phrasePill.textContent = `Alexa: "${cleanText.slice(0, 55)}${cleanText.length > 55 ? '...' : ''}"`;
    }
    const voicePill = document.getElementById('voice-activity-pill');
    if (voicePill) voicePill.classList.add('listening');

    // Trigger visual soundwave
    this.startSoundwave();

    // 1. Try Amazon Polly Neural audio playback first
    const pollyUrl = audioUrl || `/api/tts?text=${encodeURIComponent(cleanText)}`;
    if (this.audioElement) {
      try {
        this.audioElement.src = pollyUrl;
        const playPromise = this.audioElement.play();
        if (playPromise !== undefined) {
          await playPromise;
          this.isPlaying = true;
          this.audioElement.onended = () => {
            this.handleSpeechEnd();
            if (onComplete) onComplete();
          };
          return;
        }
      } catch (err) {
        console.warn('Polly audio stream not playable, falling back to Web Speech:', err);
      }
    }

    // 2. Client Web Speech Synthesis Fallback
    this.speakWithWebSpeech(cleanText, onComplete);
  }

  speakWithWebSpeech(text, onComplete = null) {
    if (!('speechSynthesis' in window)) {
      this.handleSpeechEnd();
      if (onComplete) onComplete();
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    if (this.selectedFemaleVoice) {
      utterance.voice = this.selectedFemaleVoice;
    }
    utterance.rate = 1.02;
    utterance.pitch = 1.0;

    const cleanup = () => {
      this.handleSpeechEnd();
      if (onComplete) onComplete();
    };

    utterance.onend = cleanup;
    utterance.onerror = cleanup;
    window.speechSynthesis.speak(utterance);
    this.isPlaying = true;
  }

  startSoundwave() {
    if (this.soundwaveAnim) {
      this.soundwaveAnim.classList.add('active');
    }
  }

  handleSpeechEnd() {
    this.isPlaying = false;
    if (this.soundwaveAnim) {
      this.soundwaveAnim.classList.remove('active');
    }
    const voicePill = document.getElementById('voice-activity-pill');
    if (voicePill) voicePill.classList.remove('listening');
    const phrasePill = document.getElementById('active-voice-phrase');
    if (phrasePill) {
      phrasePill.innerHTML = 'Synced with Amazon Echo &bull; Speak or tap to cook';
    }
  }

  playTimerDing() {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const tones = [880, 1174.66, 1760];
    const now = ctx.currentTime;
    tones.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now + i * 0.16);
      gain.gain.setValueAtTime(0, now + i * 0.16);
      gain.gain.linearRampToValueAtTime(0.25, now + i * 0.16 + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.16 + 1.2);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.16);
      osc.stop(now + i * 0.16 + 1.25);
    });
  }

  playTapChime() {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const now = ctx.currentTime;
    osc.type = 'sine';
    osc.frequency.setValueAtTime(659.25, now);
    osc.frequency.exponentialRampToValueAtTime(1318.51, now + 0.08);
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.2);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.22);
  }
}

// --------------------------------------------------------------------------
// 2. Main SousChefVoiceApp Architecture
// --------------------------------------------------------------------------
class SousChefVoiceApp {
  constructor() {
    // Mode Switcher Elements (3 Modes)
    this.modeCookingBtn = document.getElementById('mode-cooking-btn');
    this.modeCookbookBtn = document.getElementById('mode-cookbook-btn');
    this.modeStorageBtn = document.getElementById('mode-storage-btn');
    this.viewNowCooking = document.getElementById('view-now-cooking');
    this.viewCookbook = document.getElementById('view-cookbook');
    this.viewStorage = document.getElementById('view-storage');

    // Ambient Aura
    this.ambientBackdrop = document.getElementById('ambient-backdrop');

    // View 1: Active Cooking Hero
    this.dishName = document.getElementById('dish-name');
    this.dishSub = document.getElementById('dish-sub');
    this.dishArtworkEmoji = document.getElementById('dish-artwork-emoji');
    this.dishCoverArtwork = document.getElementById('dish-cover-artwork');
    this.recipePhaseFill = document.getElementById('recipe-phase-fill');
    this.phaseStepLabel = document.getElementById('phase-step-label');
    this.phaseTimerBadge = document.getElementById('phase-timer-badge');
    this.timerCountdownDisplay = document.getElementById('timer-countdown-display');
    this.prevStepBtn = document.getElementById('prev-step-btn');
    this.timerToggleBtn = document.getElementById('timer-toggle-btn');
    this.timerBtnText = document.getElementById('timer-btn-text');
    this.nextStepBtn = document.getElementById('next-step-btn');
    this.finishMealBtn = document.getElementById('finish-meal-btn');

    // View 1: Dialogue & Steps Stream
    this.alexaSpokenBanner = document.getElementById('alexa-spoken-banner');
    this.alexaSpokenText = document.getElementById('alexa-spoken-text');
    this.streamStatusLabel = document.getElementById('stream-status-label');
    this.tabShowSteps = document.getElementById('tab-show-steps');
    this.tabShowPrep = document.getElementById('tab-show-prep');
    this.prepReadyCount = document.getElementById('prep-ready-count');
    this.lyricsViewport = document.getElementById('lyrics-viewport');
    this.prepChecklistViewport = document.getElementById('prep-checklist-viewport');

    // View 2: Cookbook & Share
    this.cookbookRecipesGrid = document.getElementById('cookbook-recipes-grid');
    this.customRecipeOpenBtn = document.getElementById('custom-recipe-open-btn');

    // View 3: Pantry Freshness Health Gauge
    this.freshnessScoreVal = document.getElementById('freshness-score-val');
    this.barSafe = document.getElementById('bar-safe');
    this.barWarn = document.getElementById('bar-warn');
    this.barDanger = document.getElementById('bar-danger');
    this.countSafe = document.getElementById('count-safe');
    this.countWarn = document.getElementById('count-warn');
    this.countDanger = document.getElementById('count-danger');
    this.inventorySearchInput = document.getElementById('inventory-search-input');
    this.searchClearBtn = document.getElementById('search-clear-btn');
    this.storageItemsGrid = document.getElementById('storage-items-grid');

    // Bottom Dock: Integrated Voice & Input
    this.voiceActivityPill = document.getElementById('voice-activity-pill');
    this.activeVoicePhrase = document.getElementById('active-voice-phrase');
    this.screenMicBtn = document.getElementById('screen-mic-btn');
    this.screenTextInput = document.getElementById('screen-text-input');
    this.screenAskBtn = document.getElementById('screen-ask-btn');
    this.toggleMacroDrawerBtn = document.getElementById('toggle-macro-drawer-btn');

    // Modals & Drawers
    this.macroSlideDrawer = document.getElementById('macro-slide-drawer');
    this.closeMacroDrawerBtn = document.getElementById('close-macro-drawer-btn');
    this.ringCalories = document.getElementById('ring-calories');
    this.ringProtein = document.getElementById('ring-protein');
    this.ringCalCount = document.getElementById('ring-cal-count');
    this.macroCaloriesVal = document.getElementById('macro-calories-val');
    this.macroProteinVal = document.getElementById('macro-protein-val');

    this.customRecipeModal = document.getElementById('custom-recipe-modal');
    this.modalBackdrop = document.getElementById('modal-backdrop');
    this.modalCloseBtn = document.getElementById('modal-close-btn');
    this.btnCancelModal = document.getElementById('btn-cancel-modal');
    this.customRecipeForm = document.getElementById('custom-recipe-form');

    this.emergencyAlertSheet = document.getElementById('emergency-alert-sheet');
    this.alertRemedyTitle = document.getElementById('alert-remedy-title');
    this.alertRemedySubtitle = document.getElementById('alert-remedy-subtitle');
    this.alertRemedyBody = document.getElementById('alert-remedy-body');
    this.alertRemedyConfirmBtn = document.getElementById('alert-remedy-confirm-btn');

    // State Variables
    this.currentMode = 'cooking'; // 'cooking' | 'cookbook' | 'storage'
    this.activeCooking = null;
    this.inventoryItems = [];
    this.allRecipes = [];
    this.activeFilter = 'all';
    this.searchQuery = '';
    this.isListening = false;
    this.recognition = null;

    // Timer State
    this.stepTimerTotal = 0;
    this.stepTimerRemaining = 0;
    this.stepTimerInterval = null;
    this.isTimerRunning = false;

    // Alexa Voice Engine
    this.voiceEngine = new AlexaVoiceEngine();

    // Bootstrap
    this.initSpeechRecognition();
    this.initEventListeners();
    this.initPWA();
    this.startPresenceHeartbeat();

    // Initial Fetch
    this.fetchCookingState();
    this.fetchInventory();
    this.fetchNutrition();
    this.fetchRecipes();

    // Live Echo Sync Heartbeat
    setInterval(() => {
      this.fetchCookingState();
      this.fetchInventory();
      this.fetchNutrition();
    }, 3000);
  }

  // ------------------------------------------------------------------------
  // PWA Service Worker
  // ------------------------------------------------------------------------
  initPWA() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(err => {
        console.warn('PWA registration:', err);
      });
    }
  }

  // ------------------------------------------------------------------------
  // Mode Switcher (Cooking | Cookbook | Storage)
  // ------------------------------------------------------------------------
  switchMode(mode) {
    this.currentMode = mode;
    const modes = [
      { id: 'cooking', btn: this.modeCookingBtn, view: this.viewNowCooking },
      { id: 'cookbook', btn: this.modeCookbookBtn, view: this.viewCookbook },
      { id: 'storage', btn: this.modeStorageBtn, view: this.viewStorage }
    ];

    modes.forEach(m => {
      if (m.id === mode) {
        m.btn?.classList.add('active');
        m.view?.classList.remove('hidden');
        m.view?.classList.add('active');
      } else {
        m.btn?.classList.remove('active');
        m.view?.classList.add('hidden');
        m.view?.classList.remove('active');
      }
    });
  }

  // ------------------------------------------------------------------------
  // Web Speech Recognition
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
        this.screenMicBtn.classList.add('active');
        this.activeVoicePhrase.textContent = 'Listening to your kitchen command...';
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
      this.screenTextInput.focus();
      this.screenTextInput.placeholder = "Microphone unavailable. Type here...";
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
    this.screenMicBtn.classList.remove('active');
    setTimeout(() => {
      if (!this.voiceEngine.isPlaying) {
        this.activeVoicePhrase.innerHTML = 'Synced with Amazon Echo &bull; Speak or tap to cook';
      }
    }, 2500);
  }

  // ------------------------------------------------------------------------
  // Multimodal Conversational Dispatcher
  // ------------------------------------------------------------------------
  async handleUserUtterance(text) {
    if (!text || !text.trim()) return;
    const utterance = text.trim();

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

      // Step Timer Commands
      if (data.timer_command === 'start') this.startStepTimer();
      else if (data.timer_command === 'stop') this.pauseStepTimer();

      // Active cooking state update
      if (data.active_cooking !== undefined) {
        this.activeCooking = data.active_cooking;
        this.renderCookingStage();
        this.switchMode('cooking');
      }

      // Emergency rescue remedy
      if (data.remedy) {
        this.showEmergencyRescue(data.remedy);
      }

      // Speak with authentic Amazon Polly voice
      const audioUrl = data.audio_url || `/api/tts?text=${encodeURIComponent(reply)}`;
      this.voiceEngine.speak(reply, audioUrl);

      // Refresh inventory & nutrition
      await this.fetchInventory();
      await this.fetchNutrition();

    } catch (err) {
      console.error(err);
      const fallback = "Sorry, I had trouble reaching the kitchen server.";
      this.voiceEngine.speak(fallback);
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
  }

  // ------------------------------------------------------------------------
  // Echo Presence Heartbeat
  // ------------------------------------------------------------------------
  startPresenceHeartbeat() {
    const sendPresence = (status) => {
      try {
        fetch('/api/presence', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: status || 'active', client: 'web_screen' })
        }).catch(() => {});
      } catch (e) {}
    };

    sendPresence('active');
    setInterval(() => sendPresence('active'), 8000);

    document.addEventListener('visibilitychange', () => {
      sendPresence(document.visibilityState === 'visible' ? 'active' : 'inactive');
    });

    window.addEventListener('beforeunload', () => {
      try {
        navigator.sendBeacon('/api/presence', JSON.stringify({ status: 'closed', client: 'web_screen' }));
      } catch (e) {}
    });
  }

  // ------------------------------------------------------------------------
  // Dynamic Dish Palette (Harmonious Theme Generation)
  // ------------------------------------------------------------------------
  applyDishPalette(dishName, ingredients = []) {
    const ingText = Array.isArray(ingredients)
      ? ingredients.map(i => (typeof i === 'string' ? i : (i.item || i.name || ''))).join(' ')
      : String(ingredients || '');
    const text = (dishName + ' ' + ingText).toLowerCase();

    let palette = {
      hue: 38,
      primary: '#f59e0b',
      secondary: '#d97706',
      aura: 'rgba(245, 158, 11, 0.24)',
      glow: 'rgba(245, 158, 11, 0.45)',
      accentBg: 'rgba(245, 158, 11, 0.12)'
    };

    if (/salad|greens|kale|spinach|pesto|herb|avocado|cucumber|bowl/.test(text)) {
      palette = {
        hue: 158,
        primary: '#10b981',
        secondary: '#059669',
        aura: 'rgba(16, 185, 129, 0.22)',
        glow: 'rgba(16, 185, 129, 0.40)',
        accentBg: 'rgba(16, 185, 129, 0.12)'
      };
    } else if (/pasta|spaghetti|marinara|tomato|pizza|lasagna|bolognese/.test(text)) {
      palette = {
        hue: 347,
        primary: '#e11d48',
        secondary: '#be123c',
        aura: 'rgba(225, 29, 72, 0.24)',
        glow: 'rgba(225, 29, 72, 0.42)',
        accentBg: 'rgba(225, 29, 72, 0.12)'
      };
    } else if (/curry|spicy|chili|taco|fajita|stir fry|pepper|masala|roast/.test(text)) {
      palette = {
        hue: 20,
        primary: '#ea580c',
        secondary: '#c2410c',
        aura: 'rgba(234, 88, 12, 0.25)',
        glow: 'rgba(234, 88, 12, 0.45)',
        accentBg: 'rgba(234, 88, 12, 0.12)'
      };
    } else if (/salmon|fish|tuna|shrimp|seafood|cod/.test(text)) {
      palette = {
        hue: 189,
        primary: '#06b6d4',
        secondary: '#0891b2',
        aura: 'rgba(6, 182, 212, 0.22)',
        glow: 'rgba(6, 182, 212, 0.40)',
        accentBg: 'rgba(6, 182, 212, 0.12)'
      };
    } else if (/berry|smoothie|acai|oat|dessert|cake|cookie|pancake/.test(text)) {
      palette = {
        hue: 260,
        primary: '#8b5cf6',
        secondary: '#6d28d9',
        aura: 'rgba(139, 92, 246, 0.22)',
        glow: 'rgba(139, 92, 246, 0.40)',
        accentBg: 'rgba(139, 92, 246, 0.12)'
      };
    }

    const root = document.documentElement;
    root.style.setProperty('--dish-hue', palette.hue);
    root.style.setProperty('--dish-primary', palette.primary);
    root.style.setProperty('--dish-secondary', palette.secondary);
    root.style.setProperty('--dish-aura', palette.aura);
    root.style.setProperty('--dish-glow', palette.glow);
    root.style.setProperty('--dish-accent-bg', palette.accentBg);
  }

  // ------------------------------------------------------------------------
  // Guided Cooking Station
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
      // Default idle state
      this.applyDishPalette("Spinach & Cheddar Scramble", ["eggs", "spinach", "cheddar"]);
      this.dishName.textContent = "Spinach & Cheddar Scramble";
      this.dishSub.textContent = "10 min · 2 servings · ~320 kcal";
      this.dishArtworkEmoji.textContent = "🍳";
      this.streamStatusLabel.textContent = "READY TO COOK";
      this.phaseStepLabel.textContent = "Ready to Cook";
      this.recipePhaseFill.style.width = "0%";
      this.phaseTimerBadge.classList.add('hidden');
      this.timerToggleBtn.classList.add('hidden');
      this.finishMealBtn.classList.add('hidden');

      this.lyricsViewport.innerHTML = `
        <div class="lyric-line active" data-step-index="0">
          <div class="lyric-badge">Welcome</div>
          <div class="lyric-text">Say "Alexa, ask Sous-Chef what can I cook" or pick a recipe from the Cookbook tab to begin!</div>
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

    // Apply Palette
    this.applyDishPalette(recipe.name, recipe.ingredients || []);

    // 1. Hero Left Column
    this.dishName.textContent = recipe.name;
    this.dishSub.textContent = `${recipe.prep_minutes || 15} min · ${currentServings} servings · ~${Math.round((recipe.kcal_per_serving || 320) * multiplier)} kcal`;
    this.dishArtworkEmoji.textContent = this.getItemEmoji(recipe.name);

    // Update Progress Phase Bar
    const progressPct = Math.round((activeStepIdx / totalSteps) * 100);
    this.recipePhaseFill.style.width = `${progressPct}%`;
    const stepType = activeStepIdx === 1 ? 'Prep' : (activeStepIdx === totalSteps ? 'Final Step' : 'Cooking');
    this.phaseStepLabel.textContent = `Step ${activeStepIdx} of ${totalSteps} · ${stepType}`;

    // Finish Meal Button
    if (activeStepIdx === totalSteps) {
      this.finishMealBtn.classList.remove('hidden');
      this.nextStepBtn.classList.add('hidden');
    } else {
      this.finishMealBtn.classList.add('hidden');
      this.nextStepBtn.classList.remove('hidden');
    }

    // 2. Synchronized Steps Stream
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

      // Touch-to-Voice: Tapping jumps step & triggers Alexa voice explanation!
      line.addEventListener('click', () => {
        this.setCookingStep(stepNum);
      });

      this.lyricsViewport.appendChild(line);
    });

    // Auto-scroll active step to center
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
        this.voiceEngine.playTapChime();
        const res = await fetch('/api/cooking', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'check_prep', item: ing.item })
        });
        if (res.ok) {
          const data = await res.json();
          this.activeCooking = data.active_cooking;
          if (data.spoken_message) {
            this.voiceEngine.speak(data.spoken_message, data.audio_url);
          }
          this.renderCookingStage();
        }
      });

      this.prepChecklistViewport.appendChild(row);
    });

    this.prepReadyCount.textContent = `${checkedCount}/${ingredients.length}`;

    // 4. Timer Setup for current step
    if (activeStepObj.timer_seconds && activeStepObj.timer_seconds > 0) {
      this.phaseTimerBadge.classList.remove('hidden');
      this.timerToggleBtn.classList.remove('hidden');
      if (this.stepTimerTotal !== activeStepObj.timer_seconds) {
        this.stepTimerTotal = activeStepObj.timer_seconds;
        this.stepTimerRemaining = activeStepObj.timer_seconds;
        this.updateTimerDisplay();
      }
    } else {
      this.phaseTimerBadge.classList.add('hidden');
      this.timerToggleBtn.classList.add('hidden');
      this.stepTimerTotal = 0;
      this.stepTimerRemaining = 0;
      this.pauseStepTimer();
    }
  }

  async setCookingStep(stepNum) {
    this.voiceEngine.playTapChime();
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
        const steps = this.activeCooking?.recipe?.steps || [];
        const stepInst = steps[stepNum - 1]?.instruction || '';
        const msg = `Step ${stepNum}: ${stepInst}`;
        this.voiceEngine.speak(msg);
      }
    } catch (err) {
      console.error(err);
    }
  }

  // ------------------------------------------------------------------------
  // Tactical Kitchen Step Timer
  // ------------------------------------------------------------------------
  startStepTimer() {
    if (this.isTimerRunning) return;
    this.isTimerRunning = true;
    if (this.timerBtnText) this.timerBtnText.textContent = 'Pause Timer';

    this.stepTimerInterval = setInterval(() => {
      if (this.stepTimerRemaining > 0) {
        this.stepTimerRemaining--;
        this.updateTimerDisplay();
      } else {
        this.handleTimerFinished();
      }
    }, 1000);
  }

  pauseStepTimer() {
    this.isTimerRunning = false;
    if (this.timerBtnText) this.timerBtnText.textContent = 'Start Timer';
    if (this.stepTimerInterval) {
      clearInterval(this.stepTimerInterval);
      this.stepTimerInterval = null;
    }
  }

  resetStepTimer() {
    this.pauseStepTimer();
    this.stepTimerRemaining = this.stepTimerTotal;
    this.updateTimerDisplay();
  }

  updateTimerDisplay() {
    const mins = Math.floor(this.stepTimerRemaining / 60);
    const secs = this.stepTimerRemaining % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    if (this.timerCountdownDisplay) {
      this.timerCountdownDisplay.textContent = formatted;
    }
  }

  handleTimerFinished() {
    this.pauseStepTimer();
    this.voiceEngine.playTimerDing();

    let alertMsg = "Timer completed! Turn down the heat and check your dish.";
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

    this.voiceEngine.speak(alertMsg);
  }

  // ------------------------------------------------------------------------
  // View 2: Cookbook & Community (Browse & 1-Click Share)
  // ------------------------------------------------------------------------
  async fetchRecipes() {
    try {
      const res = await fetch('/api/recipes');
      if (res.ok) {
        const data = await res.json();
        this.allRecipes = data.recipes || [];
        this.renderCookbookGrid();
      }
    } catch (err) {
      console.warn('Could not fetch recipes:', err);
    }
  }

  renderCookbookGrid() {
    if (!this.cookbookRecipesGrid) return;
    this.cookbookRecipesGrid.innerHTML = '';

    if (this.allRecipes.length === 0) {
      this.cookbookRecipesGrid.innerHTML = `
        <div style="grid-column: 1 / -1; padding: 48px; text-align: center; color: rgba(255,255,255,0.4);">
          No recipes found in cookbook. Add one above!
        </div>
      `;
      return;
    }

    this.allRecipes.forEach(rec => {
      const card = document.createElement('div');
      card.className = 'cookbook-card';

      const ingredientsList = (rec.ingredients || [])
        .map(i => typeof i === 'string' ? i : i.item)
        .slice(0, 4)
        .join(', ');

      card.innerHTML = `
        <div class="cookbook-card-cover">
          <span class="cookbook-card-emoji">${this.getItemEmoji(rec.name)}</span>
        </div>
        <div class="cookbook-card-info">
          <h3 class="cookbook-card-title">${escapeHtml(rec.name)}</h3>
          <p class="cookbook-card-meta">⏱️ ${rec.prep_minutes || 15} min · 🍽️ ${rec.servings || 2} servings · ~${Math.round(rec.kcal_per_serving || 300)} kcal</p>
          <p class="cookbook-card-ingredients"><strong>Ingredients:</strong> ${escapeHtml(ingredientsList)}${(rec.ingredients || []).length > 4 ? '...' : ''}</p>
          <div class="cookbook-card-actions">
            <button class="cook-now-btn" data-id="${rec.id}">🍳 Cook Now</button>
            <button class="share-recipe-btn" data-id="${rec.id}">🔗 Share</button>
          </div>
        </div>
      `;

      // Cook Now Action
      card.querySelector('.cook-now-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.startRecipe(rec.id);
      });

      // Share Recipe Action
      card.querySelector('.share-recipe-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.shareRecipe(rec);
      });

      this.cookbookRecipesGrid.appendChild(card);
    });
  }

  async startRecipe(recipeId) {
    this.voiceEngine.playTapChime();
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
        const startMsg = data.spoken_message || `Let's make ${this.activeCooking.recipe.name}! Step 1: Check your ingredients.`;
        this.voiceEngine.speak(startMsg, data.audio_url);
      }
    } catch (err) {
      console.error(err);
    }
  }

  shareRecipe(recipe) {
    const shareData = {
      title: `Sous-Chef Recipe: ${recipe.name}`,
      text: `Try cooking ${recipe.name}! Ready in ${recipe.prep_minutes || 15} minutes with Sous-Chef on Alexa.`,
      url: window.location.origin + `/?recipe=${encodeURIComponent(recipe.id || recipe.name)}`
    };

    if (navigator.share) {
      navigator.share(shareData).catch(err => {
        if (err.name !== 'AbortError') console.warn('Share error:', err);
      });
    } else {
      navigator.clipboard.writeText(shareData.url).then(() => {
        this.showToast(`Recipe link copied to clipboard! 📋`);
      }).catch(() => {
        this.showToast(`Shared: ${recipe.name}`);
      });
    }
  }

  showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'apple-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('visible'), 10);
    setTimeout(() => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  // ------------------------------------------------------------------------
  // View 3: Pantry Freshness & Spoilage Prevention Index
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

    const perishables = ['milk', 'chicken', 'beef', 'yogurt', 'spinach', 'cream', 'fish', 'salmon', 'berries', 'turkey', 'pork'];

    let safeCount = 0;
    let warnCount = 0;
    let dangerCount = 0;

    this.inventoryItems.forEach(item => {
      const z = (item.zone || 'pantry').toLowerCase();
      const isOutside = !z.includes('fridge') && !z.includes('refrigerator') && !z.includes('freezer');
      const isPerishable = perishables.some(p => item.item.toLowerCase().includes(p));
      const isPerishableOutside = isPerishable && isOutside;
      const isExpiring = item.expires_at && new Date(item.expires_at) <= urgentCutoff;

      if (isPerishableOutside) {
        dangerCount++;
      } else if (isExpiring) {
        warnCount++;
      } else {
        safeCount++;
      }
    });

    const total = this.inventoryItems.length;
    this.countSafe.textContent = safeCount;
    this.countWarn.textContent = warnCount;
    this.countDanger.textContent = dangerCount;

    // Household Freshness Health Score (100 - penalties for danger & warn)
    let healthScore = 100;
    if (total > 0) {
      const safeRatio = safeCount / total;
      healthScore = Math.max(10, Math.round(safeRatio * 100) - (dangerCount * 10));
    }
    this.freshnessScoreVal.textContent = `${Math.min(100, Math.max(0, healthScore))}%`;

    // Dynamic Visual Slices in the Health Gauge
    if (total > 0) {
      const safePct = Math.round((safeCount / total) * 100);
      const warnPct = Math.round((warnCount / total) * 100);
      const dangerPct = Math.max(0, 100 - safePct - warnPct);
      this.barSafe.style.width = `${safePct}%`;
      this.barWarn.style.width = `${warnPct}%`;
      this.barDanger.style.width = `${dangerPct}%`;
    }

    // Filter Items
    const q = this.searchQuery;
    const items = this.inventoryItems.filter(item => {
      if (q && !item.item.toLowerCase().includes(q)) return false;
      const z = (item.zone || 'pantry').toLowerCase();
      const isOutside = !z.includes('fridge') && !z.includes('refrigerator') && !z.includes('freezer');
      const isPerishable = perishables.some(p => item.item.toLowerCase().includes(p));
      const isPerishableOutside = isPerishable && isOutside;
      const isExpiring = item.expires_at && new Date(item.expires_at) <= urgentCutoff;

      if (this.activeFilter === 'fridge') return z.includes('fridge') || z.includes('refrigerator');
      if (this.activeFilter === 'pantry') return z.includes('pantry');
      if (this.activeFilter === 'freezer') return z.includes('freezer');
      if (this.activeFilter === 'expiring') return isExpiring || isPerishableOutside;
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

      const isOutside = zoneLabel === 'Pantry';
      const isPerishable = perishables.some(p => item.item.toLowerCase().includes(p));
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
                this.voiceEngine.playTapChime();
                const ack = `Moved your ${item.item} to the refrigerator. Freshness extended!`;
                this.voiceEngine.speak(ack);
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
  // Daily Nutrition Rings
  // ------------------------------------------------------------------------
  async fetchNutrition() {
    try {
      const res = await fetch('/api/nutrition');
      if (res.ok) {
        const data = await res.json();
        const kcal = Math.round(data.total_kcal || 0);
        const prot = Math.round(data.total_protein_g || 0);

        if (this.ringCalCount) this.ringCalCount.textContent = kcal;
        if (this.macroCaloriesVal) this.macroCaloriesVal.textContent = `${kcal} / 2,000`;
        if (this.macroProteinVal) this.macroProteinVal.textContent = `${prot}g / 120g`;

        // Kinetic Apple Macro Rings
        if (this.ringCalories) {
          const kcalCircum = 502;
          const kcalRatio = Math.min(1.0, kcal / 2000);
          this.ringCalories.style.strokeDashoffset = kcalCircum * (1 - kcalRatio);
        }
        if (this.ringProtein) {
          const protCircum = 377;
          const protRatio = Math.min(1.0, prot / 120);
          this.ringProtein.style.strokeDashoffset = protCircum * (1 - protRatio);
        }
      }
    } catch (err) {
      console.warn('Could not fetch nutrition:', err);
    }
  }

  // ------------------------------------------------------------------------
  // Modal & Drawer Management
  // ------------------------------------------------------------------------
  openMacroDrawer() {
    this.macroSlideDrawer.classList.add('active-drawer');
    this.toggleMacroDrawerBtn.classList.add('active');
  }

  closeMacroDrawer() {
    this.macroSlideDrawer.classList.remove('active-drawer');
    this.toggleMacroDrawerBtn.classList.remove('active');
  }

  openCustomRecipeModal() {
    this.customRecipeModal.classList.remove('hidden');
  }

  closeCustomRecipeModal() {
    this.customRecipeModal.classList.add('hidden');
  }

  // ------------------------------------------------------------------------
  // Event Listeners
  // ------------------------------------------------------------------------
  initEventListeners() {
    // Mode Switcher Tabs
    this.modeCookingBtn.addEventListener('click', () => this.switchMode('cooking'));
    this.modeCookbookBtn.addEventListener('click', () => this.switchMode('cookbook'));
    this.modeStorageBtn.addEventListener('click', () => this.switchMode('storage'));

    // Cooking Tactical Controls
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
          if (data.spoken_message) {
            this.voiceEngine.speak(data.spoken_message, data.audio_url);
          }
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
          if (data.spoken_message) {
            this.voiceEngine.speak(data.spoken_message, data.audio_url);
          }
        }
      } catch (err) {
        console.error(err);
      }
    });

    this.timerToggleBtn.addEventListener('click', () => {
      if (this.isTimerRunning) this.pauseStepTimer();
      else this.startStepTimer();
    });

    this.finishMealBtn.addEventListener('click', async () => {
      this.pauseStepTimer();
      this.voiceEngine.playTapChime();
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
          this.voiceEngine.speak(celebrationMsg, data.audio_url);
          await this.fetchInventory();
          await this.fetchNutrition();
        }
      } catch (e) {
        console.error(e);
      }
    });

    // Steps vs Prep Tab Switcher
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

    // On-Screen Speech & Query Bar
    this.screenMicBtn.addEventListener('click', () => this.toggleListening());
    this.screenAskBtn.addEventListener('click', () => {
      const val = this.screenTextInput.value.trim();
      if (!val) return;
      this.screenTextInput.value = '';
      this.handleUserUtterance(val);
    });

    this.screenTextInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const val = this.screenTextInput.value.trim();
        if (!val) return;
        this.screenTextInput.value = '';
        this.handleUserUtterance(val);
      }
    });

    this.voiceActivityPill.addEventListener('click', () => this.toggleListening());

    // Nutrition Drawer Toggle
    this.toggleMacroDrawerBtn.addEventListener('click', () => {
      if (this.macroSlideDrawer.classList.contains('active-drawer')) {
        this.closeMacroDrawer();
      } else {
        this.openMacroDrawer();
      }
    });
    this.closeMacroDrawerBtn.addEventListener('click', () => this.closeMacroDrawer());

    // Custom Recipe Modal
    this.customRecipeOpenBtn?.addEventListener('click', () => this.openCustomRecipeModal());
    this.modalCloseBtn?.addEventListener('click', () => this.closeCustomRecipeModal());
    this.btnCancelModal?.addEventListener('click', () => this.closeCustomRecipeModal());
    this.modalBackdrop?.addEventListener('click', () => this.closeCustomRecipeModal());

    this.customRecipeForm?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('recipe-title-input').value.trim();
      const prepMinutes = parseInt(document.getElementById('recipe-prep-time').value, 10) || 15;
      const servings = parseInt(document.getElementById('recipe-servings').value, 10) || 2;
      const rawIngs = document.getElementById('recipe-ingredients-input').value.trim();

      if (!title || !rawIngs) return;

      const ingredients = rawIngs.split(',').map(s => {
        const clean = s.trim();
        return { item: clean, qty: 1, unit: 'serving' };
      }).filter(i => i.item.length > 0);

      const newRecipe = {
        name: title,
        prep_minutes: prepMinutes,
        servings: servings,
        ingredients: ingredients,
        steps: [
          { instruction: "Prepare and inspect all ingredients.", timer_seconds: 0 },
          { instruction: "Cook ingredients thoroughly according to preference.", timer_seconds: 300 },
          { instruction: "Plate nicely, season to taste, and serve hot!", timer_seconds: 0 }
        ]
      };

      try {
        const res = await fetch('/api/recipes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newRecipe)
        });
        if (res.ok) {
          this.closeCustomRecipeModal();
          this.customRecipeForm.reset();
          await this.fetchRecipes();
          this.showToast(`Saved "${title}" to your cookbook!`);
          this.voiceEngine.speak(`Saved ${title} to your family cookbook!`);
        }
      } catch (err) {
        console.error(err);
      }
    });

    // Emergency Alert Confirm
    this.alertRemedyConfirmBtn.addEventListener('click', () => {
      this.emergencyAlertSheet.classList.add('hidden');
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

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') {
        if (e.key === 'Escape') {
          document.activeElement.blur();
          this.closeMacroDrawer();
          this.closeCustomRecipeModal();
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
        this.screenTextInput.focus();
      } else if (e.key === 'Escape') {
        this.closeMacroDrawer();
        this.closeCustomRecipeModal();
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
