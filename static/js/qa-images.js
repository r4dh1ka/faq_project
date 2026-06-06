(function () {
  function initImagePreview(inputId, previewId, maxImages) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    input.addEventListener('change', function () {
      preview.innerHTML = '';
      const allFiles = Array.from(input.files);
      if (allFiles.length > (maxImages || 5)) {
        alert('Maximum ' + (maxImages || 5) + ' images allowed.');
      }
      const files = allFiles.slice(0, maxImages || 5);
      files.forEach(function (file, index) {
        if (!file.type.startsWith('image/')) return;
        const col = document.createElement('div');
        col.className = 'col-6 col-md-4 col-lg-3';
        const card = document.createElement('div');
        card.className = 'image-preview-card';
        const img = document.createElement('img');
        img.alt = 'Preview ' + (index + 1);
        const objectUrl = URL.createObjectURL(file);
        img.src = objectUrl;
        img.onload = function() {
            URL.revokeObjectURL(objectUrl);
        };
        const label = document.createElement('small');
        label.className = 'text-muted d-block mt-1 text-truncate';
        label.textContent = file.name;
        card.appendChild(img);
        card.appendChild(label);
        col.appendChild(card);
        preview.appendChild(col);
      });
    });
  }

  function initLightbox() {
    document.querySelectorAll('[data-lightbox]').forEach(function (thumb) {
      thumb.addEventListener('click', function (e) {
        e.preventDefault();
        const src = thumb.getAttribute('href') || thumb.dataset.fullSrc;
        const modal = document.getElementById('imageLightbox');
        const img = document.getElementById('lightbox-image');
        if (modal && img && src) {
          img.src = src;
          bootstrap.Modal.getOrCreateInstance(modal).show();
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initImagePreview('question-images', 'question-image-preview', 5);
    initImagePreview('answer-images', 'answer-image-preview', 5);
    initLightbox();
  });
})();
