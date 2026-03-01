/**
 * Fill-in-the-blank quiz — minimal client-side enhancements.
 * The quiz is primarily server-rendered with form POSTs.
 */
document.addEventListener('DOMContentLoaded', function () {
  // Auto-focus the first empty input on the page
  const inputs = document.querySelectorAll('.fill-answer-input');
  for (const inp of inputs) {
    if (!inp.value.trim()) {
      inp.focus();
      break;
    }
  }

  // Allow Enter key to advance to next input instead of submitting form
  inputs.forEach((inp, idx) => {
    inp.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const next = inputs[idx + 1];
        if (next) {
          next.focus();
        }
      }
    });
  });
});
