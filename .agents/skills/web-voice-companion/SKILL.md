---
name: web-voice-companion
description: UI/UX, Web Speech API, animated voice visualizer, and live MCP connectivity standards for the Sous-Chef web simulator.
---

# Web Voice Companion Engineering Standard

## 1. Aesthetic & UI Architecture
- **Location:** `web_simulator/index.html`, `web_simulator/app.js`, `web_simulator/style.css`.
- **Design Tokens:** Modern, glassmorphic dark kitchen theme.
  - Background: Deep slate/obsidian (`#0b0f19`) with subtle radial gradients.
  - Cards: Semi-transparent glass (`rgba(255, 255, 255, 0.05)`, `backdrop-filter: blur(12px)`).
  - Accent: Alexa cyan (`#00cae0`) and kitchen warm amber (`#f59e0b`).
  - Typography: System sans-serif (`Inter`, `-apple-system`, `BlinkMacSystemFont`).
- **Zero Heavy Frameworks:** Pure Vanilla HTML5, CSS3, and JavaScript (ES6+). Zero build steps or npm bundling required for instant local testing.

## 2. Animated Voice Orb (Alexa-Style State Indicator)
The central visual element is a dynamic, pulsating glowing orb with distinct visual states:
- **Idle:** Soft breathing blue pulse (`#0077b6`).
- **Listening:** Active expanding cyan rings with audio sensitivity (`#00cae0`).
- **Thinking / Processing:** Fast gradient rotation or orbital spinner (`#6366f1`).
- **Speaking:** Fluid warm wave pulse (`#a855f7` to `#ec4899`).

```css
.voice-orb {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, #00cae0 0%, #0077b6 70%, transparent 100%);
  box-shadow: 0 0 40px rgba(0, 202, 224, 0.4);
  transition: all 0.3s ease;
  animation: pulse-idle 3s infinite ease-in-out;
}
.voice-orb.listening {
  box-shadow: 0 0 60px rgba(0, 202, 224, 0.8);
  animation: pulse-listening 1.2s infinite ease-in-out;
}
.voice-orb.speaking {
  box-shadow: 0 0 60px rgba(168, 85, 247, 0.8);
  background: radial-gradient(circle, #ec4899 0%, #a855f7 70%, transparent 100%);
}
```

## 3. Web Speech API Integration (STT & TTS)
```javascript
// Speech Recognition (STT)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  handleUserUtterance(transcript);
};

// Speech Synthesis (TTS)
function speak(text, callback) {
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;
  utterance.onend = () => { if (callback) callback(); };
  window.speechSynthesis.speak(utterance);
}
```

## 4. Live Inventory & Expiring Badge UI
- Render inventory items in responsive grid cards.
- **Shelf-Life Urgency Badges:**
  - `expires_in <= 48 hours`: **Urgent Amber/Red** pulse badge (`"Expires Tomorrow!"` or `"Use in 24h"`).
  - `expires_in <= 5 days`: **Yellow Warning** badge (`"Expires in 3 days"`).
  - `good`: **Subtle Gray/Green** badge.
- Instant optimistic update on voice command ("I made it" or "I bought milk").

## 5. Direct Streamable HTTP MCP Client
The web companion directly invokes the local FastMCP server or cloudflared tunnel endpoint:
```javascript
async function callMcpTool(toolName, args) {
  const startTime = performance.now();
  const response = await fetch('/mcp/sous-chef', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: { name: toolName, arguments: args }
    })
  });
  const latency = Math.round(performance.now() - startTime);
  document.getElementById('latency-metric').textContent = `${latency} ms`;
  return await response.json();
}
```

## 6. Implementation Checklist
- [ ] Fallback text input alongside microphone button for testing without audio.
- [ ] Round-trip latency widget displaying `< 500ms` compliance.
- [ ] Error toasts gracefully display spoken error envelope messages without code crashes.
- [ ] Verified on Chrome, Edge, and Safari on macOS.
