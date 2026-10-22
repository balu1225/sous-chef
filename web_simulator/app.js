// Sous-Chef Web Voice Companion Client with Lo-Fi Ambience & Guided Cooking Station

// ==========================================================================
// 1. Web Audio API Lo-Fi Ambience & Sound Effects Engine
// ==========================================================================
class CookingMusicEngine {
  constructor() {
    this.ctx = null;
    this.isPlaying = false;
    this.wasPlayingBeforeTimer = false;
    this.gainNode = null;
    this.intervalId = null;
    this.masterVolume = 0.25;
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

    // Relaxing Lo-Fi Kitchen Chord Progression (Fmaj7 -> Em7 -> Dm7 -> Cmaj7)
    const chords = [
      [174.61, 220.00, 261.63, 329.63], // Fmaj7 (F3, A3, C4, E4)
      [164.81, 196.00, 246.94, 293.66], // Em7 (E3, G3, B3, D4)
      [146.83, 174.61, 220.00, 261.63], // Dm7 (D3, F3, A3, C4)
      [130.81, 164.81, 196.00, 246.94]  // Cmaj7 (C3, E3, G3, B3)
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
        osc.type = 'triangle'; // Warm Rhodes / vibraphone tone
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);

        // Soft attack, gentle decay
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
    // Pleasant 3-tone chime: A5 (880Hz), D6 (1174Hz), A6 (1760Hz)
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
    osc.frequency.setValueAtTime(659.25, now); // E5
    osc.frequency.exponentialRampToValueAtTime(1318.51, now + 0.08); // E6
    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);

    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(now);
    osc.stop(now + 0.24);
  }

  updateUI() {
    const pill = document.getElementById('music-pill');
    const label = document.getElementById('music-btn-label');
    if (pill && label) {
      if (this.isPlaying) {
        pill.classList.add('playing');
        label.textContent = 'Ambience: Playing';
      } else {
        pill.classList.remove('playing');
        label.textContent = 'Ambience: Off';
      }
    }
  }
}

