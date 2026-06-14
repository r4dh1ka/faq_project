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

  function appendMsg(text, role, sources, isHtml = false) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    if (isHtml) { div.innerHTML = text; } else { div.textContent = text; }
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
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden') && !messages.childElementCount) {
      appendMsg('Hi! I am Yaksha. Ask me anything about our FAQ knowledge base.', 'bot');
    }
  });

  closeBtn?.addEventListener('click', () => panel.classList.add('hidden'));

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendMsg(text, 'user');
    input.value = '';
    appendMsg('<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>', 'bot', [], true);
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
      if (data.suggested?.length && suggestionsEl) {
        suggestionsEl.innerHTML = '';
        data.suggested.forEach((s) => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'suggest-btn';
          btn.textContent = s;
          btn.addEventListener('click', () => {
            input.value = s;
            form.requestSubmit();
          });
          suggestionsEl.appendChild(btn);
        });
      }
    } catch (err) {
      thinking.remove();
      appendMsg('Sorry, something went wrong. Please try again.', 'bot');
    }
  });
})();
