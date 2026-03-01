/**
 * speech.js — Web Speech API wrapper for Spelling Master
 */

let voices = [];

/**
 * Read persisted voice selection from localStorage (voice name)
 */
function getStoredVoiceName() {
  try { return localStorage.getItem('spellingmaster_voice') || null; } catch (e) { return null; }
}

function setStoredVoiceName(name) {
  try { localStorage.setItem('spellingmaster_voice', name); } catch (e) { }
}

function populateVoiceListUI() {
  const sel = document.getElementById('voice-select');
  if (!sel) return;
  // Clear
  sel.innerHTML = '';
  const avail = voices.length ? voices : (speechSynthesis.getVoices() || []);
  avail.forEach(v => {
    const opt = document.createElement('option');
    opt.value = v.name;
    opt.textContent = `${v.name} — ${v.lang}`;
    sel.appendChild(opt);
  });
  // select stored or preferred
  const stored = getStoredVoiceName();
  if (stored) sel.value = stored;
  else {
    const preferred = chooseVoice();
    if (preferred) sel.value = preferred.name;
  }
  sel.addEventListener('change', () => {
    setStoredVoiceName(sel.value);
  });
}

function initSpeech() {
  if (!('speechSynthesis' in window)) {
    const banner = document.createElement('div');
    banner.textContent = "⚠️ Your browser doesn't support text-to-speech. Please use Chrome or Edge.";
    banner.style.background = '#fff3cd';
    banner.style.padding = '12px';
    document.body.prepend(banner);
    return;
  }
  voices = speechSynthesis.getVoices() || [];
  if (!voices.length) {
    speechSynthesis.onvoiceschanged = () => { voices = speechSynthesis.getVoices(); populateVoiceListUI(); };
  }
  populateVoiceListUI();
}

/**
 * Prefer `en-IN` voices, then `en-GB`, then `en-US`, then any `en`, then fallback.
 * If user has explicitly selected a voice, prefer that by name.
 */
function chooseVoice(preferredLangs = ['en-IN','en-GB','en-US']) {
  const avail = voices.length ? voices : (speechSynthesis.getVoices() || []);
  const stored = getStoredVoiceName();
  if (stored) {
    const sv = avail.find(x => x.name === stored);
    if (sv) return sv;
  }
  for (const lang of preferredLangs) {
    const v = avail.find(x => x.lang && x.lang.toLowerCase().startsWith(lang.toLowerCase()));
    if (v) return v;
  }
  const anyEn = avail.find(x => x.lang && x.lang.toLowerCase().startsWith('en'));
  return anyEn || avail[0] || null;
}

function speakText(text, opts = {}) {
  if (!('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  const v = chooseVoice();
  if (v) u.voice = v;
  u.rate = opts.rate ?? 0.9;
  u.pitch = opts.pitch ?? 1.0;
  u.volume = opts.volume ?? 1;
  speechSynthesis.speak(u);
}

function speakWord() {
  const el = document.getElementById('current-word');
  if (!el) return;
  const word = el.dataset.word || '';
  if (!word) return;
  speechSynthesis.cancel();
  speakText(word);
  setTimeout(() => speakText(word), 1500);
  const btn = document.getElementById('btn-speak');
  const btnr = document.getElementById('btn-repeat');
  if (btn) btn.style.display = 'none';
  if (btnr) btnr.style.display = 'inline-block';
}

function speakFeedback(isCorrect, word) {
  if (isCorrect) speakText('Correct! Well done!');
  else {
    speakText('Not quite. The correct spelling is ' + word);
    setTimeout(() => spellOutWord(word), 900);
  }
}

function spellOutWord(word) {
  const letters = word.split('');
  let i = 0;
  function next() {
    if (i >= letters.length) return;
    speakText(letters[i]);
    i += 1;
    setTimeout(next, 450);
  }
  next();
}

function speakSingleWord(word) {
  speakText(word);
}

window.initSpeech = initSpeech;
window.speakWord = speakWord;
window.speakFeedback = speakFeedback;
window.speakSingleWord = speakSingleWord;
