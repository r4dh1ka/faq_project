// Dark / light mode (Bootstrap 5.3 color modes)
(function initThemeToggle() {
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  const icon = document.getElementById('theme-toggle-icon');
  const storageKey = 'faq-theme';

  function getTheme() {
    return root.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
  }

  function updateIcon(theme) {
    if (!icon) return;
    icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
  }

  function setTheme(theme, persist) {
    root.setAttribute('data-bs-theme', theme);
    updateIcon(theme);
    if (persist) {
      localStorage.setItem(storageKey, theme);
    }
  }

  updateIcon(getTheme());

  toggle?.addEventListener('click', function () {
    const next = getTheme() === 'dark' ? 'light' : 'dark';
    setTheme(next, true);
  });
})();

// Global search autocomplete
const searchInput = document.getElementById('global-search');
if (searchInput) {
  let timeout;
  searchInput.addEventListener('input', function () {
    clearTimeout(timeout);
    const q = this.value;
    if (q.length < 2) return;
    timeout = setTimeout(() => {
      fetch(`/search/autocomplete/?q=${encodeURIComponent(q)}`)
        .then((r) => r.json())
        .then((data) => {
          console.debug('Suggestions:', data.suggestions);
        });
    }, 300);
  });
}
