(function initAppShell() {
  const sidebar = document.getElementById('app-sidebar');
  const toggle = document.getElementById('sidebar-toggle');
  const backdrop = document.getElementById('mobile-sidebar-backdrop');
  const profileToggle = document.getElementById('profile-menu-toggle');
  const profileMenu = document.getElementById('profile-menu');

  function openSidebar() {
    sidebar?.classList.add('is-open');
    backdrop?.classList.remove('hidden');
  }

  function closeSidebar() {
    sidebar?.classList.remove('is-open');
    backdrop?.classList.add('hidden');
  }

  toggle?.addEventListener('click', openSidebar);
  backdrop?.addEventListener('click', closeSidebar);

  profileToggle?.addEventListener('click', function (event) {
    event.stopPropagation();
    profileMenu?.classList.toggle('hidden');
  });

  document.addEventListener('click', function () {
    profileMenu?.classList.add('hidden');
  });

  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item[href]').forEach((item) => {
    const url = new URL(item.href);
    if (url.pathname === currentPath || (url.pathname !== '/' && currentPath.startsWith(url.pathname))) {
      item.setAttribute('aria-current', 'page');
    }
  });
})();

(function initLightbox() {
  const overlay = document.createElement('div');
  overlay.id = 'lightbox-overlay';
  overlay.className = 'lightbox-overlay hidden';
  overlay.innerHTML = `
    <button class="lightbox-close" id="lightbox-close" aria-label="Close"><i class="bi bi-x-lg"></i></button>
    <img id="lightbox-image" src="" alt="Full size image">
  `;
  document.body.appendChild(overlay);

  window.openLightbox = function (src) {
    const img = document.getElementById('lightbox-image');
    if (img) img.src = src;
    overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  };

  function closeLightbox() {
    overlay.classList.add('hidden');
    document.body.style.overflow = '';
  }

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay || e.target.id === 'lightbox-close' || e.target.closest('#lightbox-close')) {
      closeLightbox();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLightbox();
  });

  document.addEventListener('click', function (e) {
    const link = e.target.closest('[data-lightbox]');
    if (!link) return;
    e.preventDefault();
    const src = link.getAttribute('href') || link.dataset.fullSrc;
    if (src) window.openLightbox(src);
  });
})();

(function initSearchAutocomplete() {
  const searchInput = document.getElementById('global-search');
  if (!searchInput) return;

  let timeout;
  searchInput.addEventListener('input', function () {
    clearTimeout(timeout);
    const q = this.value.trim();
    if (q.length < 2) return;
    timeout = setTimeout(() => {
      fetch(`/search/autocomplete/?q=${encodeURIComponent(q)}`)
        .then((r) => r.json())
        .then((data) => {
          searchInput.dataset.suggestions = (data.suggestions || []).join('|');
        })
        .catch(() => {});
    }, 250);
  });
})();

(function initInlineReplyToggles() {
  document.addEventListener('click', function (event) {
    const trigger = event.target.closest('[data-reply-toggle]');
    if (!trigger) return;
    const target = document.getElementById(trigger.dataset.replyToggle);
    target?.classList.toggle('hidden');
  });
})();
