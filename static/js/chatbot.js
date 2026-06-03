(function () {
  const toggle = document.getElementById('chatbot-toggle');
  const panel = document.getElementById('chatbot-panel');
  const closeBtn = document.getElementById('chatbot-close');
  const form = document.getElementById('chatbot-form');
  const input = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');
  const suggestionsEl = document.getElementById('chatbot-suggestions');

  if (!toggle) return;

  function getCsrf() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }

  function appendMsg(text, role, sources) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    div.textContent = text;
    if (sources && sources.length) {
      const src = document.createElement('div');
      src.className = 'chat-sources';
      src.innerHTML = 'Sources: ' + sources.map((s) => `<a href="${s.url}">${s.title}</a>`).join(', ');
      div.appendChild(src);
    }
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  toggle.addEventListener('click', () => {
    panel.classList.toggle('d-none');
    if (!panel.classList.contains('d-none') && !messages.childElementCount) {
      appendMsg('Hi! I am Yaksha. Ask me anything about our FAQ knowledge base.', 'bot');
    }
  });
  closeBtn?.addEventListener('click', () => panel.classList.add('d-none'));

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendMsg(text, 'user');
    input.value = '';
    appendMsg('Thinking...', 'bot');
    const thinking = messages.lastChild;
    try {
      const res = await fetch('/assistant/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf(),
        },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      thinking.remove();
      appendMsg(data.reply || 'No response.', 'bot', data.sources);
      if (data.suggested?.length) {
        suggestionsEl.innerHTML =
          'Try: ' +
          data.suggested.map((s) => `<button type="button" class="btn btn-link btn-sm p-0 suggest-btn">${s}</button>`).join(' · ');
        suggestionsEl.querySelectorAll('.suggest-btn').forEach((btn) => {
          btn.addEventListener('click', () => {
            input.value = btn.textContent;
            form.requestSubmit();
          });
        });
      }
    } catch (err) {
      thinking.remove();
      appendMsg('Sorry, something went wrong. Please try again.', 'bot');
    }
  });
})();