// ==========================================================================
// 2. Main Sous-Chef Application
// ==========================================================================
class SousChefVoiceApp {
  constructor() {
    // DOM Elements
    this.orb = document.getElementById('voice-orb');
    this.voiceStateLabel = document.getElementById('voice-state');
    this.transcriptBox = document.getElementById('transcript-box');
    this.micBtn = document.getElementById('mic-btn');
    this.chatForm = document.getElementById('chat-form');
    this.textInput = document.getElementById('text-input');
    this.latencyMetric = document.getElementById('latency-metric');
    
    // Inventory
    this.inventoryGrid = document.getElementById('inventory-grid');
    this.refreshBtn = document.getElementById('refresh-inventory-btn');
    this.countAll = document.getElementById('count-all');
    this.countExpiring = document.getElementById('count-expiring');
    this.todayKcal = document.getElementById('today-kcal');
    this.todayProtein = document.getElementById('today-protein');

    // Cooking Station DOM Elements
    this.tabInventory = document.getElementById('tab-inventory');
    this.tabCooking = document.getElementById('tab-cooking');
    this.viewInventory = document.getElementById('view-inventory');
    this.viewCooking = document.getElementById('view-cooking');
    this.cookingActiveDot = document.getElementById('cooking-active-dot');
    this.cookingEmptyState = document.getElementById('cooking-empty-state');
    this.cookingActiveContainer = document.getElementById('cooking-active-container');
    this.recipeStarterList = document.getElementById('recipe-starter-list');
    
    // Recipe View Controls
    this.recipeTitle = document.getElementById('recipe-title');
    this.recipeDesc = document.getElementById('recipe-desc');
    this.recipeBadgeTime = document.getElementById('recipe-badge-time');
    this.recipeBadgeServings = document.getElementById('recipe-badge-servings');
    this.recipeBadgeKcal = document.getElementById('recipe-badge-kcal');
    this.exitCookingBtn = document.getElementById('exit-cooking-btn');

    // Prep Checklist
    this.prepCounter = document.getElementById('prep-counter');
    this.prepItemsList = document.getElementById('prep-items-list');

    // Step View
    this.stepIndexBadge = document.getElementById('step-index-badge');
    this.stepTimerIndicator = document.getElementById('step-timer-indicator');
    this.stepText = document.getElementById('step-text');
    this.stepTipBox = document.getElementById('step-tip-box');
    this.stepTipText = document.getElementById('step-tip-text');
    this.stepTimerSection = document.getElementById('step-timer-section');
    this.timerClockDisplay = document.getElementById('timer-clock-display');
    this.timerStartBtn = document.getElementById('timer-start-btn');
    this.timerPauseBtn = document.getElementById('timer-pause-btn');
    this.timerResetBtn = document.getElementById('timer-reset-btn');
    this.prevStepBtn = document.getElementById('prev-step-btn');
    this.nextStepBtn = document.getElementById('next-step-btn');
    this.finishCookingBtn = document.getElementById('finish-cooking-btn');

    // Timer Alert Modal
    this.timerAlertOverlay = document.getElementById('timer-alert-overlay');
    this.alertMessage = document.getElementById('alert-message');
    this.alertConfirmBtn = document.getElementById('alert-confirm-btn');
    this.alertAddTimeBtn = document.getElementById('alert-add-time-btn');

    // Custom Recipe Modal Elements
    this.customRecipeModal = document.getElementById('custom-recipe-modal');
    this.openCustomRecipeBtn = document.getElementById('open-custom-recipe-btn');
    this.saveActiveRecipeBtn = document.getElementById('save-active-recipe-btn');
    this.closeRecipeModalBtn = document.getElementById('close-recipe-modal-btn');
    this.cancelRecipeModalBtn = document.getElementById('cancel-recipe-modal-btn');
    this.customRecipeForm = document.getElementById('custom-recipe-form');
    this.modalRecipeName = document.getElementById('modal-recipe-name');
    this.modalPrepMin = document.getElementById('modal-prep-min');
    this.modalServings = document.getElementById('modal-servings');
    this.modalIngredients = document.getElementById('modal-ingredients');

    // Music Elements
    this.musicBtn = document.getElementById('music-btn');
    this.musicVol = document.getElementById('music-vol');

    // State Variables
    this.isListening = false;
    this.isSpeaking = false;
    this.recognition = null;
    this.inventoryItems = [];
    this.activeFilter = 'all';
    this.allRecipes = [];
    this.activeCooking = null;
    this.selectedFemaleVoice = null;

    // Timer State
    this.stepTimerSeconds = 0;
    this.stepTimerInitial = 0;
    this.stepTimerInterval = null;
    this.isTimerRunning = false;

    // Music Engine
    this.musicEngine = new CookingMusicEngine();

    // Initialization
    this.initVoices();
    this.initSpeechRecognition();
    this.initEventListeners();
    this.fetchInventory();
    this.fetchNutrition();
    this.fetchCookingState();
    this.fetchRecipes();
  }

  // ------------------------------------------------------------------------
  // Natural Female Voice Selection
  // ------------------------------------------------------------------------
  initVoices() {
    if (!('speechSynthesis' in window)) return;
    const findVoice = () => {
      const voices = window.speechSynthesis.getVoices();
      if (!voices || voices.length === 0) return;
      // Preference: Natural female English voices
      const preferred = ["Samantha", "Victoria", "Google US English", "Karen", "Zira", "en-US-Standard-C", "Moira"];
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
  // Web Speech API: STT & TTS
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
        this.setVoiceState('listening', 'Listening for your voice...');
        this.micBtn.classList.add('active');
        this.musicEngine.duck(0.2);
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.handleUserUtterance(transcript);
      };

      this.recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        this.stopListening();
        this.musicEngine.unduck(0.3);
      };

