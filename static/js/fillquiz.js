document.addEventListener('DOMContentLoaded', function () {
  const startBtn = document.getElementById('start-btn');
  const container = document.getElementById('quiz-container');
  const pager = document.getElementById('pager');
  let attemptId = null;
  let total = 0;
  let pages = 0;
  let currentPage = 1;
  let answers = {}; // qid -> answer

  startBtn?.addEventListener('click', async () => {
    startBtn.disabled = true;
    const resp = await fetch('/fillquiz/start?size=30');
    const data = await resp.json();
    attemptId = data.attempt_id;
    total = data.total;
    pages = data.pages;
    currentPage = 1;
    renderPage();
  });

  async function renderPage() {
    const resp = await fetch(`/fillquiz/play?attempt_id=${attemptId}&page=${currentPage}`);
    const data = await resp.json();
    const qs = data.questions || [];
    container.innerHTML = '';
    const form = document.createElement('form');
    qs.forEach((q, i) => {
      const div = document.createElement('div');
      div.className = 'fq';
      const p = document.createElement('p');
      p.textContent = `${(currentPage-1)*5 + i + 1}. ${q.question}`;
      const input = document.createElement('input');
      input.type = 'text';
      input.name = String(q.id);
      input.value = answers[String(q.id)] || '';
      div.appendChild(p);
      div.appendChild(input);
      form.appendChild(div);
    });
    const nextBtn = document.createElement('button');
    nextBtn.type = 'button';
    nextBtn.textContent = currentPage < pages ? 'Next' : 'Finish';
    nextBtn.addEventListener('click', async () => {
      // save answers from inputs
      new FormData(form).forEach((v,k)=> answers[k]=v);
      if (currentPage < pages) {
        currentPage += 1;
        renderPage();
      } else {
        // submit full quiz
        const payload = { attempt_id: attemptId, answers: answers };
        const r = await fetch('/fillquiz/finish', {
          method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
        });
        const res = await r.json();
        // navigate to results page
        window.location = `/fillquiz/results?attempt_id=${res.attempt_id}`;
      }
    });
    form.appendChild(nextBtn);
    container.appendChild(form);

    // pager
    pager.innerHTML = `Page ${currentPage} of ${pages}`;
  }
});
