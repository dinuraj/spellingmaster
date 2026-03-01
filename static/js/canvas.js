/**
 * canvas.js — Offline handwriting canvas for Spelling Master
 */
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let canvasInit = false;

function getCoords(e, canvas) {
  const rect = canvas.getBoundingClientRect();
  if (e.touches) {
    const t = e.touches[0];
    return { x: t.clientX - rect.left, y: t.clientY - rect.top };
  }
  return { x: e.clientX - rect.left, y: e.clientY - rect.top };
}

function initCanvas() {
  if (canvasInit) return;
  const canvas = document.getElementById('handwriting-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.style.cursor = 'crosshair';
  ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 4; ctx.strokeStyle = '#1a1a2e';

  function start(e) {
    isDrawing = true; const c = getCoords(e, canvas); lastX = c.x; lastY = c.y; ctx.beginPath(); ctx.moveTo(lastX, lastY); if (e.pointerId) canvas.setPointerCapture(e.pointerId); e.preventDefault();
  }
  function draw(e) {
    if (!isDrawing) return; const c = getCoords(e, canvas); ctx.lineTo(c.x, c.y); ctx.stroke(); e.preventDefault();
  }
  function stop(e) { isDrawing = false; if (e && e.pointerId) try { canvas.releasePointerCapture(e.pointerId); } catch (er) {} }

  canvas.addEventListener('mousedown', start);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', stop);
  canvas.addEventListener('mouseleave', stop);
  // Pointer events provide better cross-device support
  canvas.addEventListener('pointerdown', start);
  canvas.addEventListener('pointermove', draw);
  canvas.addEventListener('pointerup', stop);
  canvas.addEventListener('touchstart', start);
  canvas.addEventListener('touchmove', draw);
  canvas.addEventListener('touchend', stop);

  function drawGuide() {
    ctx.save(); ctx.setLineDash([6,6]); ctx.strokeStyle = '#e0e0e0'; const y = canvas.height * 0.75; ctx.beginPath(); ctx.moveTo(10,y); ctx.lineTo(canvas.width-10,y); ctx.stroke(); ctx.restore();
  }
  drawGuide();
  canvasInit = true;
}

function clearCanvas() {
  const canvas = document.getElementById('handwriting-canvas');
  if (!canvas) return; const ctx = canvas.getContext('2d'); ctx.clearRect(0,0,canvas.width,canvas.height); const y = canvas.height * 0.75; ctx.setLineDash([6,6]); ctx.beginPath(); ctx.moveTo(10,y); ctx.lineTo(canvas.width-10,y); ctx.stroke();
}

function toggleCanvas() {
  const cs = document.getElementById('canvas-section');
  const ts = document.getElementById('type-section');
  const btn = document.getElementById('btn-canvas');
  if (!cs || !ts) return;
  if (cs.style.display === 'none') {
    cs.style.display = 'block'; ts.style.display = 'none'; btn.textContent = '⌨️ Type Instead'; initCanvas();
  } else { cs.style.display = 'none'; ts.style.display = 'block'; btn.textContent = '✏️ Write Instead'; }
}

async function submitCanvas() {
  const canvas = document.getElementById('handwriting-canvas');
  if (!canvas) return;
  const feedback = document.getElementById('feedback');
  if (!feedback) return;
  // Send canvas as image to server for OCR recognition
  feedback.style.display = 'block';
  document.getElementById('feedback-icon').textContent = '✍️';
  document.getElementById('feedback-msg').textContent = 'Recognizing handwriting…';
  // hide previous recognized output
  const recOut = document.getElementById('recognized-output'); if (recOut) { recOut.style.display='none'; recOut.textContent=''; }
  const dataUrl = canvas.toDataURL('image/png');
  try {
    const res = await fetch('/quiz/recognize', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({image: dataUrl})});
    const jd = await res.json();
    if (res.ok && jd.recognized) {
      const recognized = jd.recognized;
      const ro = document.getElementById('recognized-output');
      if (ro) { ro.style.display='block'; ro.innerHTML = 'Recognized: <strong id="recognized-word">' + (recognized || '(none)') + '</strong>'; }
      // auto-submit recognized text to check endpoint
      const chk = await fetch('/quiz/check', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({answer: recognized})});
      const chkData = await chk.json();
      // reuse existing feedback renderer if available
      if (window.showFeedback) window.showFeedback(chkData.correct, chkData.correct_word, chkData.next_available);
      else {
        document.getElementById('feedback-icon').textContent = chkData.correct ? '✅' : '❌';
        document.getElementById('feedback-msg').textContent = chkData.correct ? 'Correct' : 'Not quite';
      }
    } else {
      document.getElementById('feedback-msg').textContent = 'Could not recognize handwriting.';
    }
  } catch (e) {
    document.getElementById('feedback-msg').textContent = 'Recognition failed.';
  }
}

async function recordResult(isCorrect) {
  const el = document.getElementById('current-word');
  const word = el ? el.dataset.word : '';
  const answer = isCorrect ? word : '';
  await fetch('/quiz/check', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({answer})});
  location.reload();
}

window.initCanvas = initCanvas;
window.toggleCanvas = toggleCanvas;
window.clearCanvas = clearCanvas;
window.submitCanvas = submitCanvas;
window.recordResult = recordResult;