      this.recognition.onend = () => {
        this.stopListening();
        this.musicEngine.unduck(0.3);
      };
    }
  }

  toggleListening() {
    if (!this.recognition) {
      this.appendTranscript('assistant', 'Speech recognition is not supported in this browser. Please type your message below.');
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
    this.micBtn.classList.remove('active');
    if (!this.isSpeaking && !this.timerAlertOverlay.classList.contains('hidden') === false) {
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
    }
  }

  speak(text, onComplete = null) {
    if (!('speechSynthesis' in window)) {
      if (onComplete) onComplete();
      return;
    }
    window.speechSynthesis.cancel();

    this.isSpeaking = true;
    this.setVoiceState('speaking', 'Sous-Chef is speaking...');
    this.musicEngine.duck(0.2);

    const utterance = new SpeechSynthesisUtterance(text);
    if (this.selectedFemaleVoice) {
      utterance.voice = this.selectedFemaleVoice;
    }
    utterance.rate = 1.04;
    utterance.pitch = 1.02;

    const cleanup = () => {
      this.isSpeaking = false;
      this.musicEngine.unduck(0.4);
      if (this.timerAlertOverlay.classList.contains('hidden')) {
        this.setVoiceState('idle', 'Tap Mic or Type to Speak');
      } else {
        this.setVoiceState('timer-alert', "Timer's up! Check your food!");
      }
      if (onComplete) onComplete();
    };

    utterance.onend = cleanup;
    utterance.onerror = cleanup;

    window.speechSynthesis.speak(utterance);
  }

  setVoiceState(state, label) {
    this.orb.className = 'voice-orb ' + state;
    this.voiceStateLabel.textContent = label;
  }

  appendTranscript(role, text) {
    const entry = document.createElement('div');
    entry.className = `transcript-entry ${role}`;
    
    const tag = document.createElement('span');
    tag.className = 'speaker-tag';
    tag.textContent = role === 'user' ? 'You' : 'Sous-Chef';

    const p = document.createElement('p');
    p.textContent = text;

    entry.appendChild(tag);
    entry.appendChild(p);
    this.transcriptBox.appendChild(entry);
    this.transcriptBox.scrollTop = this.transcriptBox.scrollHeight;
  }

  appendRemedyTranscript(remedy) {
    const entry = document.createElement('div');
    entry.className = 'transcript-entry assistant remedy-entry';

    const stepsList = (remedy.remedy_steps || [])
      .map((step, idx) => `<li><span class="step-num">${idx + 1}</span> <span>${escapeHtml(step)}</span></li>`)
      .join('');

    entry.innerHTML = `
      <div class="remedy-badge-row">
        <span class="speaker-tag">Sous-Chef</span>
        <span class="remedy-category-pill">🆘 ${escapeHtml(remedy.category)}</span>
      </div>
      <p class="remedy-quip"><em>"${escapeHtml(remedy.quip)}"</em></p>
      <div class="remedy-steps-card">
        <div class="remedy-card-title">👨‍🍳 Kitchen Rescue Plan:</div>
        <ul class="remedy-step-bullets">
          ${stepsList}
        </ul>
      </div>
      <div class="remedy-pro-tip">
        <strong>💡 Pro Tip:</strong> ${escapeHtml(remedy.pro_tip)}
      </div>
    `;

    this.transcriptBox.appendChild(entry);
    this.transcriptBox.scrollTop = this.transcriptBox.scrollHeight;
  }

  // ------------------------------------------------------------------------
  // Conversational API Dispatcher
  // ------------------------------------------------------------------------
  async handleUserUtterance(text) {
    if (!text || !text.trim()) return;
    const utterance = text.trim();
    this.appendTranscript('user', utterance);
    this.setVoiceState('thinking', 'Processing kitchen command...');

    // Check if user is confirming an active timer alert by voice!
    const clean = utterance.toLowerCase();
    const isAlertActive = !this.timerAlertOverlay.classList.contains('hidden');

    if (isAlertActive && (
      clean.includes('stove') || clean.includes('done') || clean.includes('stopped') ||
      clean.includes('off') || clean.includes('mix') || clean.includes('stir') ||
      clean.includes('check') || clean.includes('continue')
    )) {
      this.confirmTimerAction();
      return;
    }

    const start = performance.now();
    try {
      const response = await fetch('/api/converse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ utterance })
      });

      const elapsed = Math.round(performance.now() - start);
      this.latencyMetric.textContent = `${elapsed} ms`;

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const reply = data.spoken_message || data.message || "I've updated your kitchen.";

      // Handle music command returned from voice
      if (data.music_command === 'play') {
        this.musicEngine.play();
      } else if (data.music_command === 'stop') {
        this.musicEngine.stop();
      }

      // Handle timer command returned from voice
      if (data.timer_command === 'start') {
        this.startStepTimer();
      } else if (data.timer_command === 'stop') {
        this.pauseStepTimer();
      }

      // Handle action confirmation return
      if (data.action_confirmed) {
        this.timerAlertOverlay.classList.add('hidden');
        if (data.resume_music && this.musicEngine.wasPlayingBeforeTimer) {
          this.musicEngine.play();
        }
      }

      // Update active cooking state if returned
      if (data.active_cooking !== undefined) {
        this.activeCooking = data.active_cooking;
        this.renderCookingStation();
        if (this.activeCooking) {
          this.switchView('cooking');
        }
      }

      if (data.remedy) {
        this.appendRemedyTranscript(data.remedy);
      } else {
        this.appendTranscript('assistant', reply);
      }
      this.speak(reply);

      // Refresh inventory & nutrition
      await this.fetchInventory();
      await this.fetchNutrition();

    } catch (err) {
      console.error(err);
      const fallbackMsg = "Sorry, I had trouble reaching the kitchen server. Please try again.";
      this.appendTranscript('assistant', fallbackMsg);
      this.speak(fallbackMsg);
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
    }
  }

  // ------------------------------------------------------------------------
  // Guided Cooking Station & Step Timer
  // ------------------------------------------------------------------------
  async fetchCookingState() {
    try {
      const res = await fetch('/api/cooking');
      if (res.ok) {
        const data = await res.json();
        this.activeCooking = data.active_cooking;
        this.renderCookingStation();
      }
    } catch (err) {
      console.warn('Could not fetch cooking state:', err);
    }
  }

  async fetchRecipes() {
    try {
      const res = await fetch('/api/recipes');
      if (res.ok) {
        const data = await res.json();
        this.allRecipes = data.recipes || [];
        this.renderRecipeStarters();
      }
    } catch (err) {
      console.warn('Could not fetch recipes:', err);
    }
  }

  renderRecipeStarters() {
    this.recipeStarterList.innerHTML = '';
    const topStarters = this.allRecipes.slice(0, 6);
    topStarters.forEach(rec => {
      const card = document.createElement('div');
      card.className = 'recipe-start-card';
      const customTag = (rec.tags && rec.tags.includes('custom')) ? '<span class="custom-recipe-tag">Family</span>' : '';
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="recipe-start-name">${escapeHtml(rec.name)}</span>
          ${customTag}
        </div>
        <div class="recipe-start-meta">
          <span>⏱️ ${rec.prep_minutes} min</span>
          <span>🍽️ ${rec.servings} serv</span>
          <span>🔥 ~${Math.round(rec.kcal_per_serving || 300)} kcal</span>
        </div>
      `;
      card.addEventListener('click', () => {
        this.startRecipe(rec.id);
      });
      this.recipeStarterList.appendChild(card);
    });
  }

  openRecipeModal(prefill = null) {
    if (!this.customRecipeModal) return;
    this.customRecipeModal.classList.remove('hidden');
    if (prefill) {
      if (prefill.name) this.modalRecipeName.value = prefill.name;
      if (prefill.prep_minutes) this.modalPrepMin.value = prefill.prep_minutes;
      if (prefill.servings) this.modalServings.value = prefill.servings;
      if (prefill.ingredients) {
        if (Array.isArray(prefill.ingredients)) {
          this.modalIngredients.value = prefill.ingredients
            .map(i => `${i.qty || ''} ${i.unit || ''} ${i.item || ''}`.trim())
            .join(', ');
        } else {
          this.modalIngredients.value = prefill.ingredients;
        }
      }
    } else if (this.activeCooking && this.activeCooking.recipe) {
      const r = this.activeCooking.recipe;
      this.modalRecipeName.value = `${r.name} (Custom)`;
      this.modalPrepMin.value = r.prep_minutes || 15;
      this.modalServings.value = this.activeCooking.servings || r.servings || 2;
      this.modalIngredients.value = (r.ingredients || [])
        .map(i => `${i.qty || ''} ${i.unit || ''} ${i.item || ''}`.trim())
        .join(', ');
    } else {
      this.modalRecipeName.value = '';
      this.modalPrepMin.value = 15;
      this.modalServings.value = 2;
      this.modalIngredients.value = '';
    }
    this.modalRecipeName.focus();
  }

  closeRecipeModal() {
    if (this.customRecipeModal) {
      this.customRecipeModal.classList.add('hidden');
    }
  }

  async handleSaveCustomRecipe(e) {
    e.preventDefault();
    const name = this.modalRecipeName.value.trim();
    if (!name) return;
    const prep_minutes = parseInt(this.modalPrepMin.value) || 15;
    const servings = parseFloat(this.modalServings.value) || 2.0;
    const ingredients = this.modalIngredients.value.trim();

    try {
      const res = await fetch('/api/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          prep_minutes,
          servings,
          ingredients
        })
      });
      if (res.ok) {
        const data = await res.json();
        const saved = data.recipe;
        this.closeRecipeModal();
        const msg = `Saved your custom family recipe for ${saved.name}! Approximately ${Math.round(saved.kcal_per_serving)} calories and ${Math.round(saved.protein_per_serving)}g protein per serving.`;
        this.appendTranscript('assistant', msg);
        this.speak(msg);
        await this.fetchRecipes();
      } else {
        const err = await res.json();
        alert('Could not save recipe: ' + (err.error || 'Server error'));
      }
    } catch (err) {
      console.error('Save recipe failed:', err);
    }
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
        this.renderCookingStation();
        this.switchView('cooking');
        const startMsg = `Starting ${this.activeCooking.recipe.name}! I've turned on some cooking music for you. First, check off your ingredients or say 'Next step' when ready!`;
        this.appendTranscript('assistant', startMsg);
        this.speak(startMsg);
        // Start cooking music
        this.musicEngine.play();
      }
    } catch (err) {
      console.error(err);
    }
  }

  async stopCooking() {
    try {
      this.pauseStepTimer();
      await fetch('/api/cooking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'stop' })
      });
      this.activeCooking = null;
      this.renderCookingStation();
      this.switchView('inventory');
      const stopMsg = "Cancelled cooking mode. Returned to kitchen inventory.";
      this.appendTranscript('assistant', stopMsg);
      this.speak(stopMsg);
    } catch (err) {
      console.error(err);
    }
  }

  renderCookingStation() {
    if (!this.activeCooking) {
      this.cookingEmptyState.classList.remove('hidden');
      this.cookingActiveContainer.classList.add('hidden');
      this.tabCooking.classList.remove('has-active-recipe');
      this.pauseStepTimer();
      return;
    }

    const { recipe, step, checked_prep, servings } = this.activeCooking;
    this.cookingEmptyState.classList.add('hidden');
    this.cookingActiveContainer.classList.remove('hidden');
    this.tabCooking.classList.add('has-active-recipe');

    // 1. Recipe Header
    this.recipeTitle.textContent = recipe.name;
    this.recipeDesc.textContent = recipe.description || "Fresh home-cooked meal.";
    this.recipeBadgeTime.textContent = `⏱️ ${recipe.prep_minutes || 15} min`;
    this.recipeBadgeServings.textContent = `🍽️ ${servings || recipe.servings} servings`;
    this.recipeBadgeKcal.textContent = `🔥 ~${Math.round(recipe.kcal_per_serving || 320)} kcal`;

    // 2. Ingredient Prep Checklist
    this.prepItemsList.innerHTML = '';
    const ingredients = recipe.ingredients || [];
    let checkedCount = 0;

    ingredients.forEach(ing => {
      const isChecked = (checked_prep || []).includes(ing.item);
      if (isChecked) checkedCount++;

      const row = document.createElement('div');
      row.className = `prep-item-row ${isChecked ? 'checked' : ''}`;
      row.innerHTML = `
        <div class="prep-check-box">${isChecked ? '✓' : ''}</div>
        <div class="prep-item-info">
          <span class="prep-item-name">${escapeHtml(ing.item)}</span>
          <span class="prep-item-qty">${formatDisplayQty(ing.qty, ing.unit)}</span>
        </div>
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

      this.prepItemsList.appendChild(row);
    });

    this.prepCounter.textContent = `${checkedCount} / ${ingredients.length} ready`;

    // 3. Step Viewer
    const steps = recipe.steps || [];
    const totalSteps = steps.length || 1;
    const currentStepIdx = Math.max(1, Math.min(step || 1, totalSteps));
    const stepObj = steps[currentStepIdx - 1] || { instruction: "Cook your ingredients." };

    this.stepIndexBadge.textContent = `STEP ${currentStepIdx} OF ${totalSteps}`;
    this.stepText.textContent = stepObj.instruction || '';

    if (stepObj.tip) {
      this.stepTipBox.style.display = 'flex';
      this.stepTipText.textContent = stepObj.tip;
    } else {
      this.stepTipBox.style.display = 'none';
    }

    // 4. Timer Section
    if (stepObj.timer_seconds && stepObj.timer_seconds > 0) {
      this.stepTimerSection.classList.remove('hidden');
      this.stepTimerIndicator.textContent = `⏱️ ${Math.round(stepObj.timer_seconds / 60)} min timer`;
      if (!this.isTimerRunning) {
        this.stepTimerInitial = stepObj.timer_seconds;
        this.stepTimerSeconds = stepObj.timer_seconds;
        this.updateTimerDisplay();
      }
    } else {
      this.stepTimerSection.classList.add('hidden');
      this.stepTimerIndicator.textContent = '⏱️ Untimed step';
      this.pauseStepTimer();
    }

    // Navigation buttons
    this.prevStepBtn.disabled = (currentStepIdx <= 1);
    this.nextStepBtn.style.display = (currentStepIdx < totalSteps) ? 'block' : 'none';
    this.finishCookingBtn.classList.toggle('visible', currentStepIdx >= totalSteps);
  }

  // ------------------------------------------------------------------------
  // Step Timer Engine & Music Ducking
  // ------------------------------------------------------------------------
  startStepTimer() {
    if (this.isTimerRunning) return;
    this.isTimerRunning = true;
    this.timerStartBtn.textContent = '▶ Running...';

    // Remember if music was playing so we know to resume after alert confirmation
    this.musicEngine.wasPlayingBeforeTimer = this.musicEngine.isPlaying;
    if (!this.musicEngine.isPlaying) {
      this.musicEngine.play();
    }

    this.stepTimerInterval = setInterval(() => {
      if (this.stepTimerSeconds > 0) {
        this.stepTimerSeconds--;
        this.updateTimerDisplay();
      } else {
        this.handleTimerFinished();
      }
    }, 1000);
  }

  pauseStepTimer() {
    this.isTimerRunning = false;
    if (this.stepTimerInterval) {
      clearInterval(this.stepTimerInterval);
      this.stepTimerInterval = null;
    }
    this.timerStartBtn.textContent = '▶ Start Timer';
  }

  resetStepTimer() {
    this.pauseStepTimer();
    this.stepTimerSeconds = this.stepTimerInitial;
    this.updateTimerDisplay();
  }

  updateTimerDisplay() {
    const mins = Math.floor(this.stepTimerSeconds / 60);
    const secs = this.stepTimerSeconds % 60;
    this.timerClockDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  handleTimerFinished() {
    this.pauseStepTimer();

    // 1. Immediately Stop Background Music!
    this.musicEngine.stop(0.2);

    // 2. Play 3-tone Kitchen Timer Chime
    this.musicEngine.playTimerChime();

    // 3. Set Voice Orb to Timer-Alert state
    this.setVoiceState('timer-alert', "Timer's up! Check your food!");

    // 4. Determine alert instruction from recipe step
    let alertMsg = "Time's up! Turn down the stove now, give it a good mix, and check if it's cooked.";
    if (this.activeCooking && this.activeCooking.recipe) {
      const steps = this.activeCooking.recipe.steps || [];
      const curr = steps[this.activeCooking.step - 1];
      if (curr && curr.timer_alert) {
        alertMsg = curr.timer_alert;
      }
    }

    this.alertMessage.textContent = alertMsg;
    this.timerAlertOverlay.classList.remove('hidden');

    // 5. Proactively Speak Action Alert with Natural Female Voice
    const spokenAlert = `Ding! Timer's up! Turn off the stove, give it a good mix, and check your food. Let me know once you're done!`;
    this.appendTranscript('assistant', spokenAlert);
    this.speak(spokenAlert);
  }

  async confirmTimerAction() {
    // 1. Hide Alert Overlay & restore voice orb
    this.timerAlertOverlay.classList.add('hidden');
    this.setVoiceState('idle', 'Tap Mic or Type to Speak');

    // 2. Advance Step via backend
    try {
      const res = await fetch('/api/cooking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'confirm_action' })
      });
      if (res.ok) {
        const data = await res.json();
        this.activeCooking = data.active_cooking;
        this.renderCookingStation();
      }
    } catch (err) {
      console.error(err);
    }

    // 3. Spoken Confirmation & Transition Back
    const ackMsg = "Awesome, stove is turned off and food is checked! Going back to your cooking flow.";
    this.appendTranscript('assistant', ackMsg);
    this.speak(ackMsg, () => {
      // 4. Resume Music if it was playing before the timer!
      if (this.musicEngine.wasPlayingBeforeTimer) {
        this.musicEngine.play();
      }
    });
  }

  // ------------------------------------------------------------------------
  // View Switcher & Inventory Management
  // ------------------------------------------------------------------------
  switchView(viewName) {
    if (viewName === 'cooking') {
      this.tabCooking.classList.add('active');
      this.tabInventory.classList.remove('active');
      this.viewCooking.classList.remove('hidden');
      this.viewInventory.classList.add('hidden');
    } else {
      this.tabInventory.classList.add('active');
      this.tabCooking.classList.remove('active');
      this.viewInventory.classList.remove('hidden');
      this.viewCooking.classList.add('hidden');
    }
  }

  async fetchInventory() {
    const start = performance.now();
    try {
      const response = await fetch('/api/inventory');
      if (response.ok) {
        const data = await response.json();
        this.inventoryItems = data.items || [];
        this.renderInventory();
        const elapsed = Math.round(performance.now() - start);
        if (this.latencyMetric.textContent === '-- ms') {
          this.latencyMetric.textContent = `${elapsed} ms`;
        }
      }
    } catch (err) {
      console.warn('Could not fetch inventory:', err);
    }
  }

  async fetchNutrition() {
    try {
      const res = await fetch('/api/nutrition');
      if (res.ok) {
        const data = await res.json();
        if (this.todayKcal) this.todayKcal.textContent = Math.round(data.total_kcal || 0);
        if (this.todayProtein) this.todayProtein.textContent = `${Math.round(data.total_protein_g || 0)}g`;
      }
    } catch (err) {
      console.warn('Could not fetch nutrition:', err);
    }
  }

  renderInventory() {
    this.inventoryGrid.innerHTML = '';
    const now = new Date();
    const urgentCutoff = new Date(now.getTime() + 48 * 60 * 60 * 1000); // 48h
    const warningCutoff = new Date(now.getTime() + 5 * 24 * 60 * 60 * 1000); // 5 days

    let expiringCount = 0;

    const itemsToDisplay = this.inventoryItems.filter(item => {
      let isExpiring = false;
      if (item.expires_at) {
        const exp = new Date(item.expires_at);
        if (exp <= urgentCutoff) {
          expiringCount++;
          isExpiring = true;
        }
      }
      return this.activeFilter === 'expiring' ? isExpiring : true;
    });

    this.countAll.textContent = this.inventoryItems.length;
    this.countExpiring.textContent = expiringCount;

    if (itemsToDisplay.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'empty-state';
      empty.innerHTML = `<p>${this.activeFilter === 'expiring' ? 'No items expiring within 48 hours!' : 'Your pantry and fridge are empty. Add something by voice!'}</p>`;
      this.inventoryGrid.appendChild(empty);
      return;
    }

    itemsToDisplay.forEach(item => {
      const card = document.createElement('div');
      card.className = 'item-card';

      let expiryBadge = '';
      if (item.expires_at) {
        const exp = new Date(item.expires_at);
        if (exp <= urgentCutoff) {
          card.classList.add('urgent');
          expiryBadge = `<span class="expiry-badge urgent">Expires in <48h</span>`;
        } else if (exp <= warningCutoff) {
          expiryBadge = `<span class="expiry-badge warning">Expires in <5d</span>`;
        } else {
          expiryBadge = `<span class="expiry-badge good">Good</span>`;
        }
      }

      card.innerHTML = `
        <div class="item-name">${escapeHtml(item.item)}</div>
        <div class="item-qty">${formatDisplayQty(item.qty, item.unit)}</div>
        <div class="item-zone">${escapeHtml(item.zone || 'Pantry')}</div>
        ${expiryBadge}
      `;
      this.inventoryGrid.appendChild(card);
    });
  }

  // ------------------------------------------------------------------------
  // Event Listeners
  // ------------------------------------------------------------------------
  initEventListeners() {
    this.micBtn.addEventListener('click', () => this.toggleListening());

    this.chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = this.textInput.value;
      this.textInput.value = '';
      this.handleUserUtterance(val);
    });

    this.refreshBtn.addEventListener('click', () => this.fetchInventory());

    // Navigation Tabs
    this.tabInventory.addEventListener('click', () => this.switchView('inventory'));
    this.tabCooking.addEventListener('click', () => this.switchView('cooking'));

    // Ambience Music Controls
    this.musicBtn.addEventListener('click', () => {
      if (this.musicEngine.isPlaying) {
        this.musicEngine.stop();
      } else {
        this.musicEngine.play();
      }
    });

    this.musicVol.addEventListener('input', (e) => {
      this.musicEngine.setVolume(Number(e.target.value) / 100);
    });

    // Step Timer Buttons
    this.timerStartBtn.addEventListener('click', () => {
      if (this.isTimerRunning) {
        this.pauseStepTimer();
      } else {
        this.startStepTimer();
      }
    });
    this.timerPauseBtn.addEventListener('click', () => this.pauseStepTimer());
    this.timerResetBtn.addEventListener('click', () => this.resetStepTimer());

    // Cooking Navigation Buttons
    this.prevStepBtn.addEventListener('click', async () => {
      this.pauseStepTimer();
      const res = await fetch('/api/cooking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'prev_step' })
      });
      if (res.ok) {
        const data = await res.json();
        this.activeCooking = data.active_cooking;
        this.renderCookingStation();
      }
    });

    this.nextStepBtn.addEventListener('click', async () => {
      this.pauseStepTimer();
      const res = await fetch('/api/cooking', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'next_step' })
      });
      if (res.ok) {
        const data = await res.json();
        this.activeCooking = data.active_cooking;
        this.renderCookingStation();
      }
    });

    this.finishCookingBtn.addEventListener('click', () => {
      this.handleUserUtterance("I finished cooking, deduct my ingredients and log meal");
    });

    this.exitCookingBtn.addEventListener('click', () => this.stopCooking());

    // Custom Recipe Modal Listeners
    if (this.openCustomRecipeBtn) {
      this.openCustomRecipeBtn.addEventListener('click', () => this.openRecipeModal());
    }
    if (this.saveActiveRecipeBtn) {
      this.saveActiveRecipeBtn.addEventListener('click', () => this.openRecipeModal());
    }
    if (this.closeRecipeModalBtn) {
      this.closeRecipeModalBtn.addEventListener('click', () => this.closeRecipeModal());
    }
    if (this.cancelRecipeModalBtn) {
      this.cancelRecipeModalBtn.addEventListener('click', () => this.closeRecipeModal());
    }
    if (this.customRecipeForm) {
      this.customRecipeForm.addEventListener('submit', (e) => this.handleSaveCustomRecipe(e));
    }

    // Timer Alert Modal Buttons
    this.alertConfirmBtn.addEventListener('click', () => this.confirmTimerAction());
    this.alertAddTimeBtn.addEventListener('click', () => {
      this.timerAlertOverlay.classList.add('hidden');
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
      this.stepTimerSeconds = 60;
      this.updateTimerDisplay();
      this.startStepTimer();
      this.musicEngine.play();
    });

    // Filter Chips
    document.querySelectorAll('.filter-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        this.activeFilter = e.target.dataset.filter;
        this.renderInventory();
      });
    });

    // Quick Phrases
    document.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const phrase = chip.dataset.phrase;
        this.handleUserUtterance(phrase);
      });
    });
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
  return `${qty % 1 === 0 ? Math.round(qty) : qty} ${unit}`;
}

document.addEventListener('DOMContentLoaded', () => {
  window.app = new SousChefVoiceApp();
});
