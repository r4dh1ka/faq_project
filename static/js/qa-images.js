(function () {
  function initImagePreview(inputId, previewId, maxImages) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    input.addEventListener('change', function () {
      preview.innerHTML = '';
      preview.className = 'image-preview-grid';
      const allFiles = Array.from(input.files);
      if (allFiles.length > (maxImages || 5)) {
        alert('Maximum ' + (maxImages || 5) + ' images allowed.');
      }
      const files = allFiles.slice(0, maxImages || 5);
      files.forEach(function (file, index) {
        if (!file.type.startsWith('image/')) return;
        const card = document.createElement('div');
        card.className = 'image-preview-card';
        const img = document.createElement('img');
        img.alt = 'Preview ' + (index + 1);
        const objectUrl = URL.createObjectURL(file);
        img.src = objectUrl;
        img.onload = function () { URL.revokeObjectURL(objectUrl); };
        const label = document.createElement('small');
        label.textContent = file.name;
        card.appendChild(img);
        card.appendChild(label);
        preview.appendChild(card);
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initImagePreview('question-images', 'question-image-preview', 5);
    initImagePreview('answer-images', 'answer-image-preview', 5);
  });
})();
