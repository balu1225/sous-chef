// Sous-Chef Web Voice Companion Client

class SousChefVoiceApp {
  constructor() {
    this.orb = document.getElementById('voice-orb');
    this.voiceStateLabel = document.getElementById('voice-state');
    this.transcriptBox = document.getElementById('transcript-box');
    this.micBtn = document.getElementById('mic-btn');
    this.chatForm = document.getElementById('chat-form');
    this.textInput = document.getElementById('text-input');
    this.latencyMetric = document.getElementById('latency-metric');
    this.inventoryGrid = document.getElementById('inventory-grid');
    this.refreshBtn = document.getElementById('refresh-inventory-btn');
    this.countAll = document.getElementById('count-all');
    this.countExpiring = document.getElementById('count-expiring');

    this.isListening = false;
    this.recognition = null;
    this.inventoryItems = [];
    this.activeFilter = 'all';

    this.initSpeechRecognition();
    this.initEventListeners();
    this.fetchInventory();
  }

  // 1. Web Speech API (STT & TTS)
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
      };

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.handleUserUtterance(transcript);
      };

      this.recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        this.stopListening();
      };

      this.recognition.onend = () => {
        this.stopListening();
      };
    } else {
      console.warn('Web Speech API not supported in this browser. Fallback to text input active.');
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
    if (!this.isSpeaking) {
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
    }
  }

  speak(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    this.isSpeaking = true;
    this.setVoiceState('speaking', 'Sous-Chef is speaking...');
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    utterance.onend = () => {
      this.isSpeaking = false;
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
    };

    window.speechSynthesis.speak(utterance);
  }

  setVoiceState(state, label) {
    this.orb.className = 'voice-orb ' + state;
    this.voiceStateLabel.textContent = label;
  }

  // 2. Transcript & Chat Flow
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

  async handleUserUtterance(text) {
    if (!text || !text.trim()) return;
    const utterance = text.trim();
    this.appendTranscript('user', utterance);
    this.setVoiceState('thinking', 'Processing kitchen command...');

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
      
      this.appendTranscript('assistant', reply);
      this.speak(reply);

      // Refresh inventory display
      await this.fetchInventory();

    } catch (err) {
      console.error(err);
      const fallbackMsg = "Sorry, I had trouble reaching the kitchen server. Please try again.";
      this.appendTranscript('assistant', fallbackMsg);
      this.speak(fallbackMsg);
      this.setVoiceState('idle', 'Tap Mic or Type to Speak');
    }
  }

  // 3. Inventory Loading & Rendering
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

  initEventListeners() {
    this.micBtn.addEventListener('click', () => this.toggleListening());

    this.chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = this.textInput.value;
      this.textInput.value = '';
      this.handleUserUtterance(val);
    });

    this.refreshBtn.addEventListener('click', () => this.fetchInventory());

    document.querySelectorAll('.filter-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        this.activeFilter = e.target.dataset.filter;
        this.renderInventory();
      });
    });

    document.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const phrase = chip.dataset.phrase;
        this.handleUserUtterance(phrase);
      });
    });
  }
}

// Helpers
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
