/**
 * quiz.js — coordinator between UI, speech, and quiz API
 */

async function submitAnswer() {
  const input = document.getElementById('answer-input');
  const answer = input.value.trim();
  if (!answer) { input.classList.add('animate-shake'); setTimeout(()=>input.classList.remove('animate-shake'),400); return; }
  const res = await fetch('/quiz/check', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({answer})});
  const data = await res.json();
  showFeedback(data.correct, data.correct_word, data.next_available);
}

function showFeedback(isCorrect, correctWord, hasNext) {
  const feedback = document.getElementById('feedback');
  const icon = document.getElementById('feedback-icon');
  const msg = document.getElementById('feedback-msg');
  const reveal = document.getElementById('correct-word-reveal');
  // keep any recognized-output visible (canvas submit populates it)
  const ansInput = document.getElementById('answer-input');
  if (ansInput) ansInput.disabled = true;
  if (isCorrect) {
    icon.textContent = '✅'; msg.textContent = 'Correct! 🎉'; speakFeedback(true);
  } else {
    icon.textContent = '❌'; msg.textContent = 'Not quite!'; reveal.style.display='block'; reveal.textContent = 'Correct: ' + correctWord; speakFeedback(false, correctWord);
  }
  feedback.style.display = 'block'; feedback.classList.add(isCorrect ? 'animate-bounce' : 'animate-shake');
  const nextBtn = document.getElementById('btn-next');
  if (!hasNext) {
    nextBtn.textContent = 'See My Results 🏆';
    nextBtn.dataset.hasNext = 'false';
  } else {
    nextBtn.dataset.hasNext = 'true';
  }
}

function nextWord() {
  const nextBtn = document.getElementById('btn-next');
  if (nextBtn && nextBtn.dataset && nextBtn.dataset.hasNext === 'false') {
    window.location.href = '/quiz/results';
  } else {
    window.location.reload();
  }
}
function goToResults() { window.location.href = '/quiz/results'; }

document.addEventListener('DOMContentLoaded', ()=>{
  if (window.initSpeech) initSpeech();
  if (window.initCanvas) initCanvas();
  setTimeout(()=>{ if (window.speakWord) speakWord(); }, 1000);
  const input = document.getElementById('answer-input');
  if (input) input.addEventListener('keypress', e => { if (e.key === 'Enter') submitAnswer(); });
});
